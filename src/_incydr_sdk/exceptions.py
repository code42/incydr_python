class IncydrException(Exception):
    """Base class for all Incydr specific exceptions."""

    ...


class AuthMissingError(IncydrException):
    def __init__(self, error_keys):
        self.error_keys = error_keys

    def __str__(self):
        errors_formatted = "\n - ".join(self.error_keys)
        return (
            f"Missing required authentication variables in environment or in initialization\n\n - {errors_formatted}\n\n"
            "Pass required args to the `incydr.Client` or set required values in your environment.\n\n"
            "See https://developer.code42.com/sdk/settings for more details."
        )


class WatchlistNotFoundError(IncydrException):
    """Raised when a watchlist with the matching type or title is not found."""

    def __init__(self, name):
        self.name = name
        self.message = f"Watchlist Not Found Error: No watchlist matching the type or title '{name}' was found."
        super().__init__(self.message)


class DateParseError(IncydrException):
    """An error raised when the date data cannot be parsed."""

    def __init__(self, date, msg=None):
        self._date = date
        message = msg or f"DateParseError: Error parsing time data: '{date}'."
        super().__init__(message)

    @property
    def date(self):
        return self._date
