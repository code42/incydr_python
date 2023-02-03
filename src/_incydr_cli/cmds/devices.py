import click
from rich.panel import Panel

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.devices.models import Device
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def devices():
    """View devices."""


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
@logging_options
def list_(
    active: bool = None,
    blocked: bool = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List devices.
    """
    client = Client()
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
    elif format_ == TableFormat.json_pretty:
        for device in devices:
            console.print_json(device.json())
    else:
        for device in devices:
            click.echo(device.json())


@devices.command(cls=IncydrCommand)
@click.argument("device_id")
@single_format_option
@logging_options
def show(
    device_id: str,
    format_: SingleFormat,
):
    """
    Show details for a single device.
    """
    client = Client()
    device = client.devices.v1.get_device(device_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(
            Panel.fit(model_as_card(device), title=f"Device {device.device_id}")
        )
    elif format_ == SingleFormat.json_pretty:
        console.print_json(device.json())
    else:
        click.echo(device.json())
