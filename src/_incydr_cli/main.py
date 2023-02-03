import os
import platform
import site
import sys

import click
from requests.exceptions import HTTPError

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli.cmds.alert_rules import alert_rules
from _incydr_cli.cmds.alerts import alerts
from _incydr_cli.cmds.audit_log import audit_log
from _incydr_cli.cmds.cases import cases
from _incydr_cli.cmds.departments import departments
from _incydr_cli.cmds.devices import devices
from _incydr_cli.cmds.directory_groups import directory_groups
from _incydr_cli.cmds.file_events import file_events
from _incydr_cli.cmds.trusted_activities import trusted_activities
from _incydr_cli.cmds.user_risk_profiles import risk_profiles
from _incydr_cli.cmds.users import users
from _incydr_cli.cmds.watchlists import watchlists
from _incydr_cli.core import ExceptionHandlingGroup
from _incydr_sdk.__version__ import __version__

if platform.system() in ("Darwin", "Linux"):
    os.environ["MANPAGER"] = "less -S"
else:
    ...
    # TODO: figure out Windows pager to use


@click.group(
    cls=ExceptionHandlingGroup,
    invoke_without_command=True,
    no_args_is_help=True,
    help=f"Incydr CLI by Code42 Software. Version {__version__}",
)
@click.option("--version", is_flag=True)
@click.option(
    "--python",
    is_flag=True,
    help="Print path to the python interpreter env that `incydr` is installed in.",
)
@click.option(
    "--script-dir",
    is_flag=True,
    help="Print the directory the `incydr` script was installed in (for adding to your PATH if needed).",
)
@logging_options
def incydr(version, python, script_dir):
    if version:
        console.print(__version__, highlight=False)
    if python:
        console.print(sys.executable, highlight=False)
        sys.exit(0)
    if script_dir:
        for root, _dirs, files in os.walk(site.PREFIXES[0]):
            if "incydr" in files or "incydr.exe" in files:
                console.print(root, highlight=False)
                sys.exit(0)

        for root, _dirs, files in os.walk(site.USER_BASE):
            if "incydr" in files or "incydr.exe" in files:
                console.print(root, highlight=False)
                sys.exit(0)


incydr.add_command(alerts)
incydr.add_command(alert_rules)
incydr.add_command(audit_log)
incydr.add_command(departments)
incydr.add_command(devices)
incydr.add_command(directory_groups)
incydr.add_command(file_events)
incydr.add_command(cases)
incydr.add_command(risk_profiles)
incydr.add_command(trusted_activities)
incydr.add_command(users)
incydr.add_command(watchlists)

if __name__ == "__main__":
    try:
        incydr()
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")
