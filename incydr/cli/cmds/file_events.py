from typing import Optional

import click
from click import BadOptionUsage
from click import Context
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from typer import echo

from incydr._file_events.client import _create_query_from_saved_search
from incydr._file_events.models.response import SavedSearch
from incydr._queries.file_events import EventQuery
from incydr._queries.file_events import Query
from incydr.cli import console
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
from incydr.cli.cmds.utils import output_models_format
from incydr.cli.cmds.utils import output_response_format
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.enums.file_events import RiskIndicators
from incydr.enums.file_events import RiskSeverity


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
def file_events():
    pass


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
    include_all: Optional[bool],  # TODO - do we want this option
):
    """
    Search file events.

    Various options are provided to filter query results.  Use the `--saved-search` and `--advanced-query` options if the available filters don't satisfy your requirements.

    Results will be output to the console by default, use the `--output` option to send data to a server.
    """
    client = ctx.obj()

    if saved_search and advanced_query:
        raise BadOptionUsage(
            "saved-search",
            "--saved-search and --advanced-query options are incompatible.",
        )

    if saved_search:
        query = _create_query_from_saved_search(
            client.file_events.v2.get_saved_search(saved_search)
        )
    elif advanced_query:
        query = Query.parse_raw(advanced_query)
    else:
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
            include_all=include_all,
        )
    events = client.session.post("/v2/file-events", json=query.dict())
    if output:
        output_format_logger(
            events, output, format_, columns, certs, ignore_cert_validation
        )
    else:
        output_response_format(
            events,
            "fileEvents",
            "File Events",
            format_,
            columns,
            client.settings.use_rich,
        )


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
    searches = client.file_events.v2.list_saved_searches().searches
    output_models_format(
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
    include_no_risk_events = False
    for k, v in kwargs.items():
        if v:
            if k in ["start", "end", "include_all"]:
                continue
            elif k == "include_all":
                include_no_risk_events = True
            elif k == "risk_score":
                query = query.greater_than(field_option_map[k], v)
            else:
                query = query.equals(field_option_map[k], v)
    if not include_no_risk_events and not kwargs["risk_severity"]:
        query = query.not_equals("risk.severity", RiskSeverity.NO_RISK_INDICATED)
    return query


# Allows us to import individual command groups
if __name__ == "__main__":
    file_events()
