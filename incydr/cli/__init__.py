import click
from rich.console import Console

from incydr import Client

console = Console()

log_level_option = click.option(
    "--log-level", help="Set level for Incydr client logging.", default="WARNING"
)

log_file_option = click.option(
    "--log-file", help="Specify file path to write log output to.", default=None
)


def init_client(ctx, log_level, log_file):
    log_stderr = not log_file
    ctx.obj = lambda: Client(
        log_level=log_level, log_file=log_file, log_stderr=log_stderr
    )
