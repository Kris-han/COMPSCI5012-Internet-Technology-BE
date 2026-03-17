import calendar
from datetime import datetime
from django.utils import timezone

def get_month_ts():

    now = timezone.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    last_day = calendar.monthrange(now.year, now.month)[1]
    end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())
    return start_ts, end_ts


def get_current_time_ts():
    timestamp = int(datetime.now().timestamp())
    return timestamp
