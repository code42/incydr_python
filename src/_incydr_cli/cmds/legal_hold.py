from typing import Optional

import click
from rich.panel import Panel

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.legal_hold.models import Custodian
from _incydr_sdk.legal_hold.models import CustodianMatter
from _incydr_sdk.legal_hold.models import LegalHoldPolicy
from _incydr_sdk.legal_hold.models import Matter
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def legal_hold():
    """View and manage legal holds."""


@legal_hold.command("list-matters-for-user", cls=IncydrCommand)
@click.argument("user-id")
@table_format_option
@columns_option
@logging_options
def list_matters_for_user(user_id: str, format_: TableFormat, columns: Optional[str]):
    """List the matter memberships for a specific user."""
    client = Client()
    memberships_ = client.legal_hold.v1.iter_all_memberships_for_user(user_id=user_id)

    if format_ == TableFormat.csv:
        render.csv(CustodianMatter, memberships_, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(CustodianMatter, memberships_, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in memberships_:
            console.print_json(item.json())
    else:
        for item in memberships_:
            click.echo(item.json())


@legal_hold.command("list-custodians", cls=IncydrCommand)
@click.argument("matter-id")
@table_format_option
@columns_option
@logging_options
def list_custodians(matter_id: str, format_: TableFormat, columns: Optional[str]):
    """List the custodians for a specific matter."""
    client = Client()
    memberships_ = client.legal_hold.v1.iter_all_custodians(matter_id=matter_id)

    if format_ == TableFormat.csv:
        render.csv(Custodian, memberships_, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(Custodian, memberships_, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in memberships_:
            console.print_json(item.json())
    else:
        for item in memberships_:
            click.echo(item.json())


@legal_hold.command("add-custodian", cls=IncydrCommand)
@click.option("--user-id", required=True, default=None, help="The user ID to add.")
@click.option(
    "--matter-id",
    required=True,
    default=None,
    help="The matter ID to which the user will be added",
)
@single_format_option
@logging_options
def add_custodian(user_id: str, matter_id: str, format_: SingleFormat):
    """Add a custodian to a matter."""
    client = Client()
    result = client.legal_hold.v1.add_custodian(user_id=user_id, matter_id=matter_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(
            Panel.fit(
                model_as_card(result), title=f"Membership: {result.custodian.username}"
            )
        )
    elif format_ == SingleFormat.json_pretty:
        console.print_json(result.json())
    else:
        click.echo(result.json())


@legal_hold.command("remove-custodian", cls=IncydrCommand)
@click.option("--user-id", required=True, default=None, help="The user ID to remove.")
@click.option(
    "--matter-id",
    required=True,
    default=None,
    help="The matter ID from which the user will be removed",
)
@logging_options
def remove_custodian(
    user_id: str,
    matter_id: str,
):
    """Remove custodian from a matter."""
    client = Client()
    client.legal_hold.v1.remove_custodian(user_id=user_id, matter_id=matter_id)
    console.log(f"User {user_id} removed successfully from matter {matter_id}.")


@legal_hold.command("list-matters", cls=IncydrCommand)
@click.option(
    "--creator-user-id",
    default=None,
    help="Find legal hold matters that were created by the user with this unique identifier.",
)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive matters. Defaults to returning both when when neither option is passed.",
)
@click.option(
    "--name",
    default=None,
    help="Find legal hold matters whose 'name' either equals or partially contains this value.",
)
@table_format_option
@columns_option
@logging_options
def list_matters(
    creator_user_id: Optional[str],
    active: Optional[bool],
    name: Optional[str],
    format_: TableFormat,
    columns: Optional[str],
):
    """List all matters."""
    client = Client()
    result = client.legal_hold.v1.iter_all_matters(
        creator_user_id=creator_user_id, active=active, name=name
    )

    if format_ == TableFormat.csv:
        render.csv(Matter, result, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(Matter, result, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in result:
            console.print_json(item.json())
    else:
        for item in result:
            click.echo(item.json())


@legal_hold.command("create-matter", cls=IncydrCommand)
@click.option(
    "--policy-id",
    required=True,
    default=None,
    help="The policy ID to be used by the created matter. Required.",
)
@click.option(
    "--name",
    required=True,
    default=None,
    help="The name of the matter to be created. Required.",
)
@click.option(
    "--description", default=None, help="The description of the matter to be created."
)
@click.option("--notes", default=None, help="The notes for the matter to be created.")
@single_format_option
@logging_options
def create_matter(
    policy_id: str,
    name: str,
    description: Optional[str],
    notes: Optional[str],
    format_: SingleFormat,
):
    """Create a matter."""
    client = Client()
    result = client.legal_hold.v1.create_matter(
        policy_id=policy_id, name=name, description=description, notes=notes
    )

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(result), title=f"Matter: {result.name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(result.json())
    else:
        click.echo(result.json())


@legal_hold.command("deactivate-matter", cls=IncydrCommand)
@click.argument("matter-id")
@logging_options
def deactivate_matter(matter_id: str):
    """Deactivate a matter."""
    client = Client()
    client.legal_hold.v1.deactivate_matter(matter_id=matter_id)
    console.log(f"Successfully deactivated {matter_id}")


@legal_hold.command("reactivate-matter", cls=IncydrCommand)
@click.argument("matter-id")
@logging_options
def reactivate_matter(matter_id: str):
    """Reactivate a matter."""
    client = Client()
    client.legal_hold.v1.reactivate_matter(matter_id=matter_id)
    console.log(f"Successfully reactivated {matter_id}")


@legal_hold.command("show-matter", cls=IncydrCommand)
@click.argument("matter-id")
@single_format_option
@logging_options
def show_matter(matter_id: str, format_: SingleFormat):
    """Show details for a matter."""
    client = Client()
    result = client.legal_hold.v1.get_matter(matter_id=matter_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(result), title=f"Matter: {result.name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(result.json())
    else:
        click.echo(result.json())


@legal_hold.command("list-policies", cls=IncydrCommand)
@table_format_option
@columns_option
@logging_options
def list_policies(format_: TableFormat, columns: Optional[str]):
    client = Client()
    result = client.legal_hold.v1.iter_all_policies()

    if format_ == TableFormat.csv:
        render.csv(LegalHoldPolicy, result, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(LegalHoldPolicy, result, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in result:
            console.print_json(item.json())
    else:
        for item in result:
            click.echo(item.json())


@legal_hold.command("show-policy", cls=IncydrCommand)
@click.argument("policy-id")
@single_format_option
@logging_options
def show_policy(policy_id: str, format_: SingleFormat):
    client = Client()
    result = client.legal_hold.v1.get_policy(policy_id=policy_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(result), title=f"Policy: {result.name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(result.json())
    else:
        click.echo(result.json())
