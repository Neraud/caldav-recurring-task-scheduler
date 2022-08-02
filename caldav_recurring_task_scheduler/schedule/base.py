
from abc import abstractmethod
from datetime import date, datetime, timedelta


class Schedule():

    category: str = None

    def __init__(self, category: str):
        self.category = category

    @abstractmethod
    def is_applicable(self, run_date: date) -> bool:
        pass

    @abstractmethod
    def get_previous_date(self, run_date: date) -> date:
        pass

    def get_delta_for_reschedule(self, run_date: date) -> timedelta:
        return run_date - self.get_previous_date(run_date)
