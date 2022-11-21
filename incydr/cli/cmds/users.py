from typing import Optional

import click
from click import Context
from requests import HTTPError
from rich.panel import Panel
from rich.progress import track

from incydr._devices.models import Device
from incydr._users.models import User
from incydr._users.models import UserRole
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.options.utils import user_lookup_callback
from incydr.cli.cmds.utils import user_lookup
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import model_as_card
from incydr.utils import read_dict_from_csv

user_arg = click.argument("user", callback=user_lookup_callback)


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def users(ctx, log_level, log_file):
    """View and manage file events."""
    init_client(ctx, log_level, log_file)


@users.command("list", cls=IncydrCommand)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive users. Defaults to returning both when when neither option is passed.",
)
@click.option(
    "--blocked/--unblocked",
    default=None,
    help="Filter by blocked or unblocked users. Defaults to returning both when when neither option is passed.",
)
@click.option("--username", default=None)
@table_format_option
@columns_option
@click.pass_context
def list_(
    ctx: Context,
    active: Optional[bool],
    blocked: Optional[bool],
    username: Optional[str],
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List users.
    """
    client = ctx.obj()
    users_ = client.users.v1.iter_all(active=active, blocked=blocked, username=username)

    columns = columns or [
        "user_id",
        "username",
        "first_name",
        "last_name",
        "org_guid",
        "org_name",
        "notes",
        "active",
        "blocked",
    ]

    if format_ == TableFormat.csv:
        render.csv(User, users_, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(User, users_, columns=columns, flat=False)
    else:
        printed = False
        if format_ == TableFormat.json:
            for item in users_:
                printed = True
                console.print_json(item.json())
        else:  # raw-json
            for item in users_:
                printed = True
                click.echo(item.json())
        if not printed:
            console.print("No results found.")


@users.command(cls=IncydrCommand)
@click.argument("user")  # don't need username callback, handled by client method
@single_format_option
@click.pass_context
def show(ctx: Context, user, format_: SingleFormat):
    """
    Show details for a user.

    Accepts a user ID or a username.  Performs an additional lookup if username is passed.
    """
    client = ctx.obj()
    user = client.users.v1.get_user(user)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(user), title=f"User {user.username}"))
    elif format_ == SingleFormat.json:
        console.print_json(user.json())
    else:  # format == "raw-json"
        console.print(user.json(), highlight=False)


@users.command(cls=IncydrCommand)
@user_arg
@table_format_option
@columns_option
@click.pass_context
def list_devices(ctx: Context, user, format_: TableFormat, columns: str = None):
    """
    List devices associated with a particular user.
    """
    client = ctx.obj()
    devices = client.users.v1.get_devices(user).devices

    columns = columns or [
        "device_id",
        "name",
        "os_hostname",
        "status",
        "active",
        "blocked",
        "alert_state",
        "org_guid",
        "login_date",
    ]

    if format_ == TableFormat.csv:
        render.csv(Device, devices, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(Device, devices, columns=columns, flat=False)
    elif format_ == TableFormat.json:
        for item in devices:
            console.print_json(item.json())
    else:  # format == "raw-json"/TableFormat.raw_json
        for item in devices:
            console.print(item.json(), highlight=False)


@users.command(cls=IncydrCommand)
@user_arg
@table_format_option
@columns_option
@click.pass_context
def list_roles(ctx: Context, user: str, format_: TableFormat, columns: str = None):
    """
    List roles associated with a particular user.
    """
    client = ctx.obj()
    roles = client.users.v1.get_roles(user)

    if format_ == TableFormat.csv:
        render.csv(UserRole, roles, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(UserRole, roles, columns=columns, flat=False)
    elif format_ == TableFormat.json:
        for item in roles:
            console.print_json(item.json())
    else:  # format == "raw-json"/TableFormat.raw_json
        for item in roles:
            console.print(item.json(), highlight=False)


@users.command(cls=IncydrCommand)
@user_arg
@click.argument("roles")
@click.pass_context
# TODO: role IDs
def update_roles(ctx: Context, user, roles):
    """
    Update roles associated with a particular user.

    Usage:
        users update-roles USER ROLES

    Where USER is the user ID or username of the user whose roles will be updated. Performs an additional lookup if username is passed.
    ROLES is a comma-delimited list of roles to replace that user's roles.

    """
    client = ctx.obj()
    client.users.v1.update_roles(user, roles.split(","))


# TODO: add-role. blocked by INTEG-2298

# TODO: remove-role. blocked by INTEG-2298


@users.command(cls=IncydrCommand)
@user_arg
@click.pass_context
def activate(ctx: Context, user):
    """
    Activate a user.
    """
    client = ctx.obj()
    client.users.v1.activate(user)


@users.command(cls=IncydrCommand)
@user_arg
@click.pass_context
def deactivate(ctx: Context, user):
    """
    Deactivate a user.
    """
    client = ctx.obj()
    client.users.v1.deactivate(user)


@users.command(cls=IncydrCommand)
@user_arg
@click.argument("org_guid")
@click.pass_context
def move(ctx: Context, user, org_guid):
    """
    Move a user to a specified organization.
    """
    client = ctx.obj()
    client.users.v1.move(user, org_guid)


@users.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
# TODO: role IDs
def bulk_update_roles(ctx: Context, csv):
    """
    Bulk update roles associated with multiple users with a CSV file.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires the following columns:

    * `user` - User ID or username of the user whose roles will be updated. Performs an additional lookup if username is passed.
    * `roles` - Space-delimited list of role IDs to assign to the new user.  These will replace the specified user's existing roles.
    """
    client = ctx.obj()
    try:
        for row in track(
            read_dict_from_csv(csv),
            description="Updated user roles...",
            transient=True,
        ):
            user = row.get("user")
            if user and "@" in user:
                user = user_lookup(client, row["user"])
            client.users.v1.update_roles(user, row["roles"].split(" "))
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@users.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
def bulk_activate(ctx: Context, csv):
    """
    Bulk activate users.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires a single `user` column that contains either the user IDs or the usernames of the users to be activated.
    """
    client = ctx.obj()
    try:
        for row in track(
            read_dict_from_csv(csv),
            description="Activating users...",
            transient=True,
        ):
            user = row.get("user")
            if user and "@" in user:
                user = user_lookup(client, row["user"])
            client.users.v1.activate(user)
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@users.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
def bulk_deactivate(ctx: Context, csv):
    """
    Bulk deactivate users.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires a single `user` column that contains either the user IDs or the usernames of the users to be deactivated.
    """
    client = ctx.obj()
    try:
        for row in track(
            read_dict_from_csv(csv),
            description="Deactivating users...",
            transient=True,
        ):
            user = row.get("user")
            if user and "@" in user:
                user = user_lookup(client, row["user"])
            client.users.v1.deactivate(user)
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@users.command(cls=IncydrCommand)
@click.argument("csv")
@click.pass_context
def bulk_move(ctx: Context, csv):
    """
    Bulk move multiple users to specified organizations.

    Takes a single arg `CSV` which specifies the path to the file.
    Requires the following columns:

    * `user` - User ID or username of the user who will be moved to the new organization. Performs an additional lookup if username is passed.
    * `org_guid` - GUID for the user's new organization.
    """
    client = ctx.obj()
    try:
        for row in track(
            read_dict_from_csv(csv),
            description="Moving users...",
            transient=True,
        ):
            user = row.get("user")
            if user and "@" in user:
                user = user_lookup(client, row["user"])
            client.users.v1.move(user, row["org_guid"])
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")
