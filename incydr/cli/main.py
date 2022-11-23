import os
import platform

import click
from requests.exceptions import HTTPError

from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.alerts import alerts
from incydr.cli.cmds.audit_log import audit_log
from incydr.cli.cmds.cases import cases
from incydr.cli.cmds.departments import departments
from incydr.cli.cmds.directory_groups import directory_groups
from incydr.cli.cmds.file_events import file_events
from incydr.cli.cmds.user_risk_profiles import risk_profiles
from incydr.cli.cmds.users import users
from incydr.cli.cmds.watchlists import watchlists
from incydr.cli.core import IncydrGroup

if platform.system() in ("Darwin", "Linux"):
    os.environ["MANPAGER"] = "less -S"
else:
    ...
    # TODO: figure out Windows pager to use


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def incydr(ctx, log_level, log_file):
    init_client(ctx, log_level, log_file)


incydr.add_command(alerts)
incydr.add_command(audit_log)
incydr.add_command(departments)
incydr.add_command(directory_groups)
incydr.add_command(file_events)
incydr.add_command(cases, name="cases")
incydr.add_command(risk_profiles)
incydr.add_command(users)
incydr.add_command(watchlists)

if __name__ == "__main__":
    try:
        incydr()
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")
