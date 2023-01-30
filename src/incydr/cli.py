import os
import platform

import click
from _cli import console
from _cli import logging_options
from _cli.cmds.alert_rules import alert_rules
from _cli.cmds.alerts import alerts
from _cli.cmds.audit_log import audit_log
from _cli.cmds.cases import cases
from _cli.cmds.departments import departments
from _cli.cmds.devices import devices
from _cli.cmds.directory_groups import directory_groups
from _cli.cmds.file_events import file_events
from _cli.cmds.trusted_activities import trusted_activities
from _cli.cmds.user_risk_profiles import risk_profiles
from _cli.cmds.users import users
from _cli.cmds.watchlists import watchlists
from _cli.core import ExceptionHandlingGroup
from requests.exceptions import HTTPError

if platform.system() in ("Darwin", "Linux"):
    os.environ["MANPAGER"] = "less -S"
else:
    ...
    # TODO: figure out Windows pager to use


@click.group(cls=ExceptionHandlingGroup)
@logging_options
def incydr():
    """Incydr CLI tool."""


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
