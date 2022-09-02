from typing import Union
import typer
from rich import print
from incydr._core.client import Client

app = typer.Typer()


@app.callback()
def main(ctx: typer.Context, log: str = 40):
    ctx.obj = Client(log_level=log, use_rich=False)


@app.command()
def test(ctx: typer.Context):
    print(ctx.obj.cases.v1.get_case(21))
