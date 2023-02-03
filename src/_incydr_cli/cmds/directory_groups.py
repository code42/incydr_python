from typing import Optional

import click

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from incydr.models import DirectoryGroup


@click.group(cls=IncydrGroup)
@logging_options
def directory_groups():
    """View directory groups."""


# Did not provide columns option because there are only two columns [groupId, name]
@directory_groups.command("list", cls=IncydrCommand)
@table_format_option
@click.option(
    "--name", default=None, help="Filter by directory groups with a matching name."
)
@logging_options
def list_(
    format_: TableFormat,
    name: Optional[str],
):
    """
    Retrieve directory group information that has been pushed to Code42 from SCIM or User Directory Sync.

    The results can then be used with the watchlists commands to automatically assign users to watchlists by directory group.
    """
    client = Client()
    groups = client.directory_groups.v1.iter_all(name=name)

    if format_ == TableFormat.table:
        render.table(DirectoryGroup, groups)
    elif format_ == TableFormat.csv:
        render.csv(DirectoryGroup, groups)
    elif format_ == TableFormat.json_pretty:
        for group in groups:
            console.print_json(group.json())
    else:
        for group in groups:
            click.echo(group.json())
