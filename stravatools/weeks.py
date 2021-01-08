import datetime
import sys
from typing import Tuple


def get_epoch_range(week: int, year: int) -> Tuple[int, int]:
    start_monday = datetime.datetime.strptime(f"{year}-{week}-1", "%G-%V-%w")
    start_epoch = int(start_monday.timestamp())
    end_epoch = start_epoch + 7 * 24 * 3600
    return start_epoch, end_epoch


def weeks_for_year(year: int) -> int:
    last_week = datetime.date(year, 12, 28)
    return last_week.isocalendar()[1]


def get_week_year(week: int, year: int) -> Tuple[int, int]:
    last_week = datetime.datetime.now() - datetime.timedelta(weeks=1)
    yw = last_week.isocalendar()
    year = year or yw[0]
    week = week or yw[1]
    if weeks_for_year(year) < week:
        sys.exit(f"{year} does not have a week {week}")
    return week, year
