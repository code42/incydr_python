from datetime import datetime
from numbers import Number

MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_STR_FORMAT = "%Y-%m-%d %H:%M:%S"


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
        timestamp = datetime.strptime(timestamp, DATE_STR_FORMAT)
    # parse datetime to string
    return f"{timestamp.strftime(MICROSECOND_FORMAT)[:-4]}Z"


def validate_numerical_value(value):
    """validate a value is a number or can be converted to a number."""

    def raise_type_error():
        raise TypeError("Value must be a number.")

    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            raise_type_error()
    elif not isinstance(value, Number):
        raise_type_error()
    return value
