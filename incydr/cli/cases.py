import typing
from requests.exceptions import HTTPError
from typer import Context
from typer import Option
from typer import Typer
from typer import echo
from incydr.cli import init_incydr_client, console
from incydr.cli.options import format_option
from incydr.cli.options import Format
from incydr.cli.options import columns_option
from incydr.models import Case
from rich.table import Table
from rich.markdown import Markdown
from rich import print
from csv import DictWriter
import sys

app = Typer()


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
    try:
        case = ctx.obj().cases.v1.create(
            name,
            subject=subject,
            assignee=assignee,
            findings=findings,
            description=description,
        )
        print(case)
    except HTTPError as err:
        print(err.response.text)


@app.command("list")
def list_(
    ctx: Context,
    format_: Format = format_option,
    columns: str = columns_option,
):
    if columns:
        columns = columns.split(",")

    with console.status("Working..."):
        cases = ctx.obj().cases.v1.iter_all()
        if format_ == Format.table:
            table = Table(*Case.__table_header__(columns=columns), title="Cases")
            for case in cases:
                table.add_row(*case.__table_row__(columns=columns))
            console.print(table)
        if format_ == Format.csv:
            writer = DictWriter(sys.stdout, fieldnames=Case.__fields__)
            for case in cases:
                writer.writerow(case.dict(by_alias=False))

        if format_ == Format.json:
            for case in cases:
                console.print_json(case.json(include=set(columns)))
        if format_ == Format.raw_json:
            for case in cases:
                echo(case.json())


@app.command()
def show(ctx: Context, case_number: int):
    case = ctx.obj().cases.v1.get_case(case_number)
    from rich.panel import Panel

    print(Panel(Markdown(case.findings), expand=False))


if __name__ == "__main__":
    app.callback()(init_incydr_client)
    app()
