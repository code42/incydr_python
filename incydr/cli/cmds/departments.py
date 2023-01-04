import json
from typing import Optional

import click
from click import echo

from incydr._core.client import Client
from incydr.cli import console
from incydr.cli import logging_options
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import list_as_panel


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
