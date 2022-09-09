import typer

from incydr.cli import cases
from incydr.cli import init_incydr_client

incydr = typer.Typer()
incydr.callback()(init_incydr_client)

incydr.add_typer(cases.app, name="cases")

if __name__ == "__main__":
    incydr()
