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
from _incydr_cli.cmds.options.profile_filter_options import profile_filter_options
from _incydr_cli.cmds.options.utils import user_lookup_callback
from _incydr_cli.cmds.utils import deprecation_warning
from _incydr_cli.core import incompatible_with
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.exceptions import DateParseError
from _incydr_sdk.risk_profiles.models import RiskProfile
from _incydr_sdk.utils import model_as_card

# Deprecated September 2024.
DEPRECATION_TEXT = "DeprecationWarning: Risk Profile commands are deprecated. Use the 'incydr actors' command group instead."


@click.group(cls=IncydrGroup)
@logging_options
def risk_profiles():
    """View and manage risk profiles."""
    deprecation_warning(DEPRECATION_TEXT)


@risk_profiles.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@profile_filter_options
@logging_options
def list_(
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
    List risk profiles.
    """
    client = Client()
    profiles = client.risk_profiles.v1.iter_all(
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
        render.csv(RiskProfile, profiles, columns=columns, flat=True)
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
        render.table(RiskProfile, profiles, columns=columns, flat=False)
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
@logging_options
def show(
    user: str,
    format_: SingleFormat,
):
    """
    Show details for a risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.
    """
    client = Client()
    profile = client.risk_profiles.v1.get_risk_profile(user)
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
@logging_options
def update(
    user,
    start_date=None,
    end_date=None,
    notes=None,
    clear_start_date=None,
    clear_end_date=None,
    clear_notes=None,
):
    """
    Update a risk profile.

    Accepts a user ID or a username.  Performs an additional lookup if a username is passed.
    """
    if not any(
        [start_date, end_date, notes, clear_start_date, clear_end_date, clear_notes]
    ):
        raise click.UsageError(
            "At least one of --start-date, --end-date, or --notes, or one of their corresponding clear flags, "
            "is required to update a risk profile."
        )

    client = Client()

    if clear_start_date:
        start_date = ""
    if clear_end_date:
        end_date = ""
    if clear_notes:
        notes = ""

    try:
        updated_profile = client.risk_profiles.v1.update(
            user, notes, start_date, end_date
        )
        if client.settings.use_rich:
            console.print(
                Panel.fit(model_as_card(updated_profile), title="Updated Risk Profile")
            )
        else:
            console.print(updated_profile.json(), highlight=False)
    except DateParseError as err:
        raise err
