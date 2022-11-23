import os
from typing import Optional

import click
from click import Context

from incydr._audit_log.models import DateRange
from incydr._audit_log.models import QueryAuditLogRequest
from incydr._queries.utils import parse_timestamp_to_posix_timestamp
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.options.audit_log_filter_options import filter_options
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import output_options
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.utils import output_format_logger
from incydr.cli.cmds.utils import output_response_format
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def audit_log(ctx, log_level, log_file):
    """View audit log events."""
    init_client(ctx, log_level, log_file)


@audit_log.command("search", cls=IncydrCommand)
@table_format_option
@filter_options
@columns_option
@output_options
@click.pass_context
def search(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
    output: Optional[str],
    certs: Optional[str],
    ignore_cert_validation: Optional[bool],
    start: Optional[str],
    end: Optional[str],
    actor_ids: Optional[str],
    actor_ip_addresses: Optional[str],
    actor_names: Optional[str],
    event_types: Optional[str],
    resource_ids: Optional[str],
    user_types: Optional[str],
):
    """
    Search audit log events.  Returns all events that match the search criteria with paging.

    Defaults to searching for most recent events.

    Results will be output to the console by default, use the `--output` option to send data to a server.
    """
    # TODO: checkpointing
    client = ctx.obj()

    date_range = DateRange(
        startTime=None if not start else parse_timestamp_to_posix_timestamp(start),
        endTime=None if not end else parse_timestamp_to_posix_timestamp(end),
    )

    request = QueryAuditLogRequest(
        actorIds=actor_ids.split(",") if isinstance(actor_ids, str) else None,
        actorIpAddresses=actor_ip_addresses.split(",")
        if isinstance(actor_ip_addresses, str)
        else None,
        actorNames=actor_names.split(",") if isinstance(actor_names, str) else None,
        eventTypes=event_types.split(",") if isinstance(event_types, str) else None,
        resourceIds=resource_ids.split(",") if isinstance(resource_ids, str) else None,
        userTypes=user_types.split(",") if isinstance(user_types, str) else None,
        dateRange=date_range,
        pageNum=0,
        pageSize=100,
    )
    events = client.session.post("/v1/audit/search-audit-log", json=request.dict())
    events = events.json()["events"]

    # TODO: output refactor
    if output:
        output_format_logger(events, output, columns, certs, ignore_cert_validation)
    else:
        output_response_format(
            events,
            "Audit Log Events",
            format_,
            columns,
            client.settings.use_rich,
        )


@audit_log.command(cls=IncydrCommand)
@filter_options
@click.option(
    "--path",
    help="The file path where to save the CSV. Defaults to the current directory if not specified.",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.getcwd(),
)
@click.pass_context
def download(
    ctx: Context,
    path: Optional[str],
    start: Optional[str],
    end: Optional[str],
    actor_ids: Optional[str],
    actor_ip_addresses: Optional[str],
    actor_names: Optional[str],
    event_types: Optional[str],
    resource_ids: Optional[str],
    user_types: Optional[str],
):
    """
    Download audit log events in CSV format.  Returns up to the most recent 100,000 events that match the search criteria.

    Use the --path option to specify where to save the CSV.  Defaults to the current directory if not specified.
    """
    client = ctx.obj()

    # convert str to list
    actor_ids = actor_ids.split(",") if isinstance(actor_ids, str) else None
    actor_names = actor_names.split(",") if isinstance(actor_names, str) else None
    actor_ip_addresses = (
        actor_ip_addresses.split(",") if isinstance(actor_ip_addresses, str) else None
    )
    event_types = event_types.split(",") if isinstance(event_types, str) else None
    resource_ids = resource_ids.split(",") if isinstance(resource_ids, str) else None
    user_types = user_types.split(",") if isinstance(user_types, str) else None

    client.audit_log.v1.download_events(
        path,
        actor_ids,
        actor_ip_addresses,
        actor_names,
        start,
        end,
        event_types,
        resource_ids,
        user_types,
    )

    console.print(f"Audit log events downloaded to '{path}'")
