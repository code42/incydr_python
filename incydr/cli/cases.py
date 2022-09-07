from typing import Optional

from requests.exceptions import HTTPError
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from typer import Context
from typer import Option
from typer import Typer
from typer import echo

import incydr.cli.render as render
from incydr._cases.models import CaseDetail
from incydr.cli import console
from incydr.cli import init_incydr_client
from incydr.cli.options import SingleFormat
from incydr.cli.options import TableFormat
from incydr.cli.options import columns_option
from incydr.cli.options import single_format_option
from incydr.cli.options import table_format_option

app = Typer()


def render_case(case: CaseDetail):
    field_table = Table.grid(padding=(0, 1), expand=False)
    field_table.title = f"Case {case.number}"
    for name, field in case.__fields__.items():
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
    client = ctx.obj()
    cases = client.cases.v1.iter_all()

    if format_ == TableFormat.table and client.settings.use_rich:
        with console.pager():
            render.table(cases, columns=columns, title="Cases")

    if format_ == TableFormat.csv:
        render.csv(cases, columns=columns)

    if format_ == TableFormat.json:
        for case in cases:
            console.print_json(case.json(include=columns))

    else:
        for case in cases:
            echo(case.json(include=columns))


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


if __name__ == "__main__":
    app.callback()(init_incydr_client)
    app()
