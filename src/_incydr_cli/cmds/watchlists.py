from typing import Optional
from uuid import UUID

import click
from rich.progress import track
from rich.table import Table

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.models import UserCSV
from _incydr_cli.cmds.models import UserJSON
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cmds.options.utils import user_lookup_callback
from _incydr_cli.cmds.utils import user_lookup
from _incydr_cli.core import incompatible_with
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_cli.file_readers import FileOrString
from _incydr_cli.render import measure_renderable
from _incydr_cli.render import models_as_table
from _incydr_sdk.core.client import Client
from _incydr_sdk.utils import model_as_card
from _incydr_sdk.watchlists.models.responses import IncludedDepartment
from _incydr_sdk.watchlists.models.responses import IncludedDirectoryGroup
from _incydr_sdk.watchlists.models.responses import Watchlist
from _incydr_sdk.watchlists.models.responses import WatchlistUser

MAX_USER_DISPLAY_COUNT = 25

input_format_option = click.option(
    "--format",
    "-f",
    "format_",
    type=click.Choice(["csv", "json-lines"]),
    default="csv",
    help="Specify format of input file(s): 'csv' or 'json-lines'. Defaults to 'csv'. Multiple input files must all be the same format.",
)


def get_watchlist_id_callback(ctx, param, value):
    if not value:
        return
    try:
        UUID(hex=value)
        return value
    except ValueError:
        # if not an ID value
        client = Client()
        return client.watchlists.v1.get_id_by_name(value)


@click.group(cls=IncydrGroup)
@logging_options
def watchlists():
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
@logging_options
def list_(
    user: str = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List watchlists.
    """
    client = Client()
    watchlists = client.watchlists.v1.iter_all(user_id=user)
    _output_results(watchlists, Watchlist, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@logging_options
def show(
    watchlist: str,
):
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
    client = Client()
    watchlist_response = client.watchlists.v1.get(watchlist)

    if not client.settings.use_rich:
        click.echo(watchlist_response.json())
        return

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
@logging_options
def create(
    watchlist_type: str,
    title: str = None,
    description: str = None,
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
    client = Client()
    watchlist = client.watchlists.v1.create(watchlist_type, title, description)
    console.print(
        f"Successfully created {watchlist.list_type} watchlist with ID: '{watchlist.watchlist_id}'."
    )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@logging_options
def delete(
    watchlist: str,
):
    """
    Delete a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
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
@logging_options
def update(
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

    client = Client()
    client.watchlists.v1.update(watchlist_id, title, description)
    console.print(f"Successfully updated watchlist with ID: '{watchlist_id}'.")


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.option(
    "--users",
    default=None,
    type=FileOrString(),
    help="List of user IDs or usernames to include on the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--excluded-users",
    default=None,
    type=FileOrString(),
    help="List of user IDs or usernames to exclude from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--departments",
    default=None,
    help="Comma-delimited string of department names to include on the watchlist. "
    "Individual users from the departments will be added as watchlist members, where department information comes "
    "from SCIM or User Directory Sync.",
)
@click.option(
    "--directory-groups",
    default=None,
    help="Comma-delimited string of directory group IDs to include on the watchlist. "
    "Individual users from the directory groups will be added as watchlist members, where group information comes "
    "from SCIM or User Directory Sync.",
)
@input_format_option
@logging_options
def add(
    watchlist: str,
    users=None,
    excluded_users=None,
    departments=None,
    directory_groups=None,
    format_=None,
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
    client = Client()

    # Add included users
    if users:
        client.watchlists.v1.add_included_users(
            watchlist, _get_user_ids(client, users, format_=format_)
        )
        console.print(
            f"Successfully included users on watchlist with ID: '{watchlist}'"
        )

    # Add excluded users
    if excluded_users:
        client.watchlists.v1.add_excluded_users(
            watchlist, _get_user_ids(client, excluded_users, format_=format_)
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
    type=FileOrString(),
    help="List of included user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed.Argument can be "
    "passed as a comma-delimited string or as a file if prefixed with '@', e.g. '--users @users.csv'. "
    "File should have a single 'user' field.  File format can either be CSV or JSON Lines format, "
    "as specified with the --format option (Default is CSV).",
)
@click.option(
    "--excluded-users",
    default=None,
    type=FileOrString(),
    help="List of excluded user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or as a file if prefixed with '@', e.g. '--users @users.csv'. "
    "File should have a single 'user' field.  File format can either be CSV or JSON Lines format, "
    "as specified with the --format option (Default is CSV).",
)
@click.option(
    "--departments",
    default=None,
    help="Comma-delimited string of department names to remove from the watchlist. "
    "Individual users from the departments will be added as watchlist members, where department information comes "
    "from SCIM or User Directory Sync.",
)
@click.option(
    "--directory-groups",
    default=None,
    help="Comma-delimited string of directory group IDs to remove from the watchlist. "
    "Individual users from the directory groups will be added as watchlist members, where group information comes "
    "from SCIM or User Directory Sync.",
)
@input_format_option
@logging_options
def remove(
    watchlist: str,
    users=None,
    excluded_users=None,
    departments=None,
    directory_groups=None,
    format_=None,
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
    client = Client()

    # Remove included users
    if users:
        client.watchlists.v1.remove_included_users(
            watchlist, _get_user_ids(client, users, format_=format_)
        )
        console.print(
            f"Successfully removed included users on watchlist with ID: '{watchlist}'"
        )

    # Remove excluded users
    if excluded_users:
        client.watchlists.v1.remove_excluded_users(
            watchlist, _get_user_ids(client, excluded_users, format_=format_)
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
@logging_options
def list_members(
    watchlist: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List members of a watchlist.

    A member may have been added as an included user, or is a member of an included department, etc.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    members = client.watchlists.v1.list_members(watchlist)
    _output_results(members.watchlist_members, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_included_users(
    watchlist: str,
    format_: str,
    columns: Optional[str],
):
    """
    List users explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    users = client.watchlists.v1.list_included_users(watchlist)
    _output_results(users.included_users, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_excluded_users(
    watchlist: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List users excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    users = client.watchlists.v1.list_excluded_users(watchlist)
    _output_results(users.excluded_users, WatchlistUser, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_directory_groups(
    watchlist: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List directory groups included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    groups = client.watchlists.v1.list_directory_groups(watchlist)
    _output_results(
        groups.included_directory_groups, IncludedDirectoryGroup, format_, columns
    )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_departments(
    watchlist: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List departments included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    deps = client.watchlists.v1.list_departments(watchlist)
    _output_results(deps.included_departments, IncludedDepartment, format_, columns)


def _get_user_ids(client, users, format_=None):
    if isinstance(users, str):
        ids = [user_lookup(client, i.strip()) for i in users.split(",")]
    else:
        if format_ == "csv":
            users = UserCSV.parse_csv(users)
        else:
            users = UserJSON.parse_json_lines(users)
        ids = []
        for row in track(
            users,
            description="Reading users...",
            transient=True,
        ):
            ids.append(user_lookup(client, row.user))
    return ids


def _output_results(results, model, format_, columns=None):
    if format_ == TableFormat.csv:
        render.csv(model, results, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        render.table(model, results, columns=columns, flat=False)
    elif format_ == TableFormat.json_pretty:
        for item in results:
            console.print_json(item.json())
    else:
        for item in results:
            console.print(item.json(), highlight=False)
