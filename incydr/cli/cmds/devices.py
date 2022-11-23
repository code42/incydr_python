import click
from click import Context
from rich.panel import Panel

from incydr._devices.models import Device
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import model_as_card


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def devices(ctx, log_level, log_file):
    """View devices."""
    init_client(ctx, log_level, log_file)


@devices.command("list", cls=IncydrCommand)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive devices. Defaults to returning both when when neither option is passed.",
)
@click.option(
    "--blocked/--unblocked",
    default=None,
    help="Filter by blocked or unblocked devices. Defaults to returning both when when neither option is passed.",
)
@table_format_option
@columns_option
@click.pass_context
def list_(
    ctx: Context,
    active: bool = None,
    blocked: bool = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List devices.
    """
    client = ctx.obj()
    devices = client.devices.v1.iter_all(active, blocked)

    if format_ == TableFormat.table:
        columns = columns or [
            "device_id",
            "name",
            "os_hostname",
            "status",
            "active",
            "blocked",
            "alert_state",
            "org_guid",
            "login_date",
        ]
        render.table(Device, devices, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(Device, devices, columns=columns, flat=True)
    elif format_ == TableFormat.json:
        for device in devices:
            console.print_json(device.json())
    else:
        for device in devices:
            click.echo(device.json())


@devices.command(cls=IncydrCommand)
@click.argument("device_id")
@single_format_option
@click.pass_context
def show(ctx: Context, device_id: str, format_: SingleFormat = None):
    """
    Show details for a single device.
    """
    client = ctx.obj()
    device = client.devices.v1.get_device(device_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(
            Panel.fit(model_as_card(device), title=f"Device {device.device_id}")
        )
    elif format_ == SingleFormat.json:
        console.print_json(device.json())
    else:  # format == "raw-json"
        click.echo(device.json())
