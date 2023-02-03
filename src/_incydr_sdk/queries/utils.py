from datetime import date
from datetime import datetime
from datetime import timezone
from typing import Union

from dateutil import parser

from _incydr_sdk.exceptions import DateParseError

MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_STR_FORMAT = "%Y-%m-%d"


def parse_ts_to_ms_str(timestamp: Union[str, int, float, datetime, date]):
    """
    Parse int/float/str/datetime timestamp to string milliseconds precision.

    Args:
        timestamp (str or int or float or datetime): A POSIX timestamp.

    **Returns**:
        (str): A str representing the given timestamp. Example output looks like
        '2020-03-25T15:29:04.465Z'.
    """
    # convert str/int/float values to datetime
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        timestamp = parse_str_to_dt(timestamp)
    timestamp.replace(tzinfo=timezone.utc)
    # parse datetime to string
    return f"{timestamp.strftime(MICROSECOND_FORMAT)[:-4]}Z"


def parse_ts_to_posix_ts(timestamp: Union[str, datetime]):
    """
    Parse POSIX timestamp from DATE/DATETIME str or datetime obj.
    """
    dt = timestamp if isinstance(timestamp, datetime) else parse_str_to_dt(timestamp)
    return dt.timestamp()


def parse_str_to_dt(timestamp: str):
    try:
        dt = parser.parse(timestamp)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise DateParseError(
            timestamp,
            f"DateParseError: Time data '{timestamp}' does not match any known formats.  Ex: {DATETIME_STR_FORMAT}",
        )
