import json
from contextlib import nullcontext
from typing import Optional
from typing import Union

import click
from click import BadOptionUsage
from click import File
from rich.panel import Panel

from _incydr_cli import console
from _incydr_cli import get_user_project_path
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.event_filter_options import advanced_query_option
from _incydr_cli.cmds.options.event_filter_options import event_filter_options
from _incydr_cli.cmds.options.event_filter_options import saved_search_option
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import output_options
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cmds.options.utils import checkpoint_option
from _incydr_cli.cmds.utils import warn_interrupt
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_cli.cursor import CursorStore
from _incydr_cli.logger import get_server_logger
from _incydr_sdk.core.client import Client
from _incydr_sdk.enums.file_events import RiskIndicators
from _incydr_sdk.enums.file_events import RiskSeverity
from _incydr_sdk.file_events.models.event import FileEventV2
from _incydr_sdk.file_events.models.response import SavedSearch
from _incydr_sdk.queries.file_events import EventQuery
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def file_events():
    """View and manage file events."""


@file_events.command(cls=IncydrCommand)
@checkpoint_option
@table_format_option
@columns_option
@output_options
@advanced_query_option
@saved_search_option
@event_filter_options
@logging_options
def search(
    format_: TableFormat,
    columns: Optional[str],
    output: Optional[str],
    certs: Optional[str],
    ignore_cert_validation: Optional[bool],
    advanced_query: Optional[Union[str, File]],
    saved_search: Optional[str],
    start: Optional[str],
    end: Optional[str],
    event_action: Optional[str],
    username: Optional[str],
    md5: Optional[str],
    sha256: Optional[str],
    source_category: Optional[str],
    destination_category: Optional[str],
    file_name: Optional[str],
    file_directory: Optional[str],
    file_category: Optional[str],
    risk_indicator: Optional[RiskIndicators],
    risk_severity: Optional[RiskSeverity],
    risk_score: Optional[int],
    checkpoint_name: Optional[str],
):
    """
    Search file events. Various options are provided to filter query results.

    Use the `--saved-search` or the `--advanced-query` option if the available filters don't satisfy your requirements.

    Defaults to returning events with a risk score >= 1.  Add the `--risk-score 0` filter to return all events,
    including those with no risk associated with them.

    Results will be output to the console by default, use the `--output` option to send data to a server.

    Checkpointing is available through the `--checkpoint <checkpoint-name>` option and will only return new results
    on subsequent queries with that same checkpoint.  Checkpointing stores the original query it was run with, so
    additional filters on subsequent runs will be ignored.
    """
    if output:
        format_ = TableFormat.json_lines

    client = Client()

    if saved_search:
        saved_search = client.file_events.v2.get_saved_search(saved_search)
        query = EventQuery.from_saved_search(saved_search)
    elif advanced_query:
        if not isinstance(advanced_query, str):
            advanced_query = advanced_query.read()
        query = EventQuery.parse_raw(advanced_query)
    else:
        if not start:
            raise BadOptionUsage(
                "start",
                "--start option required if not using --saved-search or --advanced-query options.",
            )
        query = _create_query(
            start=start,
            end=end,
            event_action=event_action,
            username=username,
            md5=md5,
            sha256=sha256,
            source_category=source_category,
            destination_category=destination_category,
            file_name=file_name,
            file_directory=file_directory,
            file_category=file_category,
            risk_indicator=risk_indicator,
            risk_severity=risk_severity,
            risk_score=risk_score,
        )

    query.page_size = 10000

    if checkpoint_name:
        cursor = _get_cursor_store(client.settings.api_client_id)
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint:  # if stored checkpoint, overwrite query
            query = EventQuery.parse_raw(checkpoint)

        def checkpoint_func(event_):
            # Stored checkpoints are json strings of the original query with the `pageToken` key
            # updated to contain the ID of the last returned event
            q = query.copy()
            q.page_token = event_["event"]["id"]
            cursor.replace(checkpoint_name, json.dumps(q.dict()))

    else:
        checkpoint_func = None

    # skip pydantic modeling when output will just be json
    if format_ in (TableFormat.json_pretty, TableFormat.json_lines):

        def yield_all_events(q: EventQuery):
            while q.page_token is not None:
                response = client.session.post("/v2/file-events", json=q.dict())
                response_dict = response.json()
                q.page_token = response_dict.get("nextPgToken")
                page = response_dict.get("fileEvents")
                for event_ in page:
                    yield event_
                    if checkpoint_func:
                        checkpoint_func(event_)

    else:

        def yield_all_events(q: EventQuery):
            while q.page_token is not None:
                page = client.file_events.v2.search(q).file_events
                for event_ in page:
                    yield event_
                    if checkpoint_func:
                        checkpoint_func(event_.dict())

    events = yield_all_events(query)

    with warn_interrupt() if checkpoint_name else nullcontext():
        if output:
            logger = get_server_logger(output, certs, ignore_cert_validation)
            for event in events:
                logger.info(json.dumps(event))
            return

        if format_ == TableFormat.csv:
            render.csv(FileEventV2, events, columns=columns, flat=True)
        elif format_ == TableFormat.table:
            render.table(FileEventV2, events, columns=columns, flat=False)
        else:
            printed = False
            for event in events:
                printed = True
                if format_ == TableFormat.json_pretty:
                    console.print_json(data=event)
                else:
                    click.echo(json.dumps(event))
            if not printed:
                console.print("No results found.")


@file_events.command()
@click.argument("checkpoint-name")
def clear_checkpoint(checkpoint_name: str):
    """Remove the saved file events checkpoint from searches made with `--checkpoint` mode."""
    client = Client()
    cursor = _get_cursor_store(client.settings.api_client_id)
    cursor.delete(checkpoint_name)


@file_events.command(cls=IncydrCommand)
@single_format_option
@click.argument("search-id")
@logging_options
def show_saved_search(
    search_id: str,
    format_: SingleFormat,
):
    """
    Show details for a single saved search.
    """
    client = Client()
    saved_search = client.file_events.v2.get_saved_search(search_id)
    if format_ == SingleFormat.rich:
        console.print(Panel.fit(model_as_card(saved_search)))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(saved_search.json())
    else:
        click.echo(saved_search.json())


@file_events.command(cls=IncydrCommand)
@table_format_option
@columns_option
@logging_options
def list_saved_searches(
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List saved searches.
    """
    client = Client()
    searches = client.file_events.v2.list_saved_searches()
    if format_ == TableFormat.table:
        render.table(SavedSearch, searches, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(SavedSearch, searches, columns=columns, flat=True)
    elif format_ == TableFormat.json_pretty:
        for s in searches:
            console.print_json(s.json())
    else:
        for s in searches:
            click.echo(s.json())


field_option_map = {
    "event_action": "event.action",
    "username": "user.email",
    "md5": "file.hash.md5",
    "sha256": "file.hash.sha256",
    "source_category": "source.category",
    "destination_category": "destination.category",
    "file_name": "file.name",
    "file_directory": "file.directory",
    "risk_indicator": "risk.indicators.name",
    "file_category": "file.category",
    "risk_severity": "risk.severity",
    "risk_score": "risk.score",
}


def _create_query(**kwargs):
    query = EventQuery(start_date=kwargs["start"], end_date=kwargs["end"])
    for k, v in kwargs.items():
        if v:
            if k in ["start", "end"]:
                continue
            elif k == "risk_score":
                query = query.greater_than(field_option_map[k], v)
            else:
                query = query.equals(field_option_map[k], v)
    return query


def _get_cursor_store(api_key):
    """
    Get cursor store for file event search checkpoints.
    """
    dir_path = get_user_project_path(
        "checkpoints",
        api_key,
        "file_event_checkpoints",
    )
    return CursorStore(dir_path, "file_events")


# Allows us to import individual command groups
if __name__ == "__main__":
    file_events()
