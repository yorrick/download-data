# -*- coding: utf-8 -*-
from __future__ import print_function
from pytz import timezone

MONTREAL_TIMEZONE = timezone("America/Montreal")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def to_local_time(dt, tz):
    if tz is None or tz == 'None':
        return dt
    else:
        local_tz = timezone(tz)
        return local_tz.normalize(dt.astimezone(local_tz))


def get_log_time(dt):
    return MONTREAL_TIMEZONE.localize(dt, is_dst=False)
