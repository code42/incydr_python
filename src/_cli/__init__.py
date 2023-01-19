import os

import click
from _cli.utils import get_user_project_path
from rich.console import Console

ERROR_LOG_FILE_NAME = "incydr_cli.log"

console = Console()


def log_level_callback(ctx, param, value):
    """callback to update log_level environment variable"""
    if not value:
        return
    os.environ.update({"INCYDR_LOG_LEVEL": value})
    return value


def log_file_callback(ctx, param, value):
    """callback to update log_file and log_stderr environment variable"""
    if not value:
        return
    os.environ.update({"INCYDR_LOG_FILE": value})
    return value


def log_stderr_callback(ctx, param, value):
    """callback to update log_stderr environment variable"""
    if not value:
        os.environ.update({"INCYDR_LOG_STDERR": "FALSE"})
        return
    os.environ.update({"INCYDR_LOG_STDERR": "TRUE"})
    return value


log_level_option = click.option(
    "--log-level",
    help="Set level for Incydr client logging.",
    default="WARNING",
    callback=log_level_callback,
    expose_value=False,
)

log_file_option = click.option(
    "--log-file",
    help="Specify file path to write log output to.",
    default=str(os.path.join(get_user_project_path("log"), ERROR_LOG_FILE_NAME)),
    callback=log_file_callback,
    expose_value=False,
)

log_stderr_option = click.option(
    "--log-stderr",
    "log_stderr",
    help="Silence logging to stderr.",
    default=False,
    is_flag=True,
    callback=log_stderr_callback,
    expose_value=False,
)


def logging_options(f):
    f = log_level_option(f)
    f = log_file_option(f)
    f = log_stderr_option(f)
    return f
