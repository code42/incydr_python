from functools import lru_cache
from pathlib import Path
from typing import Optional

import click
from boltons.iterutils import bucketize
from pydantic import Field
from requests import HTTPError
from rich.panel import Panel
from rich.progress import track

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.models import UserCSV
from _incydr_cli.cmds.models import UserJSON
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import input_format_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cmds.options.utils import user_lookup_callback
from _incydr_cli.cmds.utils import user_lookup
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_cli.file_readers import AutoDecodedFile
from _incydr_sdk.core.client import Client
from _incydr_sdk.devices.models import Device
from _incydr_sdk.users.client import RoleNotFoundError
from _incydr_sdk.users.client import RoleProcessingError
from _incydr_sdk.users.client import UserNotAssignedRoleError
from _incydr_sdk.users.models import Role
from _incydr_sdk.users.models import User
from _incydr_sdk.users.models import UserRole
from _incydr_sdk.utils import model_as_card

user_arg = click.argument("user", callback=user_lookup_callback)


@click.group(cls=IncydrGroup)
@logging_options
def users():
    """View and manage users and user roles."""


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
@logging_options
def list_(
    active: Optional[bool],
    blocked: Optional[bool],
    username: Optional[str],
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List users.
    """
    client = Client()
    users_ = client.users.v1.iter_all(active=active, blocked=blocked, username=username)

    if format_ == TableFormat.csv:
        render.csv(User, users_, columns=columns, flat=True)
    elif format_ == TableFormat.table:
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
        render.table(User, users_, columns=columns, flat=False)
    else:
        printed = False
        if format_ == TableFormat.json_pretty:
            for item in users_:
                printed = True
                console.print_json(item.json())
        else:
            for item in users_:
                printed = True
                click.echo(item.json())
        if not printed:
            console.print("No results found.")


@users.command(cls=IncydrCommand)
@click.argument("user")  # don't need username callback, handled by client method
@single_format_option
@logging_options
def show(
    user,
    format_: SingleFormat,
):
    """
    Show details for a user.

    Accepts a user ID or a username.  Performs an additional lookup if username is passed.
    """
    client = Client()
    user = client.users.v1.get_user(user)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(user), title=f"User {user.username}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(user.json())
    else:
        click.echo(user.json())


@users.command(cls=IncydrCommand)
@user_arg
@table_format_option
@columns_option
@logging_options
def list_devices(
    user,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List devices associated with a particular user.
    """
    client = Client()
    devices = client.users.v1.get_devices(user).devices

    if format_ == TableFormat.csv:
        render.csv(Device, devices, columns=columns, flat=True)
    elif format_ == TableFormat.table:
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
        render.table(Device, devices, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in devices:
            console.print_json(item.json())
    else:
        for item in devices:
            click.echo(item.json())


@users.command("list-roles", cls=IncydrCommand)
@user_arg
@table_format_option
@columns_option
@logging_options
def list_user_roles(
    user: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List roles associated with a particular user.
    """
    client = Client()
    roles = client.users.v1.list_user_roles(user)

    if format_ == TableFormat.csv:
        render.csv(UserRole, roles, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(UserRole, roles, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in roles:
            console.print_json(item.json())
    else:
        for item in roles:
            click.echo(item.json())


@users.command(cls=IncydrCommand)
@user_arg
@click.argument("roles")
@click.option("--add", "update_method", flag_value="add", default=None)
@click.option("--remove", "update_method", flag_value="remove", default=None)
@logging_options
def update_roles(
    user,
    roles: str,
    update_method: str,
):
    """
    Update roles associated with a particular user.

    Usage:
        users update-roles USER ROLES

    USER is the user ID or username of the user whose roles will be updated.
    Performs an additional lookup if username is passed.

    ROLES is a comma-delimited list of role IDs and/or role names to replace that user's roles.

    Use the `--remove` flag to remove the specified role(s) from a user's existing roles.

    Alternatively, use the `--add` flag to assign additional roles to a user's existing roles.
    """
    client = Client()

    if update_method == "add":
        update_func = client.users.v1.add_roles
    elif update_method == "remove":
        update_func = client.users.v1.remove_roles
    else:
        update_func = client.users.v1.update_roles

    try:
        update_func(user, [r.strip() for r in roles.split(",")])
    except RoleNotFoundError as e:
        raise e
    except UserNotAssignedRoleError as e:
        raise e
    console.print(f"Roles successfully updated for user '{user}'")


@users.command(cls=IncydrCommand)
@user_arg
@logging_options
def activate(
    user,
):
    """
    Activate a user.
    """
    client = Client()
    client.users.v1.activate(user)
    console.print(f"User '{user}' successfully activated.")


@users.command(cls=IncydrCommand)
@user_arg
@logging_options
def deactivate(
    user,
):
    """
    Deactivate a user.
    """
    client = Client()
    client.users.v1.deactivate(user)
    console.print(f"User '{user}' successfully deactivated.")


@users.command(cls=IncydrCommand)
@user_arg
@click.argument("org_guid")
@logging_options
def move(
    user,
    org_guid,
):
    """
    Move a user to a specified organization.
    """
    client = Client()
    client.users.v1.move(user, org_guid)
    console.print(f"User '{user}' successfully moved to org '{org_guid}'.")


@users.group("roles", cls=IncydrGroup)
def roles_():
    """View available roles."""


@roles_.command("show", cls=IncydrCommand)
@single_format_option
@click.argument("role")
@logging_options
def show_role(
    role,
    format_: SingleFormat,
):
    """
    Show details for a single role, specified by role name or role ID.
    """
    client = Client()
    role = client.users.v1.get_role(role)
    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(role), title=role.role_name))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(role.json())
    else:
        click.echo(role.json())


@roles_.command("list", cls=IncydrCommand)
@table_format_option
@logging_options
def list_roles(
    format_: TableFormat,
):
    """
    List all available roles that can be assigned by the current user.
    """
    client = Client()
    roles = client.users.v1.list_roles()
    if format_ == TableFormat.csv:
        render.csv(Role, roles, flat=True)
    elif format_ == TableFormat.table:
        render.table(Role, roles, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in roles:
            console.print_json(item.json())
    else:
        for item in roles:
            click.echo(item.json())


@users.command(cls=IncydrCommand)
@click.argument("file", type=AutoDecodedFile())
@input_format_option
@click.option("--add", "update_method", flag_value="add", default=None)
@click.option("--remove", "update_method", flag_value="remove", default=None)
@logging_options
def bulk_update_roles(
    file,
    update_method: str,
    format_: Optional[str],
):
    """
    Bulk update roles associated with multiple users from a file.

    By default, the provided roles will replace the specified user's existing roles.
    Use the `--add` flag or the `--remove` flag to add or remove roles, respectively, from a user's existing roles.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Requires the following CSV columns or JSON keys:

    * `user` - User ID or username of the user whose roles will be updated. Performs an additional lookup if username is passed.
    * `role` - Role ID and/or role name (case-sensitive) to assign to the new user.

    Example:

        The following command will add roles to users as specified in a JSON-lines formatted file:

            incydr users bulk-update-roles path/to/file.json --add --format json-lines
    """
    client = Client()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    class RoleUpdateCSV(UserCSV):
        role: str = Field(
            csv_aliases=["role", "role_id", "role_name", "roleId", "roleName"]
        )

    class RoleUpdateJSON(UserJSON):
        role: str = Field(alias="roleId")

    if format_ == "csv":
        roles_file = RoleUpdateCSV.parse_csv(file)
    else:
        roles_file = RoleUpdateJSON.parse_json_lines(file)

    if update_method == "add":
        update_func = client.users.v1.add_roles
    elif update_method == "remove":
        update_func = client.users.v1.remove_roles
    else:
        update_func = client.users.v1.update_roles

    # group updates by user
    buckets = bucketize(
        roles_file,
        key=lambda role_update: role_update.user,
        value_transform=lambda role_update: role_update.role,
    )
    for bucket in buckets:
        user = bucket
        roles = buckets[bucket]
        try:
            user = resolve_username(user)
            update_func(user, roles)
            console.print(f"Successfully updated roles for user {user}.'")
        except RoleProcessingError as err:
            console.print(
                f"[red]Error! {str(err)} [/red]",
                highlight=False,
            )


@users.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_activate(file: Path, format_: str):
    """
    Bulk activate users.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Requires a single `user` column or field that contains either the user IDs or the usernames of the users to be activated.
    """
    client = Client()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UserCSV.parse_csv(file)
    else:
        models = UserJSON.parse_json_lines(file)

    try:
        for row in track(
            models,
            description="Activating users...",
            transient=True,
        ):
            client.users.v1.activate(resolve_username(row.user))
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@users.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_deactivate(file: Path, format_: str):
    """
    Bulk deactivate users.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Requires a single `user` column or field that contains either the user IDs or the usernames of the users to be deactivated.
    """
    client = Client()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UserCSV.parse_csv(file)
    else:
        models = UserJSON.parse_json_lines(file)

    try:
        for row in track(
            models,
            description="Deactivating users...",
            transient=True,
        ):
            client.users.v1.deactivate(resolve_username(row.user))
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@users.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_move(file: Path, format_: str):

    """
    Bulk move multiple users to specified organizations.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Requires the following columns:

    * `user` - User ID or username of the user who will be moved to the new organization. Performs an additional lookup if username is passed.
    * `org_guid` - GUID for the user's new organization.
    """
    client = Client()

    class UserMoveCSV(UserCSV):
        org_guid: str = Field(csv_aliases=["org_guid", "orgGuid", "org"])

    class UserMoveJSON(UserJSON):
        org_guid: str = Field(alias="orgGuid")

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UserMoveCSV.parse_csv(file)
    else:
        models = UserMoveJSON.parse_json_lines(file)

    try:
        for row in track(
            models,
            description="Moving users...",
            transient=True,
        ):
            client.users.v1.move(resolve_username(row.user), row.org_guid)
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")
