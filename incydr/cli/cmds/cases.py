from pathlib import Path
from typing import Optional

import typer
from requests.exceptions import HTTPError
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from typer import Context
from typer import echo
from typer import Option
from typer import Typer

from incydr._cases.models import CaseDetail
from incydr.cli import console
from incydr.cli import init_incydr_client
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.utils import output_models_format
from incydr.utils import CSVValidationError
from incydr.utils import read_models_from_csv

app = Typer()


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


@app.command()
def create(
    ctx: Context,
    name: str,
    description: str = Option(help="Case description.", default=None),
    subject: str = Option(help="UserID of the subject of the case.", default=None),
    assignee: str = Option(help="UserID of the assignee of the case.", default=None),
    findings: str = Option(
        help="Markdown formatted details of case notes.", default=None
    ),
):
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


@app.command("list")
def list_(
    ctx: Context,
    format_: TableFormat = table_format_option,
    columns: Optional[str] = columns_option,
):
    if not format_:
        format_ = TableFormat.table
    client = ctx.obj()
    cases = client.cases.v1.iter_all()
    output_models_format(cases, "Cases", format_, columns, client.settings.use_rich)


@app.command()
def show(ctx: Context, case_number: int, format_: SingleFormat = single_format_option):
    client = ctx.obj()
    case = client.cases.v1.get_case(case_number)
    if format_ == SingleFormat.rich and client.settings.use_rich:
        render_case(case)

    elif format_ == SingleFormat.json:
        console.print_json(case.json())

    else:
        echo(case.json())


@app.command()
def bulk_update(ctx: Context, csv: Path):
    client = ctx.obj()
    try:
        for case in track(
            read_models_from_csv(CaseDetail, csv),
            description="Updating cases...",
            transient=True,
        ):
            client.cases.v1.update(case)
    except CSVValidationError as err:
        console.print(f"[red]Error:[/red] {err.msg}")
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


# TODO: convert to click commands

cases = typer.main.get_command(app)

if __name__ == "__main__":
    app.callback()(init_incydr_client)
    app()
