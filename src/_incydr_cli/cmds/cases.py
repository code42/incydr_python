import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import click
from pydantic import Field
from pydantic import root_validator
from requests.exceptions import HTTPError
from rich.panel import Panel
from rich.progress import track

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import input_format_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cmds.options.utils import user_lookup_callback
from _incydr_cli.cmds.utils import user_lookup
from _incydr_cli.core import incompatible_with
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_cli.file_readers import FileOrString
from _incydr_sdk.cases.models import Case
from _incydr_sdk.cases.models import CaseDetail
from _incydr_sdk.cases.models import FileEvent
from _incydr_sdk.core.client import Client
from _incydr_sdk.core.models import CSVModel
from _incydr_sdk.file_events.models.event import FileEventV2
from _incydr_sdk.utils import model_as_card


class UpdateCaseCSV(CSVModel):
    number: str = Field(csv_aliases=["number", "case_number"])
    assignee: Optional[str]
    description: Optional[str]
    findings: Optional[str]
    name: Optional[str]
    status: Optional[str]
    subject: Optional[str]


class FileEventCSV(CSVModel):
    event_id: str = Field(csv_aliases=["event_id", "eventId"])


class FileEventJSON(FileEventV2):
    event_id: str = Field(alias="eventId")

    @root_validator(pre=True)
    def _event_id_required(cls, values):  # noqa
        # check if input is V2 file event
        event = values.get("event")
        if event and event.get("id"):
            values["event_id"] = event["id"]
        return values


path_option = click.option(
    "--path",
    help="The file path where to save the file. Defaults to the current directory.",
    default=os.getcwd(),
)


@click.group(cls=IncydrGroup)
@logging_options
def cases():
    """View and manage cases."""


@cases.command(cls=IncydrCommand)
@click.argument("name")
@click.option("--description", help="Case description.", default=None)
@click.option(
    "--subject",
    help="User of the subject of the case.  Takes a user ID or a username.  Performs an additional lookup if a username is passed.",
    default=None,
    callback=user_lookup_callback,
)
@click.option(
    "--assignee",
    help="User of the assignee of the case. Takes a user ID or a username.  Performs an additional lookup if a username is passed.",
    default=None,
    callback=user_lookup_callback,
)
@click.option(
    "--findings", help="Markdown formatted details of case notes.", default=None
)
@logging_options
def create(
    name: str,
    description: str,
    subject: str,
    assignee: str,
    findings: str,
):
    """
    Create a case.
    """
    client = Client()
    try:
        case = client.cases.v1.create(
            name,
            subject=subject,
            assignee=assignee,
            findings=findings,
            description=description,
        )
        if client.settings.use_rich:
            console.print(Panel.fit(model_as_card(case), title="Case"))
        else:
            console.print(case.json(), highlight=False)
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@logging_options
def delete(case_number: int):
    """
    Delete a case.
    """
    client = Client()
    client.cases.v1.delete(case_number)
    console.print(f"Case number '{case_number}' successfully deleted.")


@cases.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@logging_options
def list_(
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List all cases.
    """
    client = Client()
    cases_ = client.cases.v1.iter_all()

    if format_ == TableFormat.table:
        render.table(Case, cases_, columns=columns)
    elif format_ == TableFormat.csv:
        render.csv(Case, cases_, columns=columns)
    elif format_ == TableFormat.json_pretty:
        for case in cases_:
            console.print_json(case.json())
    else:
        for case in cases_:
            click.echo(case.json())


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@single_format_option
@logging_options
def show(
    case_number: int,
    format_: SingleFormat,
):
    """
    Show details for a single case.
    """
    client = Client()
    case = client.cases.v1.get_case(case_number)
    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(case), title="Case", width=120))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(case.json())
    else:
        click.echo(case.json())


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@click.option(
    "--assignee",
    default=None,
    help="The administrator assigned to the case. Takes a user ID or a username.  Performs an additional lookup if a username is passed.",
    callback=user_lookup_callback,
)
@click.option("--description", default=None, help="Brief optional description.")
@click.option(
    "--findings",
    default=None,
    help="Markdown formatted text summarizing the findings for a case.",
)
@click.option("--name", default=None, help="Case name.")
@click.option(
    "--status", default=None, help="Case status. One of `ARCHIVED`, `CLOSED` or `OPEN`."
)
@click.option(
    "--subject",
    default=None,
    help="The case subject. Takes a user ID or a username.  Performs an additional lookup if a username is passed.",
    callback=user_lookup_callback,
)
@logging_options
def update(
    case_number: str,
    assignee: Optional[str] = None,
    description: Optional[str] = None,
    findings: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    subject: Optional[str] = None,
):
    """
    Update a single case. Pass the updated value for a field to the corresponding command option.
    """
    if not any([assignee, description, findings, name, status, subject]):
        raise click.UsageError(
            "At least one command option must be provided to update a case.  Use `cases update --help` to see available options."
        )

    client = Client()
    case = client.cases.v1.get_case(case_number)
    if assignee:
        case.assignee = assignee
    if description:
        case.description = description
    if findings:
        case.findings = findings
    if name:
        case.name = name
    if status:
        case.status = status
    if subject:
        case.subject = subject
    updated_case = client.cases.v1.update(case)
    if client.settings.use_rich:
        console.print(Panel.fit(model_as_card(updated_case), title="Updated Case"))
    else:
        console.print(updated_case.json(), highlight=False)


@cases.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_update(
    file: Path,
    format_: str,
):
    """
    Bulk update cases from a file.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Valid CSV columns that correspond to update-able case fields include:

    * `number` (REQUIRED) - Case number.
    * `assignee` - User ID or username of the administrator assigned to the case. Performs an additional lookup if a username is passed.
    * `description` - Brief optional description.
    * `findings` - Markdown formatted text summarizing the findings for a case.
    * `name` - Case name.
    * `status` - Case status. One of `ARCHIVED`, `CLOSED` or `OPEN`.
    * `subject` - User ID or username of the case subject. Performs an additional lookup if a username is passed.
    """
    client = Client()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UpdateCaseCSV.parse_csv(file)
    else:
        models = CaseDetail.parse_json_lines(file)
    try:
        for updated in track(models, description="Updating cases...", transient=True):
            fields_set = updated.__fields_set__
            case = client.cases.v1.get_case(updated.number)
            if "assignee" in fields_set and case.assignee != updated.assignee:
                case.assignee = resolve_username(updated.assignee)
            if "subject" in fields_set and case.subject != updated.subject:
                case.subject = resolve_username(updated.subject)
            if "description" in fields_set:
                case.description = updated.description
            if "findings" in fields_set:
                case.findings = updated.findings
            if "name" in fields_set:
                case.name = updated.name
            if "status" in fields_set:
                case.status = updated.status
            client.cases.v1.update(case)
    except ValueError as err:
        console.print(f"[red]Error:[/red] {err}")
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@path_option
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Download a case summary in PDF format.",
)
@click.option(
    "--file-events",
    "events",
    is_flag=True,
    default=False,
    help="Download all file event data for a case in CSV format.",
)
@click.option(
    "--source-files",
    is_flag=True,
    default=False,
    help="Download the source files for file events associated with a case.",
)
@click.option(
    "--source-file",
    default=None,
    help="Download a source file for a specific event. Takes the event ID. Incompatible with other download options.",
    cls=incompatible_with(["summary", "file_events", "source_files"]),
)
@logging_options
def download(
    case_number: int,
    path: str,
    summary: bool = None,
    events: bool = None,
    source_files: bool = None,
    source_file: str = None,
):
    """
    Download one or more files related to a case to the specified target folder.

    Defaults to downloading all files if no options are passed.

    If more than one file is specified the download will be in ZIP format.
    """
    client = Client()

    # download source file for specific event
    if source_file:
        client.cases.v1.download_file_for_event(case_number, source_file, path)
        return

    flags = [summary, events, source_files]

    # if only summary or only file-events flag is passed
    if sum(bool(flag) for flag in flags) == 1:
        if summary:
            client.cases.v1.download_summary_pdf(case_number, path)
            return
        if events:
            client.cases.v1.download_file_event_csv(case_number, path)
            return

    # Default to downloading all files if no flags are passed
    if not any(flags):
        summary = True
        events = True
        source_files = True

    client.cases.v1.download_full_case_zip(
        case_number,
        path,
        include_files=source_files,
        include_summary=summary,
        include_file_events=events,
    )
    console.print(f"Case file(s) downloaded to '{path}'")


@cases.group(cls=IncydrGroup)
def file_events():
    """View and update file events associated with a case."""


@file_events.command("show", cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_id")
@single_format_option
@logging_options
def show_file_event(
    case_number: int,
    event_id: str,
    format_: SingleFormat,
):
    """
    Show details for a file event attached to a case.
    """
    client = Client()
    event = client.cases.v1.get_file_event_detail(case_number, event_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(event)))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(event.json())
    else:
        click.echo(event.json())


@file_events.command("list", cls=IncydrCommand)
@click.argument("case_number")
@table_format_option
@columns_option
@logging_options
def list_file_events(
    case_number: int,
    format_: TableFormat,
    columns: str,
):
    """
    List file events attached to a case.
    """
    client = Client()
    response = client.cases.v1.get_file_events(case_number)

    if format_ == TableFormat.table:
        columns = columns or [
            "event_timestamp",
            "file_name",
            "file_path",
            "file_availability",
            "risk_indicators",
            "risk_score",
            "event_id",
        ]
        render.table(
            FileEvent,
            response.events,
            title=f"Case {case_number}: File Events",
            columns=columns,
        )
    elif format_ == TableFormat.csv:
        render.csv(FileEvent, response.events, columns=columns)

    else:
        printed = False
        if format_ == TableFormat.json_pretty:
            for event in response.events:
                printed = True
                console.print_json(event.json())

        else:
            for event in response.events:
                printed = True
                click.echo(event.json())
        if not printed:
            console.print("No results found.")


csv_option = click.option(
    "--csv", is_flag=True, default=False, help="event IDs are specified in a CSV file."
)


@file_events.command(cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_ids", type=FileOrString())
@click.option(
    "--format", "-f", "format_", type=click.Choice(["csv", "json-lines"]), default="csv"
)
@logging_options
def add(
    case_number: int,
    event_ids: FileOrString,
    format_: str,
):
    """
    Attach file events to a case specified by CASE_NUMBER.

    EVENT_IDS can be either a comma-delimited string of event IDs:

        add CASE_NUMBER "id-1,id-2,id-3,..."

    Or a CSV or [JSON Lines](https://jsonlines.org) formatted file:

        add CASE_NUMBER @path_to_csv --format csv

        add CASE_NUMBER @path_to_json --format json-lines

    CSV format requires a header row and a column with name matching either "event_id" or "eventId".

    Input can also be parsed from stdin using "-" as the command argument, so you can add events
    directly from an `incydr file-events search` command to a case:

        incydr file-events search SEARCH_OPTIONS --format json-lines | incydr cases add CASE_NUMBER --format json-lines -

    """
    client = Client()
    if isinstance(event_ids, str):
        event_ids = [e.strip() for e in event_ids.split(",")]
    elif format_ == "csv":
        events = FileEventCSV.parse_csv(event_ids)
        event_ids = [e.event_id for e in events]
    else:
        events = FileEventJSON.parse_json_lines(event_ids)
        event_ids = [e.event_id for e in events]

    client.cases.v1.add_file_events_to_case(case_number, event_ids)
    console.print(f"{len(event_ids)} events added to case {case_number}")


@file_events.command(cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_ids", type=FileOrString())
@input_format_option
@click.option(
    "--format", "-f", "format_", type=click.Choice(["csv", "json-lines"]), default="csv"
)
@logging_options
def remove(
    case_number: int,
    event_ids: str,
    format_: str,
):
    """
    Remove file events from a case specified by CASE_NUMBER.

    EVENT_IDS can be either a comma-delimited string of event IDs:

        remove CASE_NUMBER "id-1,id-2,id-3,..."

    Or a CSV or [JSON Lines](https://jsonlines.org) formatted file:

        remove CASE_NUMBER @path_to_csv --format csv

        remove CASE_NUMBER @path_to_json --format json-lines

    CSV format requires a header row and a column with name matching either "event_id" or "eventId".

    Input can also be parsed from stdin using "-" as the command argument, so you can remove all events from a case
    by sending the output of `cases file-events list` command into `cases file-events remove`:

        incydr cases file-events list CASE_NUMBER --format json-lines | incydr cases remove CASE_NUMBER --format json-lines -

    """
    client = Client()
    if isinstance(event_ids, str):
        event_ids = [e.strip() for e in event_ids.split(",")]
    elif format_ == "csv":
        events = FileEventCSV.parse_csv(event_ids)
        event_ids = [e.event_id for e in events]
    else:
        events = FileEventJSON.parse_json_lines(event_ids)
        event_ids = [e.event_id for e in events]

    for id_ in event_ids:
        try:
            client.cases.v1.delete_file_event_from_case(case_number, id_)
            console.print(f"Event removed: {id_}", highlight=False)
        except HTTPError as err:
            if err.response.status_code == 404:
                console.print(f"Event not found on case: {id_}", highlight=False)
            else:
                console.print(
                    f"[red]Error removing event:[/red] {id_} ({err.response.status_code})",
                    highlight=False,
                )


if __name__ == "__main__":
    cases()
