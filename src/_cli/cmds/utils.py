# CLI - specific utils.py file to avoid circular imports
from functools import wraps
from signal import getsignal
from signal import SIGINT
from signal import signal

import click
from click import style


def user_lookup(client, value):
    """
    Returns the user ID for a given username, or returns the value unchanged if not a username.

    Used with the `user_lookup_callback` method on user args.
    """
    if "@" in str(value):
        # assume username/email was passed
        users = client.users.v1.get_page(username=value).users
        if len(users) < 1:
            raise ValueError(f"User with username '{value}' not found.")
        return users[0].user_id
        # else return ID
    return value


class warn_interrupt:
    """A context decorator class used to wrap functions where a keyboard interrupt could potentially
    leave things in a bad state. Warns the user with provided message and exits when wrapped
    function is complete. Requires user to ctrl-c a second time to force exit.

    Usage:

    @warn_interrupt(warning="example message")
    def my_important_func():
        pass
    """

    def __init__(self, warning="Cancelling operation cleanly, one moment... "):
        self.warning = warning
        self.old_int_handler = None
        self.interrupted = False
        self.exit_instructions = style("Hit CTRL-C again to force quit.", fg="red")

    def __enter__(self):
        self.old_int_handler = getsignal(SIGINT)
        signal(SIGINT, self._handle_interrupts)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.interrupted:
            exit(1)
        signal(SIGINT, self.old_int_handler)

        return False

    def _handle_interrupts(self, sig, frame):
        if not self.interrupted:
            self.interrupted = True
            click.echo(f"\n{self.warning}\n{self.exit_instructions}", err=True)
        else:
            exit()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner
