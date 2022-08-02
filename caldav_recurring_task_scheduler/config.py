import yaml
import logging
from typing import Dict
from schedule.base import Schedule
from schedule.regular import RegularSchedule
from schedule.monthday import MonthdaySchedule

logger = logging.getLogger(__name__)


class UserConfig:

    name: None
    password: None
    url: None
    ssl_verify_cert = True
    ssl_cert = None
    clone_children = True
    detach_from_parent = False
    clone_summary_suffix = ""

    schedules: list[Schedule] = []

    def __init__(self, name: str, password: str):
        self.name = name
        self.password = password


class ConfigManager:

    def __init__(self, path: str):
        self.path = path
        self._load()

    def _load(self):
        logger.info('Parsing config %s', self.path)
        self.user_conf = {}
        with open(self.path) as file:
            conf = yaml.full_load(file)['config']
            for user in conf.get('users', []):
                logger.debug('- user %s', user['name'])
                u = UserConfig(user['name'], user['password'])
                u.url = self._get_user_conf(user, conf, 'url')
                u.ssl_verify_cert = self._get_user_conf(
                    user, conf, 'ssl_verify_cert', True)
                u.ssl_cert = self._get_user_conf(
                    user, conf, 'ssl_cert')
                u.clone_children = self._get_user_conf(
                    user, conf, 'clone_children', True)
                u.detach_from_parent = self._get_user_conf(
                    user, conf, 'detach_from_parent', False)
                u.clone_summary_suffix = self._get_user_conf(
                    user, conf, 'clone_summary_suffix', "")

                schedules = []
                for s in self._get_user_conf(user, conf, 'schedules'):
                    sch = self._create_schedule(s)
                    schedules.append(sch)
                u.schedules = schedules

                self.user_conf[u.name] = u

    def _create_schedule(self, s: Dict) -> Schedule:
        logger.debug('* schedule %s', s['category'])
        if s['type'] == 'regular':
            return RegularSchedule(s['category'],
                                   s['unit'],
                                   int(s['value']))
        elif s['type'] == 'monthday':
            return MonthdaySchedule(s['category'],
                                    s['day'],
                                    int(s['n']))
        else:
            raise ValueError(f'Unknown schedule type "{s["type"]}"')

    def _get_user_conf(self, user: dict, conf: dict, name: str, default=None):
        return user.get(name, conf.get('default', {}).get(name, default))

    def _get_user_tag(self, user: dict, conf: dict, tag: str):
        return user.get('tags', {}).get(tag, conf.get('default', {}).get('tags', {}).get(tag, None))

    def get_user_names(self) -> list[str]:
        return self.user_conf.keys()

    def get_user_config(self, name: str) -> UserConfig:
        return self.user_conf.get(name, None)
