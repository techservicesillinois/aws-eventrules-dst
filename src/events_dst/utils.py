""" Utility functions. """
from datetime import datetime
import os

import pytz

LOCAL_TZ = pytz.timezone(os.environ.get('TZ', 'UTC'))


def events_scheduled_rules(_evt_clnt, **kwargs):
    """
    Generator for the EventBridge scheduled rules. This yields each rule that
    has a ScheduleExpression.

    Args:
        kwargs (dict): args to pass to the list_rules API.

    Yields:
        obj: EventBridge Rule.
    """
    paginator = _evt_clnt.get_paginator('list_rules')
    pages = paginator.paginate(**kwargs).search('Rules[?ScheduleExpression]')
    yield from pages

def local_now(local_tz=LOCAL_TZ):
    """
    Returns a dt object for now, with the local timezone.

    Args:
        local_tz (timezone): timezone for the local time.

    Returns:
        datetime: now in the local timezone.
    """
    return datetime.now(pytz.utc).astimezone(local_tz)
