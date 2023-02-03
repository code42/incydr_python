from typing import Optional

import click
from rich.table import Table

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
from _incydr_cli.render import measure_renderable
from _incydr_sdk.alert_rules.client import MissingUsernameCriterionError
from _incydr_sdk.alert_rules.models.response import RuleDetails
from _incydr_sdk.core.client import Client
from _incydr_sdk.utils import list_as_panel
from _incydr_sdk.utils import model_as_card


MAX_USER_DISPLAY_COUNT = 25


@click.group(cls=IncydrGroup)
@logging_options
def alert_rules():
    """View and manage alert rules."""


@alert_rules.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@logging_options
def list_(
    format_: TableFormat,
    columns: Optional[str],
):
    """
    List all rules.
    """
    client = Client()
    rules = client.alert_rules.v2.iter_all()

    if format_ == TableFormat.table:
        if not columns:
            columns = [
                "id",
                "name",
                "severity",
                "is_enabled",
                "created_at",
                "created_by",
                "modified_at",
                "modified_by",
                "description",
            ]
        render.table(RuleDetails, rules, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(RuleDetails, rules, columns=columns, flat=True)
    elif format_ == TableFormat.json_pretty:
        for rule in rules:
            console.print_json(rule.json())
    else:
        for rule in rules:
            click.echo(rule.json())


@alert_rules.command(cls=IncydrCommand)
@single_format_option
@click.argument("rule-id")
@logging_options
def show(
    rule_id: str,
    format_: SingleFormat,
):
    """
    Show details for a single rule.

    If using `rich`, also retrieve the username filter for the rule (if it exists).
    """
    client = Client()
    rule = client.alert_rules.v2.get_rule(rule_id)

    if format_ == SingleFormat.json_pretty:
        console.print_json(rule.json())
        return
    if format_ == SingleFormat.json_lines:
        click.echo(rule.json())
        return

    t = Table(title=f"Alert Rule {rule.id}")
    t.add_column("Info")
    tables = []

    try:
        username_filter = client.alert_rules.v2.get_users(rule_id)
        # Pretty sure there is only ever one "user" object whose aliases indicate the usernames on the filter
        usernames = []
        for user in username_filter.users:
            usernames.extend(user.aliases)
        if usernames:
            tables.append(list_as_panel(usernames[:MAX_USER_DISPLAY_COUNT]))
            t.add_column(
                f"{'Include' if username_filter.mode == '0' else 'Exclude'}d Usernames"
            )
    except MissingUsernameCriterionError:
        pass

    if rule.notifications:
        tables.append(model_as_card(rule.notifications))
        t.add_column("Notifications")
    if rule.education:
        tables.append(model_as_card(rule.education))
        t.add_column("Education")
    if rule.vectors:
        tables.append(model_as_card(rule.vectors))
        t.add_column("Vectors")
    if rule.filters:
        tables.append(model_as_card(rule.filters))
        t.add_column("Filters")

    t.add_row(
        model_as_card(
            rule,
            include=[
                "name",
                "description",
                "severity",
                "is_enabled",
                "created_at",
                "created_by",
                "modified_at",
                "modified_by",
                "is_system_rule",
            ],
        ),
        *tables,
    )

    with console.pager():
        # expand console and table so no values get truncated due to size of console, since we're using a pager
        console.width = t.width = measure_renderable(t)
        console.print(t, crop=False, soft_wrap=False, overflow="fold")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-ids")
@logging_options
def enable(
    rule_ids: str,
):
    """
    Enable a single rule or a set of rules.

    Where RULE-IDS is a comma-delimited list of rule IDs to enable.
    """
    client = Client()
    client.alert_rules.v2.enable_rules([r.strip() for r in rule_ids.split(",")])
    console.print("Successfully enabled rule(s).")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-ids")
@logging_options
def disable(
    rule_ids: str,
):
    """
    Disable a single rule or a set of rules.
    """
    client = Client()
    client.alert_rules.v2.disable_rules([r.strip() for r in rule_ids.split(",")])
    console.print("Successfully disabled rule(s).")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-id")
@logging_options
def remove_all_users(
    rule_id: str,
):
    """
    Remove ALL users from a rule's username filter.

    Note that the removed users could become either included or excluded from the rule,
    depending on the rule's configuration.
    """
    client = Client()
    client.alert_rules.v2.remove_all_users(rule_id)
    console.print(f"Successfully removed all users from rule '{rule_id}'.")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-id")
@single_format_option
@logging_options
def list_users(
    rule_id: str,
    format_: SingleFormat,
):
    """
    Lists the usernames on the rule's username filter.

    Note that users could either be included on or excluded from the rule depending on the rule's configuration.
    """
    client = Client()
    try:
        username_filter = client.alert_rules.v2.get_users(rule_id)
    except MissingUsernameCriterionError:
        console.print(f"No results found for rule {rule_id}")
        return

    usernames = []
    for user in username_filter.users:
        usernames.extend(user.aliases)

    if not usernames:
        console.print(f"No results found for rule {rule_id}")
        return

    if format_ == SingleFormat.rich:
        console.print(
            list_as_panel(
                usernames,
                expand=False,
                title=f"{'Include' if username_filter.mode == '0' else 'Exclude'}d Usernames",
            )
        )
    elif format_ == SingleFormat.json_pretty:
        console.print_json(username_filter.json())
    else:
        click.echo(username_filter.json())
