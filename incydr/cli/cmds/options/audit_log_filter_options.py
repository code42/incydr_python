import click

start_option = click.option(
    "--start",
    default=None,
    help="The beginning of the date range in which to look for audit log events. Accepts a date/time in yyyy-MM-dd (UTC) or"
    "yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format.",
)
end_option = click.option(
    "--end",
    default=None,
    help="The end of the date range in which to look for audit log events, argument format options are the same as `--start`.",
)
actor_ids_option = click.option(
    "--actor-ids",
    default=None,
    help="Filter events by the actor IDs. Comma-delimited string of actor user IDs.",
)
actor_ip_addresses_option = click.option(
    "--actor-ip-addresses",
    default=None,
    help="Filter events by actor IP addresses. Comma-delimited string of actor IP addresses.",
)
actor_names_option = click.option(
    "--actor-names",
    default=None,
    help="Filter events by actor usernames. Comma-delimited string of actor usernames.",
)
event_types_option = click.option(
    "--event-types",
    default=None,
    help="Filter events by event type. Comma delimited string of event types.",
)
resource_ids_option = click.option(
    "--resource-ids",
    default=None,
    help="Filter events by resource ID. Comma delimited string of resource IDs.",
)
user_types_option = click.option(
    "--user-types",
    default=None,
    help="Filter events by user type. Comma delimited string of user types.",
)


def filter_options(f):
    f = start_option(f)
    f = end_option(f)
    f = actor_ids_option(f)
    f = actor_ip_addresses_option(f)
    f = actor_names_option(f)
    f = event_types_option(f)
    f = resource_ids_option(f)
    f = user_types_option(f)
    return f
