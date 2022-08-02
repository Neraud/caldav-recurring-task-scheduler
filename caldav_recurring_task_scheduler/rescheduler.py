import logging

from datetime import date, datetime
from config import ConfigManager, UserConfig
from caldav import Calendar
from caldav_client.client import CalDavClient
from caldav_client.task import TaskWrapper
from schedule.base import Schedule

logger = logging.getLogger(__name__)


class Rescheduler:

    def __init__(self, config: ConfigManager, run_date: date, dry_run: bool = False):
        self.config = config
        self.run_date = run_date
        self.dry_run = dry_run

    def run_for_all(self):
        logger.info('Running for all users')
        for n in self.config.get_user_names():
            self.run_for_user(n)

    def run_for_user(self, name: str):
        logger.info("Running for user : %s", name)
        r = UserRescheduler(self.config, self.run_date, name, self.dry_run)
        r.run()


class UserRescheduler:

    def __init__(self, config: ConfigManager, run_date: date, name: str, dry_run: bool = False):
        self.config = config
        self.run_date = run_date
        self.name = name
        self.user_config = self.config.get_user_config(name)
        self.client = CalDavClient(self.user_config)
        self.dry_run = dry_run

    def run(self):
        applicable_schedules = []
        logger.debug('Looking for applicable schedules for %s', self.run_date)
        for s in self.user_config.schedules:
            if s.is_applicable(self.run_date):
                logger.debug('- %s : applicable', s.category)
                applicable_schedules.append(s)
            else:
                logger.debug('- %s : not applicable, ignored', s.category)

        if applicable_schedules:
            logger.debug('Applicable schedules : %s', applicable_schedules)
            calendars = self.client.list_calendars()
            logger.debug('Found %d calendars', len(calendars))
            for s in applicable_schedules:
                for c in calendars:
                    self._handle_schedule(s, c)
        else:
            logger.info('No applicable schedules for user %s', self.name)

    def _handle_schedule(self, s: Schedule, c: Calendar):
        logger.info('Handling schedule "%s" for calendar "%s"', s, c.name)
        pd = s.get_previous_date(self.run_date)
        start = datetime.combine(pd, datetime.min.time())
        end = datetime.combine(pd, datetime.max.time())

        tasks = self.client.list_tasks(c, start, end, category=s.category)

        for t in tasks:
            logger.info('- cloning task "%s"', t.get_summary())
            clone = self._clone_task(s, t)
            if self.user_config.clone_children:
                self._clone_children_recursively(s, c, t, clone)

    def _clone_children_recursively(self, s: Schedule, c: Calendar, old_parent: TaskWrapper, new_parent: TaskWrapper):
        parent_uuid = old_parent.get_instance_attribute('uid')
        logger.debug('Looking for subtasks under %s (%s)',
                     old_parent.get_summary(), parent_uuid)

        subtasks = self.client.list_tasks(c, parent_uuid=parent_uuid)
        for t in subtasks:
            logger.info('- cloning task "%s" (under %s)',
                        t.get_summary(), new_parent.get_summary())
            clone = self._clone_task(s, t, new_parent)
            self._clone_children_recursively(s, c, t, clone)

    def _clone_task(self, s: Schedule, t: TaskWrapper, new_parent: TaskWrapper = None) -> TaskWrapper:
        logger.debug('Task to clone : %s', t.event.instance)
        clone = TaskWrapper(t.event.copy())

        # Delete UID & DTSTAMP and let new ones be set automatically
        clone._delete_instance_attribute('uid')
        clone._delete_instance_attribute('dtstamp')

        # Reset completed, status and percent-complete attributes
        clone._delete_instance_attribute('completed')
        clone._delete_instance_attribute('status')
        clone._delete_instance_attribute('percent_complete')

        # Set CREATED and LAST-MODIFIED to now
        now = datetime.now()
        clone._set_instance_attribute('created', now)
        clone._set_instance_attribute('last-modified', now)

        # Update DTSTART and DUE
        delta = s.get_delta_for_reschedule(self.run_date)
        clone._increase_instance_date_attribute('dtstart', delta)
        clone._increase_instance_date_attribute('due', delta)

        # Add SUMMARY suffix
        if self.user_config.clone_summary_suffix:
            clone.event.instance.vtodo.summary.value += self.user_config.clone_summary_suffix

        if new_parent:
            # Attach to new parent
            clone._set_instance_attribute(
                'related_to', new_parent.get_instance_attribute('uid'))
        elif self.user_config.detach_from_parent:
            # Detach from parent
            clone._delete_instance_attribute('related_to')

        if not self.dry_run:
            # Calling save() once generates a new uid, but on the server side the task has a new uid ...
            clone.event.save()
            # Calling save() a second time properly saves the uid
            clone.event.save()
            logger.debug('Task cloned : %s', clone.event.instance)
        else:
            logger.debug('(DRY RUN) Task cloned but not saved : %s',
                         clone.event.instance)

        return clone
