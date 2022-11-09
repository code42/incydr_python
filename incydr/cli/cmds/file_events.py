import json
from typing import Optional

import click
from click import BadOptionUsage
from click import Context
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from typer import echo

from incydr._file_events.models.response import SavedSearch
from incydr._queries.file_events import EventQuery
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.filter_options import advanced_query_option
from incydr.cli.cmds.options.filter_options import filter_options
from incydr.cli.cmds.options.filter_options import saved_search_option
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import output_options
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.utils import output_format_logger
from incydr.cli.cmds.utils import output_response_format
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.enums.file_events import RiskIndicators
from incydr.enums.file_events import RiskSeverity
from incydr.models import FileEventV2


def render_search(search_: SavedSearch):
    field_table = Table.grid(padding=(0, 1), expand=False)
    field_table.title = f"Saved Search {search_.id}"
    for name, _field in search_.__fields__.items():
        if name == "id":
            continue
        if name == "notes" and search_.notes is not None:
            field_table.add_row(
                Panel(
                    Markdown(search_.notes, justify="left"),
                    title="Notes",
                    width=80,
                )
            )
        else:
            field_table.add_row(f"{name} = {getattr(search_, name)}")
    console.print(Panel.fit(field_table))


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def file_events(ctx, log_level, log_file):
    """View and manage file events."""
    init_client(ctx, log_level, log_file)


@file_events.command(cls=IncydrCommand)
@table_format_option
@columns_option
@output_options
@advanced_query_option
@saved_search_option
@filter_options
@click.pass_context
def search(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
    output: Optional[str],
    certs: Optional[str],
    ignore_cert_validation: Optional[bool],
    advanced_query: Optional[str],
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
):
    """
    Search file events.

    Various options are provided to filter query results.  Use the `--saved-search` and `--advanced-query` options if the available filters don't satisfy your requirements.

    Defaults to returning events with a risk score >= 1.  Add the `--risk-score 0` filter to return all events, including those with no risk associated with them.

    Results will be output to the console by default, use the `--output` option to send data to a server.
    """
    client = ctx.obj()

    if saved_search:
        saved_search = client.file_events.v2.get_saved_search(saved_search)
        query = EventQuery.from_saved_search(saved_search)
    elif advanced_query:
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

    # skip pydantic modeling when output will just be json
    if output or format_ in ("json", "raw-json"):

        def yield_all_events(q: EventQuery):
            while q.page_token is not None:
                response = client.session.post("/v2/file-events", json=q.dict())
                yield from response.json()["fileEvents"]

    else:

        def yield_all_events(q: EventQuery):
            while q.page_token is not None:
                yield from client.file_events.v2.search(q).file_events

    events = yield_all_events(query)

    if output:
        output_format_logger(events, output, columns, certs, ignore_cert_validation)
        return

    if format_ == "csv":
        render.csv(FileEventV2, events, columns=columns, flat=True)
    if format_ == "table" or format_ is None:
        render.table(FileEventV2, events, columns=columns, flat=False)
    if format_ == "json":
        for event in events:
            console.print_json(data=event)
    if format_ == "raw-json":
        for event in events:
            print(json.dumps(event))


@file_events.command(cls=IncydrCommand)
@single_format_option
@click.argument("search-id")
@click.pass_context
def show_saved_search(ctx: Context, search_id: str, format_: SingleFormat):
    """
    Show details for a single saved search.
    """
    client = ctx.obj()
    saved_search = client.file_events.v2.get_saved_search(search_id)
    if format_ == SingleFormat.rich and client.settings.use_rich:
        render_search(saved_search)

    elif format_ == SingleFormat.json:
        console.print_json(saved_search.json())

    else:
        echo(saved_search.json())


@file_events.command(cls=IncydrCommand)
@table_format_option
@columns_option
@click.pass_context
def list_saved_searches(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List saved searches.
    """
    client = ctx.obj()
    response = client.session.get("/v2/file-events/saved-searches")
    searches = response.json()["searches"]
    output_response_format(
        searches, "Saved Searches", format_, columns, client.settings.use_rich
    )


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
            if k in ["start", "end", "include_all"]:
                continue
            elif k == "risk_score":
                query = query.greater_than(field_option_map[k], v)
            else:
                query = query.equals(field_option_map[k], v)
    return query


# Allows us to import individual command groups
if __name__ == "__main__":
    file_events()
