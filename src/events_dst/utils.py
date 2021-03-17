""" Utility functions. """
from datetime import datetime
import os

import pytz

LOCAL_TZ = pytz.timezone(os.environ.get('TZ', 'UTC'))

def local_now(local_tz=LOCAL_TZ):
    """
    Returns a dt object for now, with the local timezone.

    Args:
        local_tz (timezone): timezone for the local time.

    Returns:
        datetime: now in the local timezone.
    """
    return datetime.now(pytz.utc).astimezone(local_tz)
