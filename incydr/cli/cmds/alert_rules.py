import click
from click import Context
from rich.table import Table

from incydr._alert_rules.client import MissingUsernameCriterionError
from incydr._alert_rules.models.response import RuleDetails
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
from incydr.cli.core import IncydrCommand
from incydr.cli.core import IncydrGroup
from incydr.cli.render import measure_renderable
from incydr.utils import list_as_panel
from incydr.utils import model_as_card


MAX_USER_DISPLAY_COUNT = 25


@click.group(cls=IncydrGroup)
@log_level_option
@log_file_option
@click.pass_context
def alert_rules(ctx, log_level, log_file):
    """View and manage alert rules."""
    init_client(ctx, log_level, log_file)


@alert_rules.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@click.pass_context
def list_(ctx: Context, format_: TableFormat = None, columns: str = None):
    """
    List all rules.
    """
    client = ctx.obj()
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
    elif format_ == TableFormat.json:
        for rule in rules:
            console.print_json(rule.json())
    else:
        for rule in rules:
            click.echo(rule.json())


@alert_rules.command(cls=IncydrCommand)
@single_format_option
@click.argument("rule-id")
@click.pass_context
def show(ctx: Context, rule_id: str, format_: SingleFormat = None):
    """
    Show details for a single rule.

    If using `rich`, also retrieve the username filter for the rule (if it exists).
    """
    client = ctx.obj()
    rule = client.alert_rules.v2.get_rule(rule_id)

    if format_ == SingleFormat.json:
        console.print_json(rule.json())
        return
    if format_ == SingleFormat.raw_json:
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
@click.pass_context
def enable(ctx: Context, rule_ids: str):
    """
    Enable a single rule or a set of rules.

    Where RULE-IDS is a comma-delimited list of rule IDs to enable.
    """
    client = ctx.obj()
    client.alert_rules.v2.enable_rules([r.strip() for r in rule_ids.split(",")])
    console.print("Successfully enabled rule(s).")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-ids")
@click.pass_context
def disable(ctx: Context, rule_ids: str):
    """
    Disable a single rule or a set of rules.
    """
    client = ctx.obj()
    client.alert_rules.v2.disable_rules([r.strip() for r in rule_ids.split(",")])
    console.print("Successfully disabled rule(s).")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-id")
@click.pass_context
def remove_all_users(ctx: Context, rule_id: str):
    """
    Remove ALL users from a rule's username filter.

    Note that the removed users could become either included or excluded from the rule,
    depending on the rule's configuration.
    """
    client = ctx.obj()
    client.alert_rules.v2.remove_all_users(rule_id)
    console.print(f"Successfully removed all users from rule '{rule_id}'.")


@alert_rules.command(cls=IncydrCommand)
@click.argument("rule-id")
@single_format_option
@click.pass_context
def list_users(ctx: Context, rule_id: str, format_: SingleFormat = None):
    """
    Lists the usernames on the rule's username filter.

    Note that users could either be included on or excluded from the rule depending on the rule's configuration.
    """
    client = ctx.obj()
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
    elif format_ == SingleFormat.json:
        console.print_json(username_filter.json())
    else:
        click.echo(username_filter.json())
