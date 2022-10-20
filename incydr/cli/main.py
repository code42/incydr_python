import click

from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.cases import cases
from incydr.cli.cmds.departments import departments
from incydr.cli.cmds.file_events import file_events
from incydr.cli.core import IncydrGroup


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def incydr(ctx, log_level, log_file):
    init_client(ctx, log_level, log_file)
    pass


incydr.add_command(departments)
incydr.add_command(file_events)
incydr.add_command(cases, name="cases")

if __name__ == "__main__":
    incydr()
