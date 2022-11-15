import json
from typing import Optional

import click
from click import Context
from click import echo

from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import list_as_panel


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def departments(ctx, log_level, log_file):
    """View departments."""
    init_client(ctx, log_level, log_file)


@departments.command("list", cls=IncydrCommand)
@single_format_option
@click.option(
    "--name", default=None, help="Filter by departments with a matching name."
)
@click.pass_context
def list_(ctx: Context, format_: SingleFormat, name: Optional[str] = None):
    """
    Retrieve departments that have been pushed to Code42 from SCIM or User Directory Sync.

    The results can then be used with the watchlists commands to automatically assign users to watchlists by department.
    """
    client = ctx.obj()
    if not client.settings.use_rich and format_ == SingleFormat.rich:
        format_ = SingleFormat.raw_json
    deps = list(client.departments.v1.iter_all(name=name))

    if not deps:
        echo("No results found.")
        return

    if format_ == SingleFormat.rich:
        console.print(list_as_panel(deps, expand=False, title="Departments"))
    elif format_ == SingleFormat.json:
        console.print_json(data=deps)
    else:
        console.print(json.dumps(deps), highlight=False)
