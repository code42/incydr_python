from contextlib import nullcontext
from datetime import timezone
from typing import Optional
from typing import Union

import click
import requests
from boltons.iterutils import bucketize
from boltons.iterutils import chunked
from click import BadOptionUsage
from click import File
from pydantic import Field
from rich.panel import Panel

from _incydr_cli import console
from _incydr_cli import get_user_project_path
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.alert_filter_options import advanced_query_option
from _incydr_cli.cmds.options.alert_filter_options import filter_options
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import input_format_option
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
from _incydr_cli.file_readers import AutoDecodedFile
from _incydr_cli.logger import get_server_logger
from _incydr_sdk.alerts.models.alert import AlertSummary
from _incydr_sdk.core.client import Client
from _incydr_sdk.core.models import CSVModel
from _incydr_sdk.core.models import Model
from _incydr_sdk.queries.alerts import AlertQuery
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def alerts():
    """View and manage alerts."""


@alerts.command(cls=IncydrCommand)
@checkpoint_option
@logging_options
@columns_option
@table_format_option
@output_options
@advanced_query_option
@filter_options
def search(
    format_: TableFormat,
    columns: Optional[str],
    output: Optional[str],
    certs: Optional[str],
    ignore_cert_validation: Optional[bool],
    advanced_query: Optional[Union[str, File]],
    start: Optional[str],
    end: Optional[str],
    on: Optional[str],
    alert_id: Optional[str],
    type_: Optional[str],
    name: Optional[str],
    actor: Optional[str],
    actor_id: Optional[str],
    risk_severity: Optional[str],
    state: Optional[str],
    rule_id: Optional[str],
    alert_severity: Optional[str],
    checkpoint_name: Optional[str],
):
    """
    Search alerts.  Various options are provided to filter query results.

    Results will be output to the console by default, use the `--output` option to send data to a server.

    Checkpointing is available through the `--checkpoint <checkpoint-name>` option and will only return new results
    on subsequent queries with that same checkpoint.  Checkpointing filters by timestamp, additional filter
    options will need to be included in each run.
    """
    client = Client()
    cursor = _get_cursor_store(client.settings.api_client_id)

    if output:
        format_ = TableFormat.json_lines

    # Use stored checkpoint timestamp for start filter if applicable
    if checkpoint_name:
        checkpoint = cursor.get(checkpoint_name)
        if checkpoint:
            start = float(checkpoint)

    if advanced_query:
        if not isinstance(advanced_query, str):
            advanced_query = advanced_query.read()
        query = AlertQuery.parse_raw(advanced_query)
    else:
        if not any([start, on, end]):
            raise BadOptionUsage(
                "start",
                "--start, --end, or --on options are required if not using the --advanced-query option "
                "or using an existing checkpoint.",
            )
        query = _create_query(
            start=start,
            end=end,
            on=on,
            alert_id=alert_id,
            type_=type_,
            name=name,
            actor=actor,
            actor_id=actor_id,
            risk_severity=risk_severity,
            state=state,
            rule_id=rule_id,
            alert_severity=alert_severity,
        )
    alerts_gen = client.alerts.v1.iter_all(query)

    if checkpoint_name:
        alerts_gen = _update_checkpoint(cursor, checkpoint_name, alerts_gen)

    with warn_interrupt() if checkpoint_name else nullcontext():
        if output:
            logger = get_server_logger(output, certs, ignore_cert_validation)
            for alert_ in alerts_gen:
                logger.info(alert_.json())
            return

        if format_ == TableFormat.table:
            columns = columns or [
                "created_at",
                "risk_severity",
                "state",
                "actor",
                "actor_id",
                "name",
                "description",
                "watchlists",
                "state_last_modified_by",
                "state_last_modified_at",
                "id",
            ]
            render.table(AlertSummary, alerts_gen, columns=columns, flat=False)
        elif format_ == TableFormat.csv:
            render.csv(AlertSummary, alerts_gen, columns=columns, flat=True)
        else:
            printed = False
            for alert_ in alerts_gen:
                printed = True
                if format_ == TableFormat.json_pretty:
                    console.print_json(alert_.json())
                else:
                    click.echo(alert_.json())
            if not printed:
                console.print("No results found.")


@alerts.command()
@click.argument("checkpoint-name")
def clear_checkpoint(checkpoint_name: str):
    """Remove the saved alerts checkpoint from searches made with `--checkpoint` mode."""
    client = Client()
    cursor = _get_cursor_store(client.settings.api_client_id)
    cursor.delete(checkpoint_name)


# Future enhancement: add functionality to show human-readable summaries for multiple alerts
@alerts.command(cls=IncydrCommand)
@logging_options
@single_format_option
@click.argument("alert-id")
def show(
    alert_id: str,
    format_: SingleFormat,
):
    """
    Show the details of a single alert.
    """
    client = Client()
    alert = client.alerts.v1.get_details(alert_id)[0]
    if format_ == SingleFormat.rich:
        console.print(Panel.fit(model_as_card(alert)))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(alert.json())
    else:
        click.echo(alert.json())


@alerts.command(cls=IncydrCommand)
@logging_options
@click.argument("alert-id")
@click.argument("note")
def add_note(
    alert_id: str,
    note: str,
):
    """
    Add an optional note to an alert.
    """
    client = Client()
    client.alerts.v1.add_note(alert_id, note)
    console.print("Note added.")


@alerts.command(cls=IncydrCommand)
@logging_options
@click.argument("alert-id")
@click.argument("state")
@click.option(
    "--note",
    default=None,
    help="Optional note to indicate the reason for the state change.",
)
def update_state(
    alert_id: str,
    state: str,
    note: Optional[str],
):
    """
    Change the state of an alert, and optionally add a note.
    """
    client = Client()
    client.alerts.v1.change_state(alert_id, state, note)
    console.print("State changed successfully.")


@alerts.command(cls=IncydrCommand)
@click.argument("file", type=AutoDecodedFile())
@input_format_option
@click.option(
    "--state",
    type=click.Choice(["OPEN", "RESOLVED", "IN_PROGRESS", "PENDING"]),
    help="Override CSV/JSON input's `state` value with this value.",
)
@click.option("--note", help="Override CSV/JSON input's `note` value with this value.")
@logging_options
def bulk_update_state(
    file,
    format_,
    state: str,
    note: str,
):
    """
    Bulk update multiple alerts from a file.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    The --state and --note options to this command will override respective columns/keys in the CSV/JSON input.

    This allows you to bulk change a set of alerts without having manually modify the state/note value for each CSV or
    JSON Lines row in the file. For example, to close all currently "PENDING" alerts older than <DATE>:

        incydr alerts search --end <DATE> --state PENDING --format json-lines | incydr alerts bulk-update-state - --state RESOLVED --note "bulk resolved alerts older than <DATE>"

    If --state is not provided, the CSV/JSON input _must_ have a `state` column/key for each row/object.
    """
    # if --state is provided, we want that column/key to be optional on input data, otherwise required
    state_type = Optional[str] if state else str

    class AlertBulkCSV(CSVModel):
        alert_id: str = Field(csv_aliases=["id", "alert_id"])
        state: state_type = Field(csv_aliases=["state"])
        note: Optional[str]

    class AlertBulkJSON(Model):
        alert_id: str = Field(alias="id")
        state: state_type
        note: Optional[str]

    client = Client()
    if format_ == "csv":
        alerts_ = AlertBulkCSV.parse_csv(file)

    else:
        alerts_ = AlertBulkJSON.parse_json_lines(file)

    # group alerts where state and note are the same, so we can batch API calls
    buckets = bucketize(
        alerts_,
        key=lambda alert: (state or alert.state, note or alert.note),
        value_transform=lambda alert: alert.alert_id,
    )
    for bucket in buckets:
        state_, note_ = bucket
        alert_ids = buckets[bucket]
        # backend allows max of 100 alerts per request
        for chunk in chunked(alert_ids, size=100):
            try:
                client.alerts.v1.change_state(chunk, state_, note_)
                console.print(
                    f"{len(chunk)} alerts successfully set to '{state_}' with note: '{note_}'"
                )
            except requests.HTTPError as err:
                # backend doesn't specify _which_ alert_id doesn't exist, so we need to try them 1 by 1
                if err.response.status_code == 404:
                    console.print(
                        f"[red]Error processing batch of {len(chunk)} alerts, trying individually..."
                    )
                    for id_ in chunk:
                        try:
                            client.alerts.v1.change_state(id_, state_, note_)
                            console.print(
                                f"Successfully set alert_id '{id_}' to '{state_}' with note: '{note_}'"
                            )
                        except requests.HTTPError as err:
                            console.print(
                                f"[red]Error updating alert_id[/red] '{id_}': {err.response.status_code}"
                            )


field_option_map = {
    "alert_id": "AlertId",
    "type_": "Type",
    "name": "Name",
    "actor": "Actor",
    "actor_id": "ActorId",
    "risk_severity": "RiskSeverity",
    "state": "State",
    "rule_id": "RuleId",
    "alert_severity": "AlertSeverity",
}


def _create_query(**kwargs):
    query = AlertQuery(
        start_date=kwargs["start"], end_date=kwargs["end"], on=kwargs["on"]
    )
    for k, v in kwargs.items():
        if v:
            if k in ["start", "end", "on"]:
                continue
            query = query.equals(field_option_map[k], v)
    return query


def _get_cursor_store(api_key):
    """
    Get cursor store for alerts search checkpoints.
    """
    dir_path = get_user_project_path(
        "checkpoints",
        api_key,
        "alert_checkpoints",
    )
    return CursorStore(dir_path, "alerts")


def _update_checkpoint(cursor, checkpoint_name, alerts_gen):
    """
    De-duplicates events across checkpointed runs.

    Since using the timestamp of the last event
    processed as the `--start` time of the next run causes the last event to show up again in the
    next results, store the last alert IDs in the cursor to
    filter out on the next run.

    It's also possible that two events have the exact same timestamp, so
    `checkpoint_alerts` needs to be a list of alert IDs so we can filter out everything that's actually
    been processed.
    """
    checkpoint_alerts = cursor.get_items(checkpoint_name)
    new_timestamp = None
    new_alerts = []
    for alert in alerts_gen:
        alert_id = alert.id
        if alert_id not in checkpoint_alerts:
            if not new_timestamp or alert.created_at > new_timestamp:
                new_timestamp = alert.created_at
                new_alerts.clear()
            new_alerts.append(alert_id)
            yield alert
            new_timestamp.replace(tzinfo=timezone.utc)
            cursor.replace(checkpoint_name, new_timestamp.timestamp())
            cursor.replace_items(checkpoint_name, new_alerts)
