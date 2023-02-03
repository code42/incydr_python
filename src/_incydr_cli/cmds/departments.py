import json
from typing import Optional

import click
from click import echo

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.utils import list_as_panel


@click.group(cls=IncydrGroup)
@logging_options
def departments():
    """View departments."""


@departments.command("list", cls=IncydrCommand)
@single_format_option
@click.option(
    "--name", default=None, help="Filter by departments with a matching name."
)
@logging_options
def list_(
    format_: SingleFormat,
    name: Optional[str],
):
    """
    Retrieve departments that have been pushed to Code42 from SCIM or User Directory Sync.

    The results can then be used with the watchlists commands to automatically assign users to watchlists by department.
    """
    client = Client()
    if not client.settings.use_rich and format_ == SingleFormat.rich:
        format_ = SingleFormat.json_lines
    deps = list(client.departments.v1.iter_all(name=name))

    if not deps:
        echo("No results found.")
        return

    if format_ == SingleFormat.rich:
        console.print(list_as_panel(deps, expand=False, title="Departments"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(data=deps)
    else:
        click.echo(json.dumps(deps))
