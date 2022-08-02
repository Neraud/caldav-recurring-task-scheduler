from schedule.base import Schedule
from datetime import date, datetime
from dateutil import relativedelta


class MonthdaySchedule(Schedule):

    WEEKDAYS = {
        'MO': relativedelta.MO,
        'TU': relativedelta.TU,
        'WE': relativedelta.WE,
        'TH': relativedelta.TH,
        'FR': relativedelta.FR,
        'SA': relativedelta.SA,
        'SU': relativedelta.SU,
    }
    day: str = None
    n: int = None

    def __init__(self, category: str, day: str, n: int):
        super().__init__(category)
        self.day = day
        self.n = n

    def is_applicable(self, run_date: date) -> bool:
        # We want to make sure we only trigger the schedule when we are currently on the proper weekday
        # If n is > 0, reset to the 1st of current month before looking for the next weekday
        # If n is < 0, reset to the the end of next month before looking for last weekday
        if self.n and self.n < 0:
            args = {'day': 31}
        else:
            args = {'day': 1}

        if self.n:
            args['weekday'] = self.WEEKDAYS[self.day](self.n)
        else:
            args['weekday'] = self.WEEKDAYS[self.day]

        return run_date == run_date - relativedelta.relativedelta(**args)

    def get_previous_date(self, run_date: date) -> date:
        # If n is > 0, reset to the 1st of next month before looking for the next weekday
        # If n is < 0, reset to the the end of next month before looking for last weekday
        if self.n < 0:
            args = {'day': 31, 'months': 1}
        else:
            args = {'day': 1, 'months': 1}

        args['weekday'] = self.WEEKDAYS[self.day](self.n)
        delta = relativedelta.relativedelta(**args)
        return run_date - delta

    def __repr__(self) -> str:
        return f'Schedule "{self.category}" ({self.day} {self.n})'
