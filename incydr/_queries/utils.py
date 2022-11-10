from datetime import date
from datetime import datetime
from datetime import timezone
from typing import Union

MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_STR_FORMAT = "%Y-%m-%d"


def parse_timestamp_to_millisecond_str(
    timestamp: Union[str, int, float, datetime, date]
):
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
        timestamp = parse_str_to_datetime(timestamp)
    timestamp.replace(tzinfo=timezone.utc)
    # parse datetime to string
    return f"{timestamp.strftime(MICROSECOND_FORMAT)[:-4]}Z"


def parse_timestamp_to_posix_timestamp(timestamp: Union[str, datetime]):
    """
    Parse POSIX timestamp from str in DATE or DATETIME format or datetime obj.
    """
    date_time = (
        timestamp
        if isinstance(timestamp, datetime)
        else parse_str_to_datetime(timestamp)
    )
    date_time.replace(tzinfo=timezone.utc)
    return date_time.timestamp()


def parse_str_to_datetime(timestamp: str):
    try:
        return datetime.strptime(timestamp, DATETIME_STR_FORMAT).replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        try:
            return datetime.strptime(timestamp, DATE_STR_FORMAT).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            raise ValueError(
                f"time data '{timestamp}' does not match format {DATETIME_STR_FORMAT} or {DATE_STR_FORMAT}"
            )
