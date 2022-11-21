from uuid import UUID

import click
from click import Context
from rich.panel import Panel
from rich.progress import track

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
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.options.utils import user_lookup_callback
from incydr.cli.cmds.utils import user_lookup
from incydr.cli.core import incompatible_with
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import model_as_card
from incydr.utils import read_dict_from_csv


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

    The following subcommand groups are available to manage watchlist membership:
        * members
        * included-users
        * excluded-users
        * directory-groups
        * departments

    After creation, Watchlists can be managed by ID or type.  CUSTOM watchlists must be managed by ID.

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
@single_format_option
@click.pass_context
def show(ctx: Context, watchlist: str = None, format_: SingleFormat = None):
    """
    Show details for a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    watchlist = client.watchlists.v1.get(watchlist)
    _output_single_result(
        watchlist, f"{watchlist.list_type} Watchlist", format_, client.settings.use_rich
    )


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

    Where WATCHLIST_TYPE is of the following:
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

    The --title (required) and --description (optional) options are exclusively for creating CUSTOM watchlists.
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

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
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


@watchlists.group(cls=IncydrGroup)
def members():
    """
    View watchlist members.

    A member may have been added as an included user, or is a member
    of an included department or directory group.
    """


@members.command("show", cls=IncydrCommand)
@watchlist_arg
@click.argument("user", callback=user_lookup_callback)
@single_format_option
@click.pass_context
def show_member(ctx: Context, watchlist: str, user: str, format_: SingleFormat):
    """
    Show details for a single member of a watchlist.

    A member may have been added as an included user, or is a member of an included department, etc.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    member = client.watchlists.v1.get_member(watchlist, user)
    _output_single_result(
        member,
        f"Watchlist Member: {member.username}",
        format_,
        client.settings.use_rich,
    )


@members.command("list", cls=IncydrCommand)
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

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    members = client.watchlists.v1.list_members(watchlist)
    _output_results(members.watchlist_members, WatchlistUser, format_, columns)


@watchlists.group(cls=IncydrGroup)
def included_users():
    """View and manage users individually included on a watchlist."""


@included_users.command("add", cls=IncydrCommand)
@watchlist_arg
@click.argument("users")
@csv_option
@click.pass_context
def add_included_users(ctx: Context, watchlist: str, users: str, csv: bool = False):
    """
    Include individual users on a watchlist.

        watchlists included-users add WATCHLIST USERS --csv

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    USERS is a comma-delimited string of user IDs or usernames to add to the case.
    An additional lookup is performed if a username is passed.

    To read the users from a csv (single 'users' column),
    pass the path to a csv along with the --csv flag:

        watchlists included-users add WATCHLIST CSV_PATH --csv
    """
    client = ctx.obj()

    users = _get_user_ids(client, users, csv)

    client.watchlists.v1.add_included_users(watchlist, users)
    console.print(f"Successfully included users on watchlist with ID: '{watchlist}'")


@included_users.command("remove", cls=IncydrCommand)
@watchlist_arg
@click.argument("users")
@csv_option
@click.pass_context
def remove_included_users(ctx: Context, watchlist, users: str, csv: bool = False):
    """
    Remove included users from a watchlist.

        watchlists included-users remove WATCHLIST USERS --csv

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    USERS is a comma-delimited string of user IDs or usernames to add to the case.
    An additional lookup is performed if a username is passed.

    To read the users from a csv (single 'users' column),
    pass the path to a csv along with the --csv flag:

        watchlists included-users remove WATCHLIST CSV_PATH --csv

    """
    client = ctx.obj()

    users = _get_user_ids(client, users, csv)

    client.watchlists.v1.remove_included_users(watchlist, users)
    console.print(
        f"Successfully removed included users from watchlist with ID: '{watchlist}'"
    )


@included_users.command("show", cls=IncydrCommand)
@watchlist_arg
@click.argument("user")
@single_format_option
@click.pass_context
def show_included_user(ctx: Context, watchlist: str, user: str, format_: SingleFormat):
    """
    Show details for a user explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    """
    client = ctx.obj()
    user = client.watchlists.v1.get_included_user(watchlist, user)
    _output_single_result(
        user, f"Included User: {user.username}", format_, client.settings.use_rich
    )


@included_users.command("list", cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_included_users(
    ctx: Context, watchlist: str, format_: str, columns: str = None
):
    """
    List users explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    """
    client = ctx.obj()
    users = client.watchlists.v1.list_included_users(watchlist)
    _output_results(users.included_users, WatchlistUser, format_, columns)


@watchlists.group(cls=IncydrGroup)
def excluded_users():
    """View and manage users individually excluded from a watchlist."""


@excluded_users.command("add", cls=IncydrCommand)
@watchlist_arg
@click.argument("users")
@csv_option
@click.pass_context
def add_excluded_users(ctx: Context, watchlist: str, users: str, csv: bool = False):
    """
    Exclude individual users from a watchlist.

        watchlists excluded-users add WATCHLIST USERS --csv

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    USERS is a comma-delimited string of user IDs or usernames to add to the case.
    An additional lookup is performed if a username is passed.

    To read the users from a csv (single 'users' column),
    pass the path to a csv along with the --csv flag:

        watchlists excluded-users add WATCHLIST CSV_PATH --csv
    """
    client = ctx.obj()

    users = _get_user_ids(client, users, csv)

    client.watchlists.v1.add_excluded_users(watchlist, users)
    console.print(f"Successfully excluded users from watchlist with ID: '{watchlist}'")


@excluded_users.command("remove", cls=IncydrCommand)
@watchlist_arg
@click.argument("users")
@csv_option
@click.pass_context
def remove_excluded_users(ctx: Context, watchlist: str, users: str, csv: bool = False):
    """
    Remove excluded users from a watchlist.

        watchlists excluded-users remove WATCHLIST USERS --csv

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    USERS is a comma-delimited string of user IDs or usernames to add to the case.
    An additional lookup is performed if a username is passed.

    To read the users from a csv (single 'users' column),
    pass the path to a csv along with the --csv flag:

        watchlists excluded-users remove WATCHLIST CSV_PATH --csv

    """
    client = ctx.obj()

    users = _get_user_ids(client, users, csv)

    client.watchlists.v1.remove_excluded_users(watchlist, users)
    console.print(
        f"Successfully removed excluded users from watchlist with ID: '{watchlist}'"
    )


@excluded_users.command("show", cls=IncydrCommand)
@watchlist_arg
@click.argument("user")
@single_format_option
@click.pass_context
def show_excluded_user(ctx: Context, watchlist: str, user: str, format_: SingleFormat):
    """
    Show details for a user excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    user = client.watchlists.v1.get_excluded_user(watchlist, user)
    _output_single_result(
        user, f"Excluded User: {user.username}", format_, client.settings.use_rich
    )


@excluded_users.command("list", cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_excluded_users(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List users excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    users = client.watchlists.v1.list_excluded_users(watchlist)
    _output_results(users.excluded_users, WatchlistUser, format_, columns)


@watchlists.group(cls=IncydrGroup)
def directory_groups():
    """
    View and manage directory groups included on a watchlist.

    Directory groups are pushed to Code42 from SCIM or User Directory Sync.
    Retrieve information on the directory groups in your environment using
    the `incydr directory-groups` command group.
    """


@directory_groups.command("add", cls=IncydrCommand)
@watchlist_arg
@click.argument("group_ids")
@click.pass_context
def add_directory_group(ctx: Context, watchlist: str, group_ids: str):
    """
    Include directory groups on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    GROUP_IDS is a comma-delimited list of directory group IDs.
    """
    client = ctx.obj()
    client.watchlists.v1.add_directory_groups(
        watchlist, [i.strip() for i in group_ids.split(",")]
    )
    console.print(
        f"Successfully included directory groups to watchlist with ID: {watchlist}"
    )


@directory_groups.command("remove", cls=IncydrCommand)
@watchlist_arg
@click.argument("group_ids")
@click.pass_context
def remove_directory_group(ctx: Context, watchlist: str, group_ids: str):
    """
    Remove included directory groups from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    GROUP_IDS is a comma-delimited list of directory group IDs.
    """
    client = ctx.obj()
    client.watchlists.v1.remove_directory_groups(
        watchlist, [i.strip() for i in group_ids.split(",")]
    )
    console.print(
        f"Successfully removed included directory groups from watchlist with ID: {watchlist}"
    )


@directory_groups.command("show", cls=IncydrCommand)
@watchlist_arg
@click.argument("group_id")
@single_format_option
@click.pass_context
def show_directory_group(
    ctx: Context, watchlist: str, group_id: str, format_: SingleFormat
):
    """
    Show details for a directory group included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    group = client.watchlists.v1.get_directory_group(watchlist, group_id)
    _output_single_result(
        group, f"Directory Group: {group.name}", format_, client.settings.use_rich
    )


@directory_groups.command("list", cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_directory_groups(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List directory groups included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    groups = client.watchlists.v1.list_directory_groups(watchlist)
    _output_results(
        groups.included_directory_groups, IncludedDirectoryGroup, format_, columns
    )


@watchlists.group(cls=IncydrGroup)
def departments():
    """
    View and manage departments included on a watchlist.

    Departments are pushed to Code42 from SCIM or User Directory Sync.
    Retrieve information on the departments in your environment using
    the `incydr departments` command group.
    """


@departments.command("add", cls=IncydrCommand)
@watchlist_arg
@click.argument("departments")
@click.pass_context
def add_department(ctx: Context, watchlist: str, departments: str):
    """
    Include departments on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    DEPARTMENTS is a comma-delimited list of department names.
    """
    client = ctx.obj()
    client.watchlists.v1.add_departments(
        watchlist, [i.strip() for i in departments.split(",")]
    )
    console.print(
        f"Successfully included departments to watchlist with ID: {watchlist}"
    )


@departments.command("remove", cls=IncydrCommand)
@watchlist_arg
@click.argument("departments")
@click.pass_context
def remove_department(ctx: Context, watchlist: str, departments: str):
    """
    Remove included departments from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.

    DEPARTMENTS is a comma-delimited list of department names.
    """
    client = ctx.obj()
    client.watchlists.v1.remove_departments(
        watchlist, [i.strip() for i in departments.split(",")]
    )
    console.print(
        f"Successfully removed included departments from watchlist with ID: {watchlist}"
    )


@departments.command("show", cls=IncydrCommand)
@watchlist_arg
@click.argument("department")
@single_format_option
@click.pass_context
def show_department(
    ctx: Context, watchlist: str, department: str, format_: SingleFormat
):
    """
    Show details for a department included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
    """
    client = ctx.obj()
    dep = client.watchlists.v1.get_department(watchlist, department)
    _output_single_result(
        dep, f"Department: {dep.name}", format_, client.settings.use_rich
    )


@departments.command("list", cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@click.pass_context
def list_departments(
    ctx: Context, watchlist: str, format_: TableFormat, columns: str = None
):
    """
    List departments included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: DEPARTING_EMPLOYEE) or ID.
    CUSTOM watchlists must be specified by ID.
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


def _output_single_result(model, title, format_, use_rich=True):
    if format_ == SingleFormat.rich and use_rich:
        console.print(Panel.fit(model_as_card(model), title=title))
    elif format_ == SingleFormat.json:
        console.print_json(model.json())
    else:  # format == "raw-json"
        console.print(model.json(), highlight=False)
