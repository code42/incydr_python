import click
import requests
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
from _incydr_sdk.actors.client import ActorNotFoundError
from _incydr_sdk.actors.models import Actor
from _incydr_sdk.core.client import Client
from _incydr_sdk.exceptions import IncydrException
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def actors():
    """
    View and manage Incydr actors.

    Actors are identities that generate events collected by Incydr.
    User cloud accounts are consolidated into a single actor through adoption,
    which tie related actors to one parent actor.

    The actor commands can be used to retrieve information about actors and their relationships,
    and also manage adoption.
    """


@actors.command("list", cls=IncydrCommand)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive actors. Defaults to returning both when when neither option is passed.",
)
@click.option(
    "--name-starts-with",
    default=None,
    help="Find actors whose name (e.g. username/email) starts with this text, ignoring case.",
)
@click.option(
    "--name-ends-with",
    default=None,
    help="Find actors whose name (e.g. username/email) ends with this text, ignoring case.",
)
@click.option(
    "--prefer-parent",
    is_flag=True,
    default=False,
    help="Returns an actor's parent when applicable. Returns an actor themselves if they have no parent.",
)
@table_format_option
@columns_option
@logging_options
def list_(
    active: bool = None,
    name_starts_with: str = None,
    name_ends_with: str = None,
    prefer_parent: bool = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List actors.
    """

    client = Client()

    actors = client.actors.v1.iter_all(
        active=active,
        name_starts_with=name_starts_with,
        name_ends_with=name_ends_with,
        prefer_parent=prefer_parent,
    )

    if format_ == TableFormat.table:
        render.table(Actor, actors, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(Actor, actors, columns=columns, flat=True)
    elif format_ == TableFormat.json_pretty:
        for actor in actors:
            console.print_json(actor.json())
    else:
        for actor in actors:
            click.echo(actor.json())


@actors.command(cls=IncydrCommand)
@click.option("--actor-id", default=None, help="Get an actor by actor ID.")
@click.option(
    "--name",
    default=None,
    help="Get an actor by actor name, typically a username/email address.",
)
@click.option(
    "--prefer-parent",
    is_flag=True,
    default=False,
    help="Returns an actor's parent when applicable. Returns an actor themselves if they have no parent.",
)
@single_format_option
@logging_options
def show(
    actor_id: str = None,
    name: str = None,
    prefer_parent: bool = None,
    format_: SingleFormat = None,
):
    """
    Show actor details.

    Specify actor by ID or name, either --actor-id or --name is required.
    """
    client = Client()

    try:
        if actor_id:
            if name:
                console.print(
                    "Both --actor-id and --name options passed, ignoring name and retrieving by actor ID."
                )
            actor = client.actors.v1.get_actor_by_id(
                actor_id, prefer_parent=prefer_parent
            )
        elif name:
            actor = client.actors.v1.get_actor_by_name(
                name, prefer_parent=prefer_parent
            )
        else:
            raise click.UsageError(
                "At least one of --actor-id or --name options must be supplied."
            )
    except ActorNotFoundError:
        console.print(f"No results for actors with name '{name}'.")
        return

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(actor), title=f"Actor {actor.actor_id}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(actor.json())
    else:
        click.echo(actor.json())


@actors.command(cls=IncydrCommand)
@click.option(
    "--actor-id",
    default=None,
    help="Get an actor family by the actor ID of one of its members.",
)
@click.option(
    "--name",
    default=None,
    help="Get an actor family by the actor name of one of its members, where name is typically a username/email address.",
)
@single_format_option
@logging_options
def show_family(actor_id: str = None, name: str = None, format_: SingleFormat = None):
    """
    Show an actors family.

    Specify actor by ID or name, either --actor-id or --name is required.

    An actor family consists of the the parent actor and any associated children.
    """

    client = Client()
    if actor_id:
        if name:
            console.print(
                "Both --actor-id and --name options passed, ignoring name and retrieving by actor ID."
            )
        family = client.actors.v1.get_family_by_member_id(actor_id)
    elif name:
        family = client.actors.v1.get_family_by_member_name(name)
    else:
        raise click.UsageError(
            "At least one of --actor-id or --name options must be supplied."
        )

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(
            Panel.fit(
                model_as_card(family),
                title=f"Actor Family with Parent {family.parent.actor_id}",
            )
        )
    elif format_ == SingleFormat.json_pretty:
        console.print_json(family.json())
    else:
        click.echo(family.json())


@actors.group("adoption", cls=IncydrGroup)
def adoption():
    """Manage actor adoption."""


@adoption.command(cls=IncydrCommand)
@click.argument("children")
@click.argument("parent")
@logging_options
def create(
    children: str,
    parent: str,
):
    """
    Create an adoption between an actor and a parent actor by adding the actor as a child to the parent, both
    are specified by their actor ID.

    Activity originating from actors who have a parent will have said activity attributed to their parent.

    CHILDREN is a comma-delimited string of one or more actor IDs, all of which will be adopted by the specified parent actor.

    PARENT is a single actor ID.
    """
    client = Client()
    children_list = children.split(",")
    response = None
    for child in children_list:
        try:
            response = client.actors.v1.create_adoption(child, parent)
        except (IncydrException, requests.HTTPError):
            console.print(f"Error creating adoption for child {child}, skipping...")

    if response:
        console.print(
            f"Adoption(s) created between parent actor with ID: {response.parent_actor_id} and children with ID(s): {response.child_actor_ids}"
        )
    else:
        console.print("No adoptions created successfully.")


@adoption.command(cls=IncydrCommand)
@click.argument("children")
@logging_options
def remove(
    children: str,
):
    """
    Removes the adoption between a child and parent actor by removing the parent from a child actor, specified by
    actor ID.

    CHILDREN is a comma-delimited string of one or more actor IDs, all of which will be removed from their parent actor.
    """
    client = Client()
    children_list = children.split(",")
    response = None
    success = []
    for child in children_list:
        try:
            response = client.actors.v1.remove_adoption(child)
            success.append(child)
        except (IncydrException, requests.HTTPError):
            console.print(f"Error removing adoption for child {child}, skipping...")

    if response:
        console.print(
            f"Adoption removed. Following actors removed from parent: {success}"
        )
    else:
        console.print("No adoptions removed successfully.")
