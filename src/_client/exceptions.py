import os

import click
from _cli import ERROR_LOG_FILE_NAME
from _cli import get_user_project_path
from click._compat import get_text_stderr


class IncydrException(click.ClickException):
    """Wrapper class for Incydr CLI exceptions. The `message` param automatically gets logged to error file and printed
    to stderr in red text. If `help` param is provided, it will also be printed to stderr after the
    message but not logged to file.
    """

    def __init__(self, message, help=None):
        self.help = help
        super().__init__(message)

    def show(self, file=None):
        """Override default `show` to print CLI errors in red text."""
        if file is None:
            file = get_text_stderr()
        click.secho(f"ERROR: {self.format_message()}", file=file, fg="red")
        if self.help:
            click.echo(self.help, err=True)


class LoggedCLIError(IncydrException):
    """Exception to be raised when wanting to point users to error logs for error details.

    If `message` param is provided it will be printed to screen along with message on where to
    find error details in the log.
    """

    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

    def format_message(self):
        path = os.path.join(get_user_project_path("log"), ERROR_LOG_FILE_NAME)
        locations_message = f"View details in {path}"
        return (
            f"{self.message}\n{locations_message}"
            if self.message
            else locations_message
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
