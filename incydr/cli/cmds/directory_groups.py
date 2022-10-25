from typing import Optional

import click
from click import Context

from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.utils import output_models_format
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def directory_groups(ctx, log_level, log_file):
    """View directory groups."""
    init_client(ctx, log_level, log_file)


# Did not provide columns option because there are only two columns [groupId, name]
@directory_groups.command("list", cls=IncydrCommand)
@table_format_option
@click.option(
    "--name", default=None, help="Filter by directory groups with a matching name."
)
@click.pass_context
def list_(ctx: Context, format_: TableFormat, name: Optional[str] = None):
    """
    Retrieve directory group information that has been pushed to Code42 from SCIM or User Directory Sync.

    The results can then be used with the watchlists commands to automatically assign users to watchlists by directory group.
    """
    if not format_:
        format_ = TableFormat.table
    client = ctx.obj()
    groups = client.directory_groups.v1.iter_all(name=name)
    output_models_format(
        groups, "Directory Groups", format_, None, client.settings.use_rich
    )
