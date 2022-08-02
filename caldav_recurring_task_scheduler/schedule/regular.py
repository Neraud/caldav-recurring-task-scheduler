from schedule.base import Schedule
from datetime import date, datetime
from dateutil import relativedelta


class RegularSchedule(Schedule):

    unit: str = None
    value: int = None

    def __init__(self, category: str, unit: str, value: int):
        super().__init__(category)
        self.unit = unit
        self.value = value

    def is_applicable(self, run_date: date) -> bool:
        return True

    def get_previous_date(self, run_date: date) -> date:
        args = {self.unit: self.value}
        delta = relativedelta.relativedelta(**args)
        return run_date - delta

    def __repr__(self) -> str:
        return f'Schedule "{self.category}" ({self.value} {self.unit})'
