class IncydrException(Exception):
    """Base class for all Incydr specific exceptions."""

    ...


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
