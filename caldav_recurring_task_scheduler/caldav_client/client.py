import logging
from config import UserConfig
from caldav_client.task import TaskWrapper
from caldav import Calendar, DAVClient
from caldav.elements import dav, cdav
from caldav.objects import Todo
from datetime import datetime

logger = logging.getLogger(__name__)


class CalDavClient():

    def __init__(self, u: UserConfig):
        self.client = DAVClient(
            url=u.url,
            username=u.name, password=u.password,
            ssl_verify_cert=u.ssl_verify_cert,
            ssl_cert=u.ssl_cert)

    def list_calendars(self) -> list[Calendar]:
        principal = self.client.principal()
        return principal.calendars()

    def list_tasks(self, c: Calendar, start: datetime = None, end: datetime = None, category: str = None, parent_uuid: str = None):
        logger.debug('Search for category="%s" tasks between %s and %s, under parent "%s"',
                     category, start, end, parent_uuid)

        # Fetch all calendar data
        prop = dav.Prop() + cdav.CalendarData()

        query = cdav.CompFilter("VTODO")
        vcalendar = cdav.CompFilter("VCALENDAR") + query
        filter = cdav.Filter() + vcalendar
        root = cdav.CalendarQuery() + [prop, filter]

        # Add filter on dtstart
        if start and end:
            dts_filter = cdav.PropFilter(
                'DTSTART') + cdav.TimeRange(start, end)
            query += dts_filter

        if category:
            # Add filter on category
            query += cdav.PropFilter('CATEGORIES') + cdav.TextMatch(category)

        if parent_uuid:
            # Add filter on parent
            query += cdav.PropFilter('RELATED-TO') + \
                cdav.TextMatch(parent_uuid)

        logger.debug('Search query : %s', root)
        res = c.search(root, comp_class=Todo)
        tasks = [TaskWrapper(t) for t in res]

        tasks = []
        for r in res:
            t = TaskWrapper(r)

            # The TextMatch filter we use is basically a "contains"
            # So if we search for 'weekly', we can get task from 'foo-weekly-bar'
            tcat = t.get_instance_attribute('categories', [])
            if category and not category in tcat:
                logger.debug('Ignoring task : "%s", "%s" not in %s',
                             t, category, tcat)
                continue

            tasks.append(t)

        logger.debug('%d tasks found', len(tasks))
        return tasks
