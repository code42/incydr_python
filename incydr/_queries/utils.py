from datetime import datetime

MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_STR_FORMAT = "%Y-%m-%d"


def parse_timestamp(timestamp):
    """Parse timestamp to milliseconds precision.

    Args:
        timestamp (str or int or float or datetime): A POSIX timestamp.

    Returns:
        (str): A str representing the given timestamp. Example output looks like
        '2020-03-25T15:29:04.465Z'.
    """
    # convert str/int/float values to datetime
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, DATETIME_STR_FORMAT)
        except ValueError:
            timestamp = datetime.strptime(timestamp, DATE_STR_FORMAT)
    # parse datetime to string
    return f"{timestamp.strftime(MICROSECOND_FORMAT)[:-4]}Z"