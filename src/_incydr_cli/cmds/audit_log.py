import json
import os
from contextlib import nullcontext
from datetime import timezone
from hashlib import md5
from itertools import count
from typing import Optional

import click
from pydantic import Field

from _incydr_cli import console
from _incydr_cli import get_user_project_path
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.audit_log_filter_options import filter_options
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import output_options
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cmds.options.utils import checkpoint_option
from _incydr_cli.cmds.utils import warn_interrupt
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_cli.cursor import CursorStore
from _incydr_cli.logger import get_server_logger
from _incydr_sdk.audit_log.models import DateRange
from _incydr_sdk.audit_log.models import QueryAuditLogRequest
from _incydr_sdk.core.client import Client
from _incydr_sdk.core.models import Model
from _incydr_sdk.queries.utils import parse_str_to_dt
from _incydr_sdk.queries.utils import parse_ts_to_posix_ts


@click.group(cls=IncydrGroup)
@logging_options
def audit_log():
    """View audit log events."""


@audit_log.command("search", cls=IncydrCommand)
@checkpoint_option
@click.option(
    "--format",
    "-f",
    "format_",
    type=click.Choice(
        [TableFormat.csv, TableFormat.json_lines, TableFormat.json_pretty]
    ),
    help="Format to print result. One of 'json-pretty', 'json-lines', or 'csv. "
    "'table' format is unavailable due to long processing times for very large data sets."
    "If environment has INCYDR_USE_RICH=false set, defaults to 'json-lines', else defaults to 'json-pretty'."
    "CSV output includes limited fields, use audit-log download for a more comprehensive CSV download.",
    default=TableFormat.json_pretty,
)
@filter_options
@columns_option
@output_options
@logging_options
def search(
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
    checkpoint_name: Optional[str],
):
    """
    Search audit log events.  Returns all events that match the search criteria with paging.

    Defaults to searching for most recent events.

    Results will be output to the console by default, use the `--output` option to send data to a server.

    Checkpointing is available through the `--checkpoint <checkpoint-name>` option and will only return new results
    on subsequent queries with that same checkpoint. Checkpointing filters by timestamp, additional filter
    options will need to be included in each run.
    """
    client = Client()
    cursor = _get_cursor_store(client.settings.api_client_id)

    if output:
        format_ = TableFormat.json_lines

    # skip pydantic modeling when output will just be json
    if format_ in (TableFormat.json_pretty, TableFormat.json_lines):

        def yield_all_events(request_):
            for page_num in count(0):
                request_.page = page_num
                page = client.session.post(
                    "/v1/audit/search-audit-log", json=request_.dict()
                )
                events = page.json().get("events")
                yield from events
                if len(events) < request_.pageSize:
                    break

    else:

        def yield_all_events(request_):
            for page_num in count(0):
                request_.page = page_num
                page = client.session.post(
                    "/v1/audit/search-audit-log", json=request_.dict()
                )
                events = page.json().get("events")
                for e in events:
                    yield DefaultAuditEvent.parse_obj(e)
                if len(events) < request_.pageSize:
                    break

    # Use stored checkpoint timestamp for start filter if applicable
    if checkpoint_name:
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint:
            start = float(checkpoint)

    # Checks if start float timestamp was read from checkpoints
    start = parse_ts_to_posix_ts(start) if isinstance(start, str) else start

    request = QueryAuditLogRequest(
        actorIds=actor_ids.split(",") if actor_ids else None,
        actorIpAddresses=actor_ip_addresses.split(",") if actor_ip_addresses else None,
        actorNames=actor_names.split(",") if actor_names else None,
        eventTypes=event_types.split(",") if event_types else None,
        resourceIds=resource_ids.split(",") if resource_ids else None,
        userTypes=user_types.split(",") if user_types else None,
        dateRange=DateRange(
            startTime=start or None,
            endTime=parse_ts_to_posix_ts(end) if end else None,
        ),
        page=0,
        pageSize=100,
    )
    events_gen = yield_all_events(request)

    # Checkpointing
    if checkpoint_name:
        events_gen = _update_checkpoint(cursor, checkpoint_name, events_gen)

    with warn_interrupt() if checkpoint_name else nullcontext():
        if output:
            logger = get_server_logger(output, certs, ignore_cert_validation)
            for event in events_gen:
                logger.info(json.dumps(event))
            return

        if format_ == TableFormat.csv:
            render.csv(DefaultAuditEvent, events_gen, columns=columns, flat=True)
        else:
            printed = False
            for event in events_gen:  # Generator of audit log events in dict format
                printed = True
                if format_ == TableFormat.json_pretty:
                    console.print_json(data=event)
                else:
                    click.echo(json.dumps(event))
            if not printed:
                console.print("No results found.")


@audit_log.command()
@click.argument("checkpoint-name")
def clear_checkpoint(checkpoint_name: str):
    """Remove the saved audit log checkpoint from searches made with `--checkpoint` mode."""
    client = Client()
    cursor = _get_cursor_store(client.settings.api_client_id)
    cursor.delete(checkpoint_name)


@audit_log.command(cls=IncydrCommand)
@filter_options
@click.option(
    "--path",
    help="The file path where to save the CSV. Defaults to the current directory if not specified.",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.getcwd(),
)
@logging_options
def download(
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
    client = Client()

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


def _update_checkpoint(cursor, checkpoint_name, events_gen):
    """
    De-duplicates events across checkpointed runs.

    Since using the timestamp of the last event
    processed as the `--start` time of the next run causes the last event to show up again in the
    next results, we hash the last event(s) of each run and store those hashes in the cursor to
    filter out on the next run.

    It's also possible that two events have the exact same timestamp, so
    `checkpoint_events` needs to be a list of hashes so we can filter out everything that's actually
    been processed.
    """

    checkpoint_events = cursor.get_items(checkpoint_name)
    new_timestamp = None
    new_events = []
    for event in events_gen:
        # if event is a model, convert to a dict
        event_as_dict = event.dict() if isinstance(event, Model) else event
        event_hash = _hash_event(event_as_dict)
        if event_hash not in checkpoint_events:
            ts = parse_str_to_dt(event_as_dict["timestamp"])
            if not new_timestamp or ts > new_timestamp:
                new_timestamp = ts
                new_events.clear()
            new_events.append(event_hash)
            yield event
            new_timestamp.replace(tzinfo=timezone.utc)
            cursor.replace(checkpoint_name, new_timestamp.timestamp())
            cursor.replace_items(checkpoint_name, new_events)


def _hash_event(event):
    if isinstance(event, dict):
        event = json.dumps(event, sort_keys=True)
    return md5(event.encode()).hexdigest()


def _get_cursor_store(api_key):
    """
    Get cursor store for audit log search checkpoints.
    """
    dir_path = get_user_project_path(
        "checkpoints",
        api_key,
        "audit_log_checkpoints",
    )
    return CursorStore(dir_path, "audit_events")


class DefaultAuditEvent(Model):
    type: str = Field(None, alias="type$")
    actor_id: str = Field(None, alias="actorId")
    actor_name: str = Field(None, alias="actorName")
    actor_agent: str = Field(None, alias="actorAgent")
    actor_ip_addresses: str = Field(None, alias="actorIpAddress")
    timestamp: str
