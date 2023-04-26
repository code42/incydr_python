from pydantic import ValidationError


class IncydrException(Exception):
    """Base class for all Incydr specific exceptions."""

    ...


class AuthMissingError(ValidationError, IncydrException):
    def __init__(self, validation_error: ValidationError):
        self.pydantic_error = str(validation_error)
        super().__init__(validation_error.raw_errors, validation_error.model)

    @property
    def error_keys(self):
        return [e["loc"][0] for e in self.errors()]

    def __str__(self):
        return (
            f"{self.pydantic_error}\n\n"
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
