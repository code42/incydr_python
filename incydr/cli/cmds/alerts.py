from typing import Optional

import click
from click import BadOptionUsage
from click import Context
from rich.panel import Panel
from rich.progress import track

from incydr._alerts.models.alert import AlertSummary
from incydr._queries.alerts import AlertQuery
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.alert_filter_options import advanced_query_option
from incydr.cli.cmds.options.alert_filter_options import filter_options
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import output_options
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.utils import output_format_logger
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import model_as_card
from incydr.utils import read_dict_from_csv


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def alerts(ctx, log_level, log_file):
    """View and manage alerts."""
    init_client(ctx, log_level, log_file)


@alerts.command(cls=IncydrCommand)
@click.pass_context
@columns_option
@table_format_option
@output_options
@advanced_query_option
@filter_options
def search(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
    output: Optional[str],
    certs: Optional[str],
    ignore_cert_validation: Optional[bool],
    advanced_query: Optional[str],
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
):
    """
    Search alerts.
    """
    if advanced_query:
        query = AlertQuery.parse_raw(advanced_query)
    else:
        if not any([start, on]):
            raise BadOptionUsage(
                "start",
                "--start or --on options are required if not using the --advanced-query option.",
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

    client = ctx.obj()
    alert_summaries = client.alerts.v1.iter_all(query)

    if output:
        output_format_logger(
            (a.dict() for a in alert_summaries),
            output,
            columns,
            certs,
            ignore_cert_validation,
        )
        return
    if format_ == TableFormat.table:
        if not columns:
            columns = [
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
        render.table(AlertSummary, alert_summaries, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(AlertSummary, alert_summaries, columns=columns, flat=True)
    elif format_ == TableFormat.json:
        for alert in alert_summaries:
            console.print_json(alert.json())
    else:
        for alert in alert_summaries:
            console.print(alert.json(), highlight=False)


# Future enhancement: add functionality to show human-readable summaries for multiple alerts
@alerts.command(cls=IncydrCommand)
@click.pass_context
@single_format_option
@click.argument("alert-id")
def show(ctx: Context, alert_id: str, format_: SingleFormat):
    """
    Show the details of a single alert.
    """
    client = ctx.obj()
    alert = client.alerts.v1.get_details(alert_id)[0]
    if format_ == SingleFormat.rich:
        console.print(Panel.fit(model_as_card(alert)))
    elif format_ == SingleFormat.json:
        console.print_json(alert.json())
    else:
        console.print(alert.json(), highlight=False)


@alerts.command(cls=IncydrCommand)
@click.pass_context
@click.argument("alert-id")
@click.argument("note")
def add_note(ctx: Context, alert_id: str, note: str):
    """
    Add an optional note to an alert.
    """
    client = ctx.obj()
    client.alerts.v1.add_note(alert_id, note)
    console.print("Note added.")


@alerts.command(cls=IncydrCommand)
@click.pass_context
@click.argument("alert-ids")
@click.argument("state")
@click.option(
    "--note",
    default=None,
    help="Optional note to indicate the reason for the state change.",
)
@click.option(
    "--csv", is_flag=True, default=False, help="alert IDs are specified in a CSV file."
)
def update_state(
    ctx: Context, alert_ids: str, state: str, note: str = None, csv: bool = False
):
    """
    Update multiple alerts to the same state.

    Changes the state of all alerts specified in `ALERT-IDS` to the indicated `STATE`,
    where `STATE` is one of `OPEN`, `RESOLVED`, `IN_PROGRESS` or `PENDING`

    `ALERT-IDS` is a comma-delimited list of alert IDs.

        alerts update-state ALERT_IDS STATE

    To read alert event IDs from a csv (single column, no header),
    pass the path to a csv along with the --csv flag:

        alerts update-state CSV_PATH STATE --csv

    """
    alert_ids = _parse_alert_ids(alert_ids, csv)
    client = ctx.obj()
    client.alerts.v1.change_state(alert_ids, state, note)
    console.print("State changed.")


@alerts.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
def bulk_update_state(ctx: Context, csv: str):
    """
    Bulk update multiple alerts to different states using a CSV file.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires an `alert_id` column to identify the alerts by its ID.

    Valid CSV columns include:

    * `alert_id` (REQUIRED) - Alert ID.
    * `state` (REQUIRED) - Updated alert state. One of OPEN, RESOLVED, IN_PROGRESS or PENDING.
    * `note` - Brief optional note to indicate the reason for the state change.
    """
    client = ctx.obj()
    for row in track(
        read_dict_from_csv(csv), description="Updating cases...", transient=True
    ):
        note = row.get("note")
        client.alerts.v1.change_state(row["alert_id"], row["state"], note)


def _parse_alert_ids(alert_ids, csv):
    if csv:
        ids = []
        for row in track(
            read_dict_from_csv(alert_ids, field_names=["alert_id"]),
            description="Reading alert IDs...",
            transient=True,
        ):
            ids.append(row["alert_id"])
    else:
        ids = [e.strip() for e in alert_ids.split(",")]
    return ids


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
