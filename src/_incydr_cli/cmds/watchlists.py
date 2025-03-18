from typing import Optional
from uuid import UUID

import click
import requests
from boltons.iterutils import chunked
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
from _incydr_cli.cmds.options.utils import actor_lookup_callback
from _incydr_cli.cmds.options.utils import user_lookup_callback
from _incydr_cli.cmds.utils import actor_lookup
from _incydr_cli.cmds.utils import deprecation_warning
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
from _incydr_sdk.watchlists.models.responses import WatchlistActor
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
        return client.watchlists.v2.get_id_by_name(value)


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
    "--actor",
    default=None,
    help="Filter by watchlists where the actor is a member.  Accepts an actor ID or actor name.  Performs an additional lookup if an actor name is passed",
    callback=actor_lookup_callback,
)
@click.option(
    "--user",
    default=None,
    help="DEPRECATED. Use Actor instead. Filter by watchlists where the user is a member.  Accepts a user ID or a username.  Performs an additional lookup if a username is passed",
    callback=user_lookup_callback,
)
@table_format_option
@columns_option
@logging_options
def list_(
    actor: str = None,
    user: str = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List watchlists.
    """
    if user and not actor:
        actor = user
    client = Client()
    watchlists = client.watchlists.v2.iter_all(actor_id=actor)
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

    * included_actors
    * excluded_actors
    * included_departments
    * included_directory_groups

    Lists of actors will be truncated to only display the first 25 members, use the `list-included-actors` and `list-excluded-actors`
    commands respectively to see more details.

    If not using `rich`, outputs watchlist information in JSON without additional membership summary information.
    """
    client = Client()
    watchlist_response = client.watchlists.v2.get(watchlist)

    if not client.settings.use_rich:
        click.echo(watchlist_response.json())
        return

    included_actors = client.watchlists.v2.list_included_actors(
        watchlist
    ).included_actors
    excluded_actors = client.watchlists.v2.list_excluded_actors(
        watchlist
    ).excluded_actors
    departments = client.watchlists.v2.list_departments(watchlist).included_departments
    dir_groups = client.watchlists.v2.list_directory_groups(
        watchlist
    ).included_directory_groups
    t = Table(title=f"{watchlist_response.list_type} Watchlist")
    t.add_column("Stats")

    tables = []
    if included_actors:
        tables.append(
            models_as_table(WatchlistActor, included_actors[:MAX_USER_DISPLAY_COUNT])
        )
        t.add_column("Included Users")
    if excluded_actors:
        tables.append(
            models_as_table(WatchlistActor, excluded_actors[:MAX_USER_DISPLAY_COUNT])
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
    watchlist = client.watchlists.v2.create(watchlist_type, title, description)
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
    client.watchlists.v2.delete(watchlist)
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
    client.watchlists.v2.update(watchlist_id, title, description)
    console.print(f"Successfully updated watchlist with ID: '{watchlist_id}'.")


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.option(
    "--actors",
    default=None,
    type=FileOrString(),
    help="List of actor IDs or actor names to include on the watchlist. "
    "An additional lookup is performed if an actor name is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'actor' "
    "column if prefixed with '@', e.g. '--actors @actors.csv'.",
)
@click.option(
    "--excluded-actors",
    default=None,
    type=FileOrString(),
    help="List of actor IDs or actor names to exclude from the watchlist. "
    "An additional lookup is performed if an actor name is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'actor' "
    "column if prefixed with '@', e.g. '--excluded-actors @actors.csv'.",
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
@click.option(
    "--users",
    default=None,
    type=FileOrString(),
    help="DEPRECATED. Use --actors instead. List of user IDs or usernames to include on the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@click.option(
    "--excluded-users",
    default=None,
    type=FileOrString(),
    help="DEPRECATED. Use --excluded-actors instead. List of user IDs or usernames to exclude from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'user' "
    "column if prefixed with '@', e.g. '--users @users.csv'.",
)
@input_format_option
@logging_options
def add(
    watchlist: str,
    actors=None,
    excluded_actors=None,
    departments=None,
    directory_groups=None,
    users=None,
    excluded_users=None,
    format_=None,
):
    """
    Manage watchlist membership by including or excluding individual actors and/or groups.

    Add any of the following members to a watchlist with the corresponding options:

    * actors
    * excluded-actors
    * departments
    * directory-groups

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.

    If adding or excluding more than 100 actors in a single run, the CLI will automatically batch
    requests due to a limit of 100 per request on the backend.
    """
    client = Client()

    if users and not actors:
        actors = users
    if excluded_users and not excluded_actors:
        excluded_actors = excluded_users

    # Add included actors
    if actors:
        actor_ids, errors = _get_actor_ids(client, actors, format_=format_)
        succeeded = 0
        for chunk in chunked(actor_ids, size=100):
            try:
                client.watchlists.v2.add_included_actors(watchlist, chunk)
                console.print(
                    f"Successfully included {len(chunk)} actors on watchlist with ID: '{watchlist}'"
                )
                succeeded += len(chunk)
            except requests.HTTPError as err:
                if "Actor not found" in err.response.text:
                    console.print(
                        "Problem processing batch of actors, will attempt each individually."
                    )
                    chunk_succeeded = 0
                    for actor in chunk:
                        try:
                            client.watchlists.v2.add_included_actors(watchlist, actor)
                            succeeded += 1
                            chunk_succeeded += 1
                        except requests.HTTPError as err:
                            client.settings.logger.error(
                                f"Problem adding actorId={actor} to watchlist={watchlist}: {err.response.text}"
                            )
                            errors.append(actor)
                    console.print(
                        f"Successfully included {chunk_succeeded} users on watchlist with ID: '{watchlist}'"
                    )
                else:
                    raise err
        if errors:
            console.print("[red]The following usernames/user IDs were not found:")
            console.print("\t" + "\n\t".join(errors))

    # Add excluded actors
    if excluded_actors:
        succeeded = 0
        actor_ids, errors = _get_actor_ids(client, excluded_actors, format_=format_)
        for chunk in chunked(actor_ids, size=100):
            try:
                client.watchlists.v2.add_excluded_actors(watchlist, chunk)
                console.print(
                    f"Successfully excluded {len(chunk)} actors from watchlist with ID: '{watchlist}'"
                )
                succeeded += len(chunk)
            except requests.HTTPError as err:
                if "Actor not found" in err.response.text:
                    console.print(
                        "Problem processing batch of actors, will attempt each individually."
                    )
                    chunk_succeeded = 0
                    for actor in chunk:
                        try:
                            client.watchlists.v2.add_excluded_actors(watchlist, actor)
                            succeeded += 1
                            chunk_succeeded += 1
                        except requests.HTTPError as err:
                            client.settings.logger.error(
                                f"Problem excluding actorId={actor} from watchlist={watchlist}: {err.response.text}"
                            )
                            errors.append(actor)
                    console.print(
                        f"Successfully excluded {chunk_succeeded} users from watchlist with ID: '{watchlist}'"
                    )
                else:
                    raise err
        if errors:
            console.print("[red]The following actornames/actor IDs were not found:")
            console.print("\t" + "\n\t".join(errors))

    # Add departments
    if departments:
        client.watchlists.v2.add_departments(
            watchlist, [i.strip() for i in departments.split(",")]
        )
        console.print(
            f"Successfully included departments to watchlist with ID: {watchlist}"
        )

    # Add directory groups
    if directory_groups:
        client.watchlists.v2.add_directory_groups(
            watchlist, [i.strip() for i in directory_groups.split(",")]
        )
        console.print(
            f"Successfully included directory groups to watchlist with ID: {watchlist}"
        )


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@click.option(
    "--actors",
    default=None,
    type=FileOrString(),
    help="List of actor IDs or actor names to remove from the watchlist. "
    "An additional lookup is performed if an actor name is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'actor' "
    "column if prefixed with '@', e.g. '--actors @actors.csv'. "
    "File should have a single 'actor' field.  File format can either be CSV or JSON Lines format, "
    "as specified with the --format option (Default is CSV).",
)
@click.option(
    "--excluded-actors",
    default=None,
    type=FileOrString(),
    help="List of actor IDs or actor names to remove from the watchlist. "
    "An additional lookup is performed if an actor name is passed. Argument can be "
    "passed as a comma-delimited string or from a CSV file with a single 'actor' "
    "column if prefixed with '@', e.g. '--excluded-actors @actors.csv'. "
    "File should have a single 'actor' field.  File format can either be CSV or JSON Lines format, "
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
@click.option(
    "--users",
    default=None,
    type=FileOrString(),
    help="DEPRECATED. Use --actors instead. List of included user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed.Argument can be "
    "passed as a comma-delimited string or as a file if prefixed with '@', e.g. '--users @users.csv'. "
    "File should have a single 'user' field.  File format can either be CSV or JSON Lines format, "
    "as specified with the --format option (Default is CSV).",
)
@click.option(
    "--excluded-users",
    default=None,
    type=FileOrString(),
    help="DEPRECATED. Use --excluded-actors instead. List of excluded user IDs or usernames to remove from the watchlist. "
    "An additional lookup is performed if a username is passed. Argument can be "
    "passed as a comma-delimited string or as a file if prefixed with '@', e.g. '--users @users.csv'. "
    "File should have a single 'user' field.  File format can either be CSV or JSON Lines format, "
    "as specified with the --format option (Default is CSV).",
)
@input_format_option
@logging_options
def remove(
    watchlist: str,
    actors=None,
    excluded_actors=None,
    departments=None,
    directory_groups=None,
    users=None,
    excluded_users=None,
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

    If removing more than users or exclusions in a single run, the CLI will automatically batch
    requests due to a limit of 100 per request on the backend.
    """
    client = Client()

    if users and not actors:
        actors = users
    if excluded_users and not excluded_actors:
        excluded_actors = excluded_users

    # Remove included users
    if actors:
        actor_ids, errors = _get_actor_ids(client, actors, format_=format_)
        succeeded = 0
        for chunk in chunked(actor_ids, size=100):
            try:
                client.watchlists.v2.remove_included_actors(watchlist, chunk)
                console.print(
                    f"Successfully removed {len(chunk)} included actors on watchlist with ID: '{watchlist}'"
                )
                succeeded += len(chunk)
            except requests.HTTPError as err:
                if "Actor not found" in err.response.text:
                    console.print(
                        "Problem processing batch of actors, will attempt each individually."
                    )
                    chunk_succeeded = 0
                    for actor in chunk:
                        try:
                            client.watchlists.v2.remove_included_actors(
                                watchlist, actor
                            )
                            succeeded += 1
                            chunk_succeeded += 1
                        except requests.HTTPError as err:
                            client.settings.logger.error(
                                f"Problem removing actorId={actor} from watchlist={watchlist}: {err.response.text}"
                            )
                            errors.append(actor)
                    console.print(
                        f"Successfully removed {chunk_succeeded} actors from watchlist with ID: '{watchlist}'"
                    )
                else:
                    raise err
        if errors:
            console.print("[red]The following actornames/actor IDs were not found:")
            console.print("\t" + "\n\t".join(errors))

    # Remove excluded users
    if excluded_actors:
        actor_ids, errors = _get_actor_ids(client, excluded_actors, format_=format_)
        succeeded = 0
        for chunk in chunked(actor_ids, size=100):
            try:
                client.watchlists.v2.remove_excluded_actors(watchlist, chunk)
                console.print(
                    f"Successfully removed {len(chunk)} excluded actors from watchlist with ID: '{watchlist}'"
                )
                succeeded += len(chunk)
            except requests.HTTPError as err:
                if "User not found" in err.response.text:
                    console.print(
                        "Problem processing batch of actors, will attempt each individually."
                    )
                    chunk_succeeded = 0
                    for actor in chunk:
                        try:
                            client.watchlists.v2.remove_excluded_actors(
                                watchlist, actor
                            )
                            succeeded += 1
                            chunk_succeeded += 1
                        except requests.HTTPError as err:
                            client.settings.logger.error(
                                f"Problem removing excluded actorId={actor} from watchlist={watchlist}: {err.response.text}"
                            )
                            errors.append(actor)
                    console.print(
                        f"Successfully removed {chunk_succeeded} excluded actors from watchlist with ID: '{watchlist}'"
                    )
                else:
                    raise err
            if errors:
                console.print("[red]The following actornames/actor IDs were not found:")
                console.print("\t" + "\n\t".join(errors))

    # Remove departments
    if departments:
        client.watchlists.v2.remove_departments(
            watchlist, [i.strip() for i in departments.split(",")]
        )
        console.print(
            f"Successfully removed departments from watchlist with ID: {watchlist}"
        )

    # Remove directory groups
    if directory_groups:
        client.watchlists.v2.remove_directory_groups(
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
    members = list(client.watchlists.v2.iter_all_members(watchlist))
    _output_results(members, WatchlistActor, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_included_actors(
    watchlist: str,
    format_: str,
    columns: Optional[str],
):
    """
    List actors explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    users = list(client.watchlists.v2.iter_all_included_actors(watchlist))
    _output_results(users, WatchlistActor, format_, columns)


@watchlists.command(cls=IncydrCommand)
@watchlist_arg
@table_format_option
@columns_option
@logging_options
def list_excluded_actors(
    watchlist: str,
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List actors excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    client = Client()
    users = list(client.watchlists.v2.iter_all_excluded_actors(watchlist))
    _output_results(users, WatchlistActor, format_, columns)


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
    groups = list(client.watchlists.v2.iter_all_directory_groups(watchlist))
    _output_results(groups, IncludedDirectoryGroup, format_, columns)


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
    deps = list(client.watchlists.v2.iter_all_departments(watchlist))
    _output_results(deps, IncludedDepartment, format_, columns)


def _get_actor_ids(client, actors, format_=None):
    ids, errors = [], []
    if isinstance(actors, str):
        for actor in actors.split(","):
            try:
                actor = actor_lookup(client, actor)
                ids.append(actor)
            except ValueError:
                client.settings.logger.error(
                    f"Problem looking up actorId for actor name: {actor}"
                )
                errors.append(actor)
    else:
        if format_ == "csv":
            actors = UserCSV.parse_csv(actors)
        else:
            actors = UserJSON.parse_json_lines(actors)
        for row in track(
            actors,
            description="Reading actors...",
            transient=True,
        ):
            try:
                actor_id = actor_lookup(client, row.user)
                ids.append(actor_id)
            except ValueError:
                client.settings.logger.error(
                    f"Problem looking up actorId for actor name: {row.user}"
                )
                errors.append(row.user)
    return ids, errors


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


# Deprecated 2025-03. Will be removed 2026-03.


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
    DEPRECATED. List users explicitly included on a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    deprecation_warning("DEPRECATED. Use list_included_actors instead.")
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
    DEPRECATED. List users excluded from a watchlist.

    WATCHLIST can be specified by watchlist type (ex: `DEPARTING_EMPLOYEE`) or ID.
    `CUSTOM` watchlists must be specified by title or ID.
    """
    deprecation_warning("DEPRECATED. Use list_excluded_actors instead.")

    client = Client()
    users = client.watchlists.v1.list_excluded_users(watchlist)
    _output_results(users.excluded_users, WatchlistUser, format_, columns)
