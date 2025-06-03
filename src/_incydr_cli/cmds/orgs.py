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
from _incydr_sdk.orgs.models import Org
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def orgs():
    """View and manage orgs."""


@orgs.command("activate", cls=IncydrCommand)
@click.argument("org_guid")
@logging_options
def activate_org(org_guid: str):
    """
    Activate the given org.
    """
    client = Client()
    client.orgs.v1.activate(org_guid)
    console.print(f"Org '{org_guid}' successfully activated.")


@orgs.command("list", cls=IncydrCommand)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive orgs. Defaults to returning both when when neither option is passed.",
)
@table_format_option
@columns_option
@logging_options
def list_(
    active: Optional[bool],
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List orgs.
    """
    client = Client()
    orgs_ = client.orgs.v1.list(active=active).orgs

    if format_ == TableFormat.csv:
        render.csv(Org, orgs_, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(Org, orgs_, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in orgs_:
            console.print_json(item.json())
    else:
        for item in orgs_:
            click.echo(item.json())


@orgs.command("create", cls=IncydrCommand)
@click.argument("name")
@click.option(
    "--external-reference",
    default=None,
    help="The external reference string for the org. Defaults to None.",
)
@click.option(
    "--notes",
    default=None,
    help="The notes string for the org. Defaults to None.",
)
@click.option(
    "--parent-org-guid",
    default=None,
    help="The org guid for the created org's parent. Defaults to your tenant's parent org.",
)
@single_format_option
@columns_option
@logging_options
def create(
    name: str,
    external_reference: Optional[str],
    notes: Optional[str],
    parent_org_guid: Optional[str],
    format_: SingleFormat,
    columns: Optional[str],
):
    """
    Create a new org.
    """
    client = Client()
    org = client.orgs.v1.create(
        org_name=name,
        org_ext_ref=external_reference,
        parent_org_guid=parent_org_guid,
        notes=notes,
    )

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(org), title=f"Org {org.org_name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(org.json())
    else:
        click.echo(org.json())


@orgs.command("deactivate", cls=IncydrCommand)
@click.argument("org_guid")
@logging_options
def deactivate_org(org_guid: str):
    """
    Deactivate the given org.
    """
    client = Client()
    client.orgs.v1.deactivate(org_guid)
    console.print(f"Org '{org_guid}' successfully deactivated.")


@orgs.command("show", cls=IncydrCommand)
@click.argument("org_guid")
@single_format_option
@columns_option
@logging_options
def show(
    org_guid: str,
    format_: SingleFormat,
    columns: Optional[str],
):
    """
    View details of an org.
    """
    client = Client()
    org = client.orgs.v1.get_org(org_guid=org_guid)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(org), title=f"Org: {org.org_name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(org.json())
    else:
        click.echo(org.json())


@orgs.command("update", cls=IncydrCommand)
@click.argument("org_guid")
@click.option(
    "--name", help="The name of the org being updated. Required.", required=True
)
@click.option(
    "--external-reference",
    default=None,
    help="The external reference string for the org. Defaults to None.",
)
@click.option(
    "--notes",
    default=None,
    help="The notes string for the org. Defaults to None.",
)
@single_format_option
@columns_option
@logging_options
def update(
    org_guid: str,
    name: str,
    external_reference: Optional[str],
    notes: Optional[str],
    format_: SingleFormat,
    columns: Optional[str],
):
    """
    Update an org.
    """
    client = Client()
    org = client.orgs.v1.update(
        org_guid=org_guid, org_name=name, org_ext_ref=external_reference, notes=notes
    )

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(org), title=f"Org {org.org_name}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(org.json())
    else:
        click.echo(org.json())
