from uuid import UUID

import click
from click import Context
from pydantic import BaseModel
from rich.console import ConsoleRenderable
from rich.console import RichCast
from rich.progress import track
from rich.table import Table

from incydr._watchlists.models.responses import IncludedDepartment
from incydr._watchlists.models.responses import IncludedDirectoryGroup
from incydr._watchlists.models.responses import Watchlist
from incydr._watchlists.models.responses import WatchlistUser
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.options.utils import user_lookup_callback
from incydr.cli.cmds.utils import user_lookup
from incydr.cli.core import incompatible_with
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.cli.render import measure_renderable
from incydr.types import file_or_str_cls
from incydr.utils import get_fields
from incydr.utils import iter_model_formatted
from incydr.utils import model_as_card
from incydr.utils import read_dict_from_csv

MAX_USER_DISPLAY_COUNT = 25


def get_watchlist_id_callback(ctx, param, value):
    if not value:
        return
    try:
        UUID(hex=value)
        return value
    except ValueError:
        # if not an ID value
        client = ctx.obj()
        return client.watchlists.v1.get_id_by_name(value)


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def watchlists(ctx, log_level, log_file):
    """
    View and manage watchlists.

    After creation, Watchlists can be managed by type (ex: `DEPARTING_EMPLOYEE`) or ID. `CUSTOM` watchlists must be managed by title or ID.

    The following values are valid watchlist types:

        * CONTRACT_EMPLOYEE
        * DEPARTING_EMPLOYEE
        * ELEVATED_ACCESS_PRIVILEGES
        * FLIGHT_RISK
        * HIGH_IMPACT_EMPLOYEE
        * NEW_EMPLOYEE
        * PERFORMANCE_CONCERNS
        * POOR_SECURITY_PRACTICES
        * SUSPICIOUS_SYSTEM_ACTIVITY
        * CUSTOM
    """
    init_client(ctx, log_level, log_file)


watchlist_arg = click.argument("watchlist", callback=get_watchlist_id_callback)
csv_option = click.option(
    "--csv", is_flag=True, default=False, help="Users are specified in a CSV file. "
)


@watchlists.command("list", cls=IncydrCommand)
@click.option(
    "--user",
    default=None,
    help="Filter by watchlists where the user is a member.  Accepts a user ID or a username.  Performs an additional lookup if a username is passed",
    callback=user_lookup_callback,
)
@table_format_option
@columns_option
@click.pass_context
def list_(
    ctx: Context, user: str = None, format_: TableFormat = None, columns: str = None
):
    """
    List watchlists.
    """
    client = ctx.obj()
    watchlists = client.watchlists.v1.iter_all(user_id=user)
    _output_results(watchlists, Watchlist, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.pass_context
def show(ctx: Context, watchlist: str = None):
    """
    Show details for a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.

    If using `rich`, outputs a summary of watchlist information and membership. This includes the following:

    * included_users
    * excluded_users
    * included_departments
    * included_directory_groups

    Lists of users will be truncated to only display the first 25 members, use the `list-included-users` and `list-excluded-users`
    commands respectively to see more details.

    If not using `rich`, outputs watchlist information in JSON without additional membership summary information.
    """
    client = ctx.obj()
    watchlist_response = client.watchlists.v1.get(watchlist)

    if not client.settings.use_rich:
        console.print(watchlist_response.json(), highlight=False)

    def models_as_table(model, models, title=None):
        headers = list(get_fields(model))
        tbl = Table(*headers, title=title, show_lines=True)
        for m in models:
            values = []
            for _name, value in iter_model_formatted(m, render="table"):
                if isinstance(value, BaseModel):
                    value = model_as_card(value)
                elif not isinstance(value, (ConsoleRenderable, RichCast, str)):
                    value = str(value)
                values.append(value)
            tbl.add_row(*values)
        return tbl

    included_users = client.watchlists.v1.list_included_users(watchlist).included_users
    excluded_users = client.watchlists.v1.list_excluded_users(watchlist).excluded_users
    departments = client.watchlists.v1.list_departments(watchlist).included_departments
    dir_groups = client.watchlists.v1.list_directory_groups(
        watchlist
    ).included_directory_groups
    t = Table(title=f"{watchlist_response.list_type} Watchlist")
    t.add_column("Stats")

    tables = []
    if included_users:
        tables.append(
            models_as_table(WatchlistUser, included_users[:MAX_USER_DISPLAY_COUNT])
        )
        t.add_column("Included Users")
    if excluded_users:
        tables.append(
            models_as_table(WatchlistUser, excluded_users[:MAX_USER_DISPLAY_COUNT])
        )
        t.add_column("Excluded Users")
    if departments:
        tables.append(models_as_table(IncludedDepartment, departments))
        t.add_column("Included Departments")
    if dir_groups:
        tables.append(models_as_table(IncludedDirectoryGroup, dir_groups))
        t.add_column("Included Directory Groups")

    t.add_row(model_as_card(watchlist_response), *tables)

    with console.pager():
        # expand console and table so no values get truncated due to size of console, since we're using a pager
        console.width = t.width = measure_renderable(t)
        console.print(t, crop=False, soft_wrap=False, overflow="fold")


@watchlists.command(cls=IncydrCommand)
@click.argument("watchlist-type")
@click.option("--title", help="Required title for a CUSTOM watchlist.")
@click.option("--description", help="Optional description for a CUSTOM watchlist.")
@click.pass_context
def create(
    ctx: Context, watchlist_type: str, title: str = None, description: str = None
):
    """
    Create a new watchlist.

    Where `WATCHLIST_TYPE` is of the following:

    * `CONTRACT_EMPLOYEE`
    * `DEPARTING_EMPLOYEE`
    * `ELEVATED_ACCESS_PRIVILEGES`
    * `FLIGHT_RISK`
    * `HIGH_IMPACT_EMPLOYEE`
    * `NEW_EMPLOYEE`
    * `PERFORMANCE_CONCERNS`
    * `POOR_SECURITY_PRACTICES`
    * `SUSPICIOUS_SYSTEM_ACTIVITY`
    * `CUSTOM`

    The `--title` (required) and `--description` (optional) options are exclusively for creating CUSTOM watchlists.
    """
    client = ctx.obj()
    watchlist = client.watchlists.v1.create(watchlist_type, title, description)
    console.print(
        f"Successfully created {watchlist.list_type} watchlist with ID: '{watchlist.watchlist_id}'."
    )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.pass_context
def delete(ctx: Context, watchlist: str):
    """
    Delete a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    client.watchlists.v1.delete(watchlist)
    console.print(f"Successfully deleted watchlist with ID: '{watchlist}'.")


@watchlists.command(cls=IncydrCommand)
@click.argument("watchlist-id")
@click.option("--title", help="Updated title for a CUSTOM watchlist.")
@click.option("--description", help="Updated description for a CUSTOM watchlist.")
@click.option(
    "--clear-description",
    is_flag=True,
    default=False,
    help="Clear the description on a CUSTOM watchlist.",
    cls=incompatible_with("description"),
)
@click.pass_context
def update(
    ctx: Context,
    watchlist_id: str,
    title: str = None,
    description: str = None,
    clear_description: str = None,
):
    """
    Update a CUSTOM watchlist.
    """
    if clear_description:
        description = ""

    client = ctx.obj()
    client.watchlists.v1.update(watchlist_id, title, description)
    console.print(f"Successfully updated watchlist with ID: '{watchlist_id}'.")


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.option(
    "--users",
    default=None,
    type=file_or_str_cls,
    help="List of user IDs or usernames to include on the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--excluded-users",
    default=None,
    type=file_or_str_cls,
    help="List of user IDs or usernames to exclude from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--departments",
    default=None,
    type=file_or_str_cls,
    help="Comma-delimited string of department names to include on the watchlist. "
    "Individual users from the departments will be added as watchlist members, where department information comes "
    "from SCIM or User Directory Sync.",
)
@click.option(
    "--directory-groups",
    default=None,
    type=file_or_str_cls,
    help="Comma-delimited string of directory group IDs to include on the watchlist. "
    "Individual users from the directory groups will be added as watchlist members, where group information comes "
    "from SCIM or User Directory Sync.",
)
@click.pass_context
def add(
    ctx: Context,
    watchlist: str,
    users=None,
    excluded_users=None,
    departments=None,
    directory_groups=None,
):
    """
    Manage watchlist membership by including or excluding individual users and/or groups.

    Add any of the following members to a watchlist with the corresponding options:

    * users
    * excluded-users
    * departments
    * directory-groups

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()

    # Add included users
    if users:
        client.watchlists.v1.add_included_users(
            watchlist, _get_user_ids(client, users, _is_path(users))
        )
        console.print(
            f"Successfully included users on watchlist with ID: '{watchlist}'"
        )

    # Add excluded users
    if excluded_users:
        client.watchlists.v1.add_excluded_users(
            watchlist, _get_user_ids(client, excluded_users, _is_path(excluded_users))
        )
        console.print(
            f"Successfully excluded users from watchlist with ID: '{watchlist}'"
        )

    # Add departments
    if departments:
        client.watchlists.v1.add_departments(
            watchlist, [i.strip() for i in departments.split(",")]
        )
        console.print(
            f"Successfully included departments to watchlist with ID: {watchlist}"
        )

    # Add directory groups
    if directory_groups:
        client.watchlists.v1.add_directory_groups(
            watchlist, [i.strip() for i in directory_groups.split(",")]
        )
        console.print(
            f"Successfully included directory groups to watchlist with ID: {watchlist}"
        )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.option(
    "--users",
    default=None,
    type=file_or_str_cls,
    help="List of included user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--excluded-users",
    default=None,
    type=file_or_str_cls,
    help="List of excluded user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--departments",
    default=None,
    type=file_or_str_cls,
    help="Comma-delimited string of department names to remove from the watchlist. "
    "Individual users from the departments will be added as watchlist members, where department information comes "
    "from SCIM or User Directory Sync.",
)
@click.option(
    "--directory-groups",
    default=None,
    type=file_or_str_cls,
    help="Comma-delimited string of directory group IDs to remove from the watchlist. "
    "Individual users from the directory groups will be added as watchlist members, where group information comes "
    "from SCIM or User Directory Sync.",
)
@click.pass_context
def remove(
    ctx: Context,
    watchlist: str,
    users=None,
    excluded_users=None,
    departments=None,
    directory_groups=None,
):
    """
    Manage watchlist membership by removing individual users and/or groups.

    Remove any of the following members from a watchlist with the corresponding options:

    * users
    * excluded-users
    * departments
    * directory-groups

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()

    # Remove included users
    if users:
        client.watchlists.v1.remove_included_users(
            watchlist, _get_user_ids(client, users, _is_path(users))
        )
        console.print(
            f"Successfully removed included users on watchlist with ID: '{watchlist}'"
        )

    # Remove excluded users
    if excluded_users:
        client.watchlists.v1.remove_excluded_users(
            watchlist, _get_user_ids(client, excluded_users, _is_path(excluded_users))
        )
        console.print(
            f"Successfully removed excluded users from watchlist with ID: '{watchlist}'"
        )

    # Remove departments
    if departments:
        client.watchlists.v1.remove_departments(
            watchlist, [i.strip() for i in departments.split(",")]
        )
        console.print(
            f"Successfully removed departments from watchlist with ID: {watchlist}"
        )

    # Remove directory groups
    if directory_groups:
        client.watchlists.v1.remove_directory_groups(
            watchlist, [i.strip() for i in directory_groups.split(",")]
        )
        console.print(
            f"Successfully removed directory groups from watchlist with ID: {watchlist}"
        )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@columns_option
@table_format_option
@click.pass_context
def list_members(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List members of a watchlist.

    A member may have been added as an included user, or is a member of an included department, etc.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    members = client.watchlists.v1.list_members(watchlist)
    _output_results(members.watchlist_members, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_included_users(
    ctx: Context, watchlist: str, format_: str, columns: str = None
):
    """
    List users explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    users = client.watchlists.v1.list_included_users(watchlist)
    _output_results(users.included_users, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_excluded_users(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List users excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    users = client.watchlists.v1.list_excluded_users(watchlist)
    _output_results(users.excluded_users, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_directory_groups(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List directory groups included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    groups = client.watchlists.v1.list_directory_groups(watchlist)
    _output_results(
        groups.included_directory_groups, IncludedDirectoryGroup, format_, columns
    )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_departments(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List departments included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = ctx.obj()
    deps = client.watchlists.v1.list_departments(watchlist)
    _output_results(deps.included_departments, IncludedDepartment, format_, columns)


def _get_user_ids(client, users, csv=False):
    if csv:
        ids = []
        for row in track(
            read_dict_from_csv(users),
            description="Reading users...",
            transient=True,
        ):
            ids.append(user_lookup(client, row["user"]))
    else:
        ids = [user_lookup(client, i.strip()) for i in users.split(",")]
    return ids


def _output_results(results, model, format_, columns=None):
    if format_ == TableFormat.csv:
        render.csv(model, results, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(model, results, columns=columns, flat=False)
    elif format_ == TableFormat.json:
        for item in results:
            console.print_json(item.json())
    else:  # format_ == "raw-json"/TableFormat.raw_json
        for item in results:
            console.print(item.json(), highlight=False)


def _is_path(users: str):
    return users.lower().endswith(".csv")
