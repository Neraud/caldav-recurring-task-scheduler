from __future__ import annotations
import logging
from typing import Any
from caldav import Event
from datetime import timedelta

logger = logging.getLogger(__name__)


class TaskWrapper():

    def __init__(self, event: Event):
        self.event = event

    def get_summary(self):
        return self.event.instance.vtodo.summary.value

    def get_instance_attribute(self, name: str, default: Any = None) -> Any:
        if hasattr(self.event.instance.vtodo, name):
            return getattr(self.event.instance.vtodo, name).value
        else:
            return default

    def _delete_instance_attribute(self, name: str):
        if hasattr(self.event.instance.vtodo, name):
            logger.debug(' - delete "%s" attribute', name)
            delattr(self.event.instance.vtodo, name)

    def _set_instance_attribute(self, name: str, v: any):
        logger.debug(' - setting "%s" attribute to %s', name, v)
        getattr(self.event.instance.vtodo, name).value = v

    def _increase_instance_date_attribute(self, name: str, d: timedelta):
        if hasattr(self.event.instance.vtodo, name):
            logger.debug(' - increasing "%s" attribute by %s', name, d)
            getattr(self.event.instance.vtodo, name).value += d

    def __repr__(self) -> str:
        return f"Task '{self.get_instance_attribute('summary')}'"
