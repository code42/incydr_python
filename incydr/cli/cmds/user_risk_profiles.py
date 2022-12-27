from functools import lru_cache
from pathlib import Path
from typing import Optional

import click
from click import Context
from pydantic import Field
from requests import HTTPError
from rich.panel import Panel
from rich.progress import track

from incydr._core.models import CSVModel
from incydr._core.models import Model
from incydr._user_risk_profiles.client import DateParseError
from incydr._user_risk_profiles.models import UserRiskProfile
from incydr.cli import console
from incydr.cli import init_client
from incydr.cli import log_file_option
from incydr.cli import log_level_option
from incydr.cli import render
from incydr.cli.cmds.options.output_options import columns_option
from incydr.cli.cmds.options.output_options import input_format_option
from incydr.cli.cmds.options.output_options import single_format_option
from incydr.cli.cmds.options.output_options import SingleFormat
from incydr.cli.cmds.options.output_options import table_format_option
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.cmds.options.profile_filter_options import profile_filter_options
from incydr.cli.cmds.options.utils import user_lookup_callback
from incydr.cli.cmds.users import users
from incydr.cli.cmds.utils import user_lookup
from incydr.cli.core import incompatible_with
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.utils import model_as_card


class UpdateCloudAliasesCSV(CSVModel):
    user: str = Field(csv_aliases=["user", "user_id", "username", "id", "userId"])
    cloud_alias: str = Field(csv_aliases=["cloudAlias", "cloud_alias", "alias"])


class UpdateCloudAliasesJSON(Model):
    user: str
    cloud_alias: str


@users.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def risk_profiles(ctx, log_level, log_file):
    """View and manage user risk profiles."""
    init_client(ctx, log_level, log_file)


@risk_profiles.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@profile_filter_options
@click.pass_context
def list_(
    ctx: Context,
    format_: TableFormat,
    columns: Optional[str],
    manager: Optional[str],
    title: Optional[str],
    division: Optional[str],
    department: Optional[str],
    employment_type: Optional[str],
    country: Optional[str],
    region: Optional[str],
    locality: Optional[str],
    active: Optional[bool],
    deleted: Optional[bool],
    support_user: Optional[bool],
):
    """
    List user risk profiles.
    """
    client = ctx.obj()
    profiles = client.user_risk_profiles.v1.iter_all(
        manager_id=manager,
        title=title,
        division=division,
        department=department,
        employment_type=employment_type,
        country=country,
        region=region,
        locality=locality,
        active=active,
        deleted=deleted,
        support_user=support_user,
    )

    if format_ == TableFormat.csv:
        render.csv(UserRiskProfile, profiles, columns=columns, flat=True)
    elif format_ == TableFormat.table:
        columns = columns or [
            "username",
            "user_id",
            "display_name",
            "cloud_aliases",
            "active",
            "start_date",
            "end_date",
        ]
        render.table(UserRiskProfile, profiles, columns=columns, flat=False)
    else:
        printed = False
        if format_ == TableFormat.json_pretty:
            for p in profiles:
                printed = True
                console.print_json(p.json())
        else:
            for p in profiles:
                printed = True
                click.echo(p.json())
        if not printed:
            console.print("No results found.")


@risk_profiles.command(cls=IncydrCommand)
@click.argument("user", callback=user_lookup_callback)
@single_format_option
@click.pass_context
def show(ctx: Context, user: str, format_: SingleFormat):
    """
    Show details for a user risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.
    """
    client = ctx.obj()
    profile = client.user_risk_profiles.v1.get_user_risk_profile(user)
    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(
            Panel.fit(model_as_card(profile), title=f"Risk Profile {profile.username}")
        )
    elif format_ == SingleFormat.json_pretty:
        console.print_json(profile.json())
    else:
        click.echo(profile.json())


@risk_profiles.command(cls=IncydrCommand)
@click.argument("user", callback=user_lookup_callback)
@click.option(
    "--start-date",
    default=None,
    help="Update a user's starting date. Accepts a date in yyyy-MM-dd (UTC) format.",
)
@click.option(
    "--end-date",
    default=None,
    help="Update a user's departure date. Accepts a date in yyyy-MM-dd (UTC) format.",
)
@click.option(
    "--notes", default=None, help="Update the optional notes on a user's profile."
)
@click.option(
    "--clear-start-date",
    is_flag=True,
    default=False,
    help="Clear the start date on a user's profile. Incompatible with --start-date.",
    cls=incompatible_with("start_date"),
)
@click.option(
    "--clear-end-date",
    is_flag=True,
    default=False,
    help="Clear the end date on a user's profile. Incompatible with --end-date.",
    cls=incompatible_with("end_date"),
)
@click.option(
    "--clear-notes",
    is_flag=True,
    default=False,
    help="Clear the notes on a user's profile. Incompatible with --notes.",
    cls=incompatible_with("notes"),
)
@click.pass_context
def update(
    ctx: Context,
    user,
    start_date=None,
    end_date=None,
    notes=None,
    clear_start_date=None,
    clear_end_date=None,
    clear_notes=None,
):
    """
    Update a user risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.
    """
    if not any(
        [start_date, end_date, notes, clear_start_date, clear_end_date, clear_notes]
    ):
        raise click.UsageError(
            "At least one of --start-date, --end-date, or --notes, or one of their corresponding clear flags, "
            "is required to update a user risk profile."
        )

    client = ctx.obj()

    if clear_start_date:
        start_date = ""
    if clear_end_date:
        end_date = ""
    if clear_notes:
        notes = ""

    try:
        updated_profile = client.user_risk_profiles.v1.update(
            user, notes, start_date, end_date
        )
        if client.settings.use_rich:
            console.print(
                Panel.fit(
                    model_as_card(updated_profile), title="Updated User Risk Profile"
                )
            )
        else:
            console.print(updated_profile.json(), highlight=False)
    except DateParseError as err:
        raise err


@risk_profiles.command(cls=IncydrCommand)
@click.argument("user", callback=user_lookup_callback)
@click.argument("cloud-alias")
@click.pass_context
def add_cloud_alias(ctx: Context, user, cloud_alias):
    """
    Add a cloud alias to a user risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.

    A cloud alias is the username an employee uses to access cloud services such as Google Drive or Box.
    Adding a cloud alias allows Incydr to link a user's cloud activity with their Code42 username.
    Each user has a default cloud alias of their Code42 username. You can add one additional alias.
    """
    client = ctx.obj()
    client.user_risk_profiles.v1.add_cloud_alias(user, cloud_alias)
    console.print(f"Cloud alias successfully added to user '{user}")


@risk_profiles.command(cls=IncydrCommand)
@click.argument("user", callback=user_lookup_callback)
@click.argument("cloud-alias")
@click.pass_context
def remove_cloud_alias(ctx: Context, user, cloud_alias):
    """
    Remove a cloud alias from a user risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.
    """
    client = ctx.obj()
    client.user_risk_profiles.v1.delete_cloud_alias(user, cloud_alias)
    console.print(f"Cloud alias successfully removed from user '{user}")


@risk_profiles.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@click.pass_context
def bulk_add_cloud_aliases(ctx: Context, file: Path, format_: str):
    """
    Bulk add cloud aliases to user risk profiles.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Required CSV columns:

     * `user` - User ID or username of the user risk profile. Performs an additional lookup if username is passed.
     * `cloud_alias` - The cloud alias to remove from the profile.
    """
    client = ctx.obj()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UpdateCloudAliasesCSV.parse_csv(file)
    else:
        models = UpdateCloudAliasesJSON.parse_json_lines(file)

    try:
        for row in track(
            models,
            description="Adding cloud aliases...",
            transient=True,
        ):
            client.user_risk_profiles.v1.add_cloud_alias(
                resolve_username(row.user), row.cloud_alias
            )
    except ValueError as err:
        console.print(f"[red]Error:[/red] {err}")
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")


@risk_profiles.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@click.pass_context
def bulk_remove_cloud_aliases(ctx: Context, file: Path, format_: str):
    """
    Bulk remove cloud aliases from user risk profiles.

    Takes a single arg `FILE` which specifies the path to the file (use "-" to read from stdin).

    File format can either be CSV or [JSON Lines format](https://jsonlines.org) (Default is CSV).

    Required CSV columns:

     * `user` - User ID or username of the user risk profile. Performs an additional lookup if username is passed.
     * `cloud_alias` - The cloud alias to remove from the profile.
    """
    client = ctx.obj()

    @lru_cache()
    def resolve_username(user):
        if user is None:
            return
        elif "@" in user:
            return user_lookup(client, user)
        else:  # assume user_id
            return user

    if format_ == "csv":
        models = UpdateCloudAliasesCSV.parse_csv(file)
    else:
        models = UpdateCloudAliasesJSON.parse_json_lines(file)

    try:
        for row in track(
            models,
            description="Removing cloud aliases...",
            transient=True,
        ):
            client.user_risk_profiles.v1.delete_cloud_alias(
                resolve_username(row.user), row.cloud_alias
            )
    except ValueError as err:
        console.print(f"[red]Error:[/red] {err}")
    except HTTPError as err:
        console.print(f"[red]Error:[/red] {err.response.text}")
