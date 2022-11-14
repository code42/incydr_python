import os
from pathlib import Path
from typing import Optional
from typing import Union

import click
from requests.exceptions import HTTPError
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from typer import Context
from typer import echo
from typer import Typer

from incydr._cases.models import CaseDetail
from incydr._cases.models import UpdateCaseRequest
from incydr._file_events.models.event import FileEventV2
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.options.utils import user_lookup_callback
from incydr.cli.cmds.utils import output_models_format
from incydr.cli.cmds.utils import output_response_format
from incydr.cli.cmds.utils import output_single_format
from incydr.cli.cmds.utils import user_lookup
from incydr.cli.core import incompatible_with
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import CSVValidationError
from incydr.utils import read_dict_from_csv
from incydr.utils import read_models_from_csv

app = Typer()


path_option = click.option(
    "--path",
    help="The file path where to save the file. Defaults to the current directory.",
    default=os.getcwd(),
)


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def cases(ctx, log_level, log_file):
    """View and manage cases."""
    init_client(ctx, log_level, log_file)


def render_case(case: CaseDetail):
    field_table = Table.grid(padding=(0, 1), expand=False)
    field_table.title = f"Case {case.number}"
    for name, _field in case.__fields__.items():
        if name == "number":
            continue
        if name == "findings" and case.findings is not None:
            field_table.add_row(
                Panel(
                    Markdown(case.findings, justify="left"),
                    title="Findings",
                    width=80,
                )
            )
        else:
            field_table.add_row(f"{name} = {getattr(case, name)}")
    console.print(Panel.fit(field_table))


def render_file_event(event: FileEventV2):
    field_table = Table.grid(padding=(0, 1), expand=False)
    field_table.title = f"File Event {event.event.id}"
    event_dict = event.dict()
    for name, _field in event_dict.items():
        if name == "event.id":
            continue
        field_table.add_row(f"{name} = {event_dict[name]}")
    console.print(Panel.fit(field_table))


@cases.command(cls=IncydrCommand)
@click.argument("name")
@click.option("--description", help="Case description.", default=None)
@click.option(
    "--subject",
    help="User of the subject of the case.  Takes a user ID or a username.  Performs an additional lookup if username is passed.",
    default=None,
    callback=user_lookup_callback,
)
@click.option(
    "--assignee",
    help="User of the assignee of the case. Takes a user ID or a username.  Performs an additional lookup if username is passed.",
    default=None,
    callback=user_lookup_callback,
)
@click.option(
    "--findings", help="Markdown formatted details of case notes.", default=None
)
@click.pass_context
def create(
    ctx: Context,
    name: str,
    description: str,
    subject: str,
    assignee: str,
    findings: str,
):
    """
    Create a case.
    """
    client = ctx.obj()
    try:
        case = client.cases.v1.create(
            name,
            subject=subject,
            assignee=assignee,
            findings=findings,
            description=description,
        )
        if client.settings.use_rich:
            render_case(case)
        else:
            echo(case.json())
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@click.pass_context
def delete(
    ctx: Context,
    case_number: int,
):
    """
    Delete a case.
    """
    client = ctx.obj()
    client.cases.v1.delete(case_number)


@cases.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@click.pass_context
def list_(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List all cases.
    """
    if not format_:
        format_ = TableFormat.table
    client = ctx.obj()
    cases = client.cases.v1.iter_all()
    output_models_format(cases, "Cases", format_, columns, client.settings.use_rich)


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@single_format_option
@click.pass_context
def show(ctx: Context, case_number: int, format_: SingleFormat):
    """
    Show details for a single case.
    """
    client = ctx.obj()
    case = client.cases.v1.get_case(case_number)
    output_single_format(case, render_case, format_, client.settings.use_rich)


@cases.command(cls=IncydrCommand)
@click.argument("case_number")
@click.option(
    "--assignee",
    default=None,
    help="The administrator assigned to the case. Takes a user ID or a username.  Performs an additional lookup if username is passed.",
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
    help="The case subject. Takes a user ID or a username.  Performs an additional lookup if username is passed.",
    callback=user_lookup_callback,
)
@click.pass_context
def update(
    ctx: Context,
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

    client = ctx.obj()
    data = UpdateCaseRequest(
        assignee=assignee,
        description=description,
        findings=findings,
        name=name,
        status=status,
        subject=subject,
    )
    client.session.put(f"/v1/cases/{case_number}", json=data.dict())


@cases.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
def bulk_update(ctx: Context, csv: Path):
    """
    Bulk update cases using a `.csv` file.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires a `number` column to identify the case by its `case_number`.

    Valid CSV columns that correspond to mutable case fields include:

    * `number` (REQUIRED) - Case number.
    * `assignee` - User ID or username of the administrator assigned to the case. Performs an additional lookup if username is passed.
    * `description` - Brief optional description.
    * `findings` - Markdown formatted text summarizing the findings for a case.
    * `name` - Case name.
    * `status` - Case status. One of `ARCHIVED`, `CLOSED` or `OPEN`.
    * `subject` - User ID or username of the case subject. Performs an additional lookup if username is passed.

    """
    client = ctx.obj()
    username_cache = {}
    try:
        for case in track(
            read_models_from_csv(CaseDetail, csv),
            description="Updating cases...",
            transient=True,
        ):
            if case.assignee:
                if "@" in case.assignee:
                    try:
                        case.assignee = username_cache[case.assignee]
                    except KeyError:
                        username_cache[case.assignee] = user_lookup(
                            client, case.assignee
                        )
                        case.assignee = username_cache[case.assignee]
            if case.subject:
                if "@" in case.subject:
                    try:
                        case.subject = username_cache[case.subject]
                    except KeyError:
                        username_cache[case.subject] = user_lookup(client, case.subject)
                        case.subject = username_cache[case.subject]
            client.cases.v1.update(case)
    except CSVValidationError as err:
        console.print(f"[red]Error:[/red] {err.msg}")
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
@click.pass_context
def download(
    ctx: Context,
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
    client = ctx.obj()

    # download source file for specific event
    if source_file:
        client.cases.v1.download_file_for_event(case_number, source_file, path)
        return

    flags = [summary, events, source_files]

    # if only only summary or only file-events flag is passed
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


@cases.group(cls=IncydrGroup)
def file_events():
    """View and update file events associated with a case."""
    pass


@file_events.command("show", cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_id")
@single_format_option
@click.pass_context
def show_file_event(
    ctx: Context, case_number: int, event_id: str, format_: SingleFormat
):
    """
    Show details for a file event attached to a case.
    """
    client = ctx.obj()
    event = client.cases.v1.get_file_event_detail(case_number, event_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        render_file_event(event)

    elif format_ == SingleFormat.json:
        console.print_json(event.json())

    else:
        echo(event.json())


@file_events.command("list", cls=IncydrCommand)
@click.argument("case_number")
@table_format_option
@columns_option
@click.pass_context
def list_file_events(
    ctx: Context, case_number: int, format_: TableFormat, columns: str
):
    """
    List file events attached to a case.
    """
    client = ctx.obj()
    events = client.cases.v1.get_file_events(case_number).dict()["events"]

    output_response_format(
        events,
        f"Case {case_number}: File Events",
        format_,
        columns,
        client.settings.use_rich,
    )


csv_option = click.option(
    "--csv", is_flag=True, default=False, help="event IDs are specified in a CSV file."
)


@file_events.command(cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_ids")
@csv_option
@click.pass_context
def add(ctx: Context, case_number: int, event_ids: Union[str, Path], csv: bool):
    """
    Attach file events to a case specified by CASE_NUMBER.

    EVENT_IDS is a comma-delimited string of event IDs to add to the case:

        add CASE_NUMBER EVENT_IDS

    To read the event IDs from a csv (single 'event_id' column),
    pass the path to a csv along with the --csv flag:

        add CASE_NUMBER CSV_PATH --csv
    """
    client = ctx.obj()
    client.cases.v1.add_file_events_to_case(
        case_number, _parse_event_ids(event_ids, csv)
    )


@file_events.command(cls=IncydrCommand)
@click.argument("case_number")
@click.argument("event_ids")
@csv_option
@click.pass_context
def remove(ctx: Context, case_number: int, event_ids: str, csv: bool):
    """
    Remove file events from a case specified by CASE_NUMBER.

    EVENT_IDS is a comma-delimited string of event IDs to add to the case:

        add CASE_NUMBER EVENT_IDSs

    To read the event IDs from a csv (single 'event_id' column),
    pass the path to a csv along with the --csv flag:

        add CASE_NUMBER CSV_PATH --csv
    """
    client = ctx.obj()
    ids = _parse_event_ids(event_ids, csv)
    for id_ in ids:
        client.cases.v1.delete_file_event_from_case(case_number, id_)


def _parse_event_ids(event_ids, csv):
    if csv:
        ids = []
        for row in track(
            read_dict_from_csv(event_ids),
            description="Reading event IDs...",
            transient=True,
        ):
            ids.append(row["event_id"])
    else:
        ids = [e.strip() for e in event_ids.split(",")]
    return ids


if __name__ == "__main__":
    cases()
