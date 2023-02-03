import click

from _incydr_cli.core import incompatible_with
from _incydr_cli.file_readers import FileOrString

# did not include the following fields to filter by:
# Description, HasAuthSignificantWatchlist, Target, LastModifiedAt,
# LastModifiedBy, StateLastModifiedAt, StateLastModifiedBy

AdvancedQueryIncompatible = incompatible_with(["advanced_query"])

start_option = click.option(
    "--start",
    default=None,
    help="The beginning of the date range in which to look for alerts. Filters by alert creation time. "
    "Accepts a date/time in yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format.",
    cls=incompatible_with(["advanced_query, on"]),
)
end_option = click.option(
    "--end",
    default=None,
    help="The end of the date range in which to look for alerts, argument format options are the same as `--start`.",
    cls=incompatible_with(["advanced_query, on"]),
)
on_option = click.option(
    "--on",
    default=None,
    help="Look for alerts created on the date given, argument forms are the same as `--start`.",
    cls=incompatible_with(["advanced_query, start, end"]),
)

alert_id_option = click.option(
    "--alert-id",
    default=None,
    help="Filter by the unique alert ID.",
    cls=AdvancedQueryIncompatible,
)
type_option = click.option(
    "--type",
    "type_",
    default=None,
    help="Filter by the type of alert. One of [FED_ENDPOINT_EXFILTRATION, FED_CLOUD_SHARE_PERMISSIONS, FED_FILE_TYPE_MISMATCH, FED_FILE_NAME_MATCH, FED_COMPOSITE].",
    cls=AdvancedQueryIncompatible,
)
name_option = click.option(
    "--name",
    default=None,
    help="Filter by the name of the alert.",
    cls=AdvancedQueryIncompatible,
)
actor_option = click.option(
    "--actor",
    default=None,
    help="Filter by the actor (the user who triggered the alert.)",
    cls=AdvancedQueryIncompatible,
)
actor_id_option = click.option(
    "--actor-id",
    default=None,
    help="Filter by the actor ID.",
    cls=AdvancedQueryIncompatible,
)
risk_severity_option = click.option(
    "--risk-severity",
    default=None,
    help="Filter by risk severity.  One of [NO_RISK_INDICATED, LOW, MODERATE, HIGH, CRITICAL].",
    cls=AdvancedQueryIncompatible,
)
state_option = click.option(
    "--state",
    default=None,
    help="Filter by the state of the alert.  One of [OPEN, RESOLVED, IN_PROGRESS, PENDING].",
    cls=AdvancedQueryIncompatible,
)
rule_id_option = click.option(
    "--rule-id",
    default=None,
    help="Filter by the rule ID that corresponds to the rulel which triggered the alert.",
    cls=AdvancedQueryIncompatible,
)
severity_option = click.option(
    "--alert-severity",
    default=None,
    help="Filter by alert severity.  One of [LOW, MEDIUM, HIGH].",
    cls=AdvancedQueryIncompatible,
)

advanced_query_option = click.option(
    "--advanced-query",
    type=FileOrString(),
    default=None,
    help=(
        "A raw JSON alerts query. Useful for when the provided query parameters do not satisfy your requirements.  "
        "Argument can be passed as a string, read from stdin by passing '-', or from a filename if prefixed with '@',"
        "e.g. '--advanced-query @query.json'. WARNING: Using advanced queries is incompatible with other query-"
        "building arguments.  Any additional filter options will be ignored."
    ),
)


def filter_options(f):
    f = start_option(f)
    f = end_option(f)
    f = on_option(f)
    f = alert_id_option(f)
    f = type_option(f)
    f = name_option(f)
    f = actor_option(f)
    f = actor_id_option(f)
    f = risk_severity_option(f)
    f = state_option(f)
    f = rule_id_option(f)
    f = severity_option(f)
    return f
