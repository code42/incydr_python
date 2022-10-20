import sys
from typing import Optional

import click
from click import Context
from click import echo

from incydr.cli import console
from incydr.cli import render
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import write_dict_to_csv


@click.group(cls=IncydrGroup)
def departments():
    pass


@departments.command("list", cls=IncydrCommand)
@table_format_option
@click.option(
    "--name", default=None, help="Filter by departments with a matching name."
)
@click.pass_context
def list_(ctx: Context, format_: TableFormat, name: Optional[str] = None):
    """
    Retrieve departments that have been pushed to Code42 from SCIM or User Directory Sync.

    The results can then be used with the watchlists commands to automatically assign users to watchlists by department.
    """
    if not format_:
        format_ = TableFormat.table
    client = ctx.obj()
    deps = list(client.departments.v1.iter_all(name=name))

    # TODO: output is an array of strings

    if not any(deps):
        echo("No results found.")
        return

    deps_dict = [{"name": i} for i in deps]

    if format_ == TableFormat.table and client.settings.use_rich:
        with console.pager():
            render.table_json(deps_dict, columns=None, title="Departments")

    # doesn't work for nested objects
    elif format_ == TableFormat.csv:
        write_dict_to_csv(deps_dict, sys.stdout, columns=None)

    elif format_ == TableFormat.json:
        console.print_json(data=deps)

    else:
        echo(deps)
