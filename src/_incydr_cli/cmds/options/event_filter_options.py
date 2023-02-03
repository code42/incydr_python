import click

from _incydr_cli.core import incompatible_with
from _incydr_cli.file_readers import FileOrString

AdvancedQueryAndSavedSearchIncompatible = incompatible_with(
    ["advanced_query", "saved_search"]
)

start_option = click.option(
    "--start",
    default=None,
    help="The beginning of the date range in which to look for file events. Accepts a date/time in yyyy-MM-dd (UTC) or"
    "yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format or a duration in the form of an ISO-duration string (ex. Pass `P7D` to filter for events which occurred in the last week).",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
end_option = click.option(
    "--end",
    default=None,
    help="The end of the date range in which to look for file events, argument format options are the same as `--start`.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
event_action_option = click.option(
    "--event-action",
    default=None,
    help="Filter by the type of file event observed.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
username_option = click.option(
    "--username",
    default=None,
    help="Filter by the Code42 username used to sign in to the Code42 app on the device. Null if the file event occurred on a cloud provider.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
md5_option = click.option(
    "--md5",
    default=None,
    help="Filter by the MD5 hash of the file contents.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
sha256_option = click.option(
    "--sha256",
    default=None,
    help="Filter by the SHA-256 hash of the file contents.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
source_category_option = click.option(
    "--source-category",
    default=None,
    help="Filter by the category of where the file originated. For example: Cloud Storage, Email, Social Media.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
destination_category_option = click.option(
    "--destination-category",
    default=None,
    help="Filter by the category of the file destination. For example: Cloud Storage, Email, Social Media.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
file_name_option = click.option(
    "--file-name",
    default=None,
    help="Filter by the name of the file, including the file extension.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
file_directory_option = click.option(
    "--file-directory",
    default=None,
    help="Filter by the file location on the user's device; a forward or backslash must be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
file_category_option = click.option(
    "--file-category",
    default=None,
    help="Filter by the categorization of the file that is inferred from MIME type.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
risk_indicator_option = click.option(
    "--risk-indicator",
    default=None,
    help="Filter by a list of risk indicators identified for this event. If more than one risk indicator applies to this event, the sum of all indicators determines the total risk score.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
risk_severity_option = click.option(
    "--risk-severity",
    default=None,
    help="Filter by the general risk assessment of the event, based on the numeric score.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)
risk_score_option = click.option(
    "--risk-score",
    default=1,
    help="Filter by risk scores greater than the provided value. The risk score is the sum of the weights for each risk indicator. This score is used to determine the overall risk severity of the event.  "
    "Defaults to 1.  Set to 0 to return all events, including those that have no risk associated with them.",
    cls=AdvancedQueryAndSavedSearchIncompatible,
)

saved_search_option = click.option(
    "--saved-search",
    default=None,
    help="Get events from a saved search with the given ID.  WARNING: Using a saved search is incompatible with other query-building arguments.  Any additional filter options will be ignored.",
    cls=incompatible_with(["advanced_query"]),
)
advanced_query_option = click.option(
    "--advanced-query",
    default=None,
    type=FileOrString(),
    help=(
        "Get events from a raw JSON file events query. Useful for when the provided query parameters do not satisfy your requirements.  "
        "Argument can be passed as a string, read from stdin by passing '-', or from a filename if prefixed with '@',"
        "e.g. '--advanced-query @query.json'. WARNING: Using advanced queries is incompatible with other query-"
        "building arguments.  Any additional filter options will be ignored."
    ),
    cls=incompatible_with(["saved_search"]),
)


def event_filter_options(f):
    f = start_option(f)
    f = end_option(f)
    f = event_action_option(f)
    f = username_option(f)
    f = md5_option(f)
    f = sha256_option(f)
    f = source_category_option(f)
    f = destination_category_option(f)
    f = file_name_option(f)
    f = file_directory_option(f)
    f = file_category_option(f)
    f = risk_indicator_option(f)
    f = risk_severity_option(f)
    f = risk_score_option(f)
    return f
