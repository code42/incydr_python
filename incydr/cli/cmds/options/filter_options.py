import click

start_option = click.option(
    "--start",
    default=None,
    help="The beginning of the date range in which to look for file events. Accepts a date/time in yyyy-MM-dd (UTC) or"
    "yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format or a duration in the form of an ISO-duration string (ex. Pass `P7D` to filter for events which occurred in the last week).",
)
end_option = click.option(
    "--end",
    default=None,
    help="The end of the date range in which to look for file events, argument format options are the same as `--start`.",
)
event_action_option = click.option(
    "--event-action",
    default=None,
    help="The type of file event observed.",
)
username_option = click.option(
    "--username",
    default=None,
    help="The Code42 username used to sign in to the Code42 app on the device. Null if the file event occurred on a cloud provider.",
)
md5_option = click.option(
    "--md5",
    default=None,
    help="The MD5 hash of the file contents.",
)
sha256_option = click.option(
    "--sha256",
    default=None,
    help="The SHA-256 hash of the file contents.",
)
source_category_option = click.option(
    "--source-category",
    default=None,
    help="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
)
destination_category_option = click.option(
    "--destination-category",
    default=None,
    help="General category of the file destination. For example: Cloud Storage, Email, Social Media.",
)
file_name_option = click.option(
    "--file-name",
    default=None,
    help="The name of the file, including the file extension.",
)
file_directory_option = click.option(
    "--file-directory",
    default=None,
    help="The file location on the user's device; a forward or backslash must be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
)
file_category_option = click.option(
    "--file-category",
    default=None,
    help="A categorization of the file that is inferred from MIME type.",
)
risk_indicator_option = click.option(
    "--risk-indicator",
    default=None,
    help="List of risk indicators identified for this event. If more than one risk indicator applies to this event, the sum of all indicators determines the total risk score.",
)
risk_severity_option = click.option(
    "--risk-severity",
    default=None,
    help="The general risk assessment of the event, based on the numeric score.",
)
risk_score_option = click.option(
    "--risk-score",
    default=None,
    help="Filter results by risk scores greater than the provided value. The risk score is the sum of the weights for each risk indicator. This score is used to determine the overall risk severity of the event.",
)
include_all_option = click.option(
    "--include-no-risk-events",
    "include_all",
    default=False,
    help="Include all events in results, including those that have no risk associated with them.",
)

saved_search_option = click.option(
    "--saved-search",
    default=None,
    help="Get events from a saved search with the given ID.  WARNING: Using a saved search is incompatible with other query-building arguments.  Any additional filter options will be ignored.",
)
# TODO - is it alright to just ignore other filter options when --saved-search or --advanced-query is passed? Should we raise errors if they try and pass additional options
advanced_query_option = click.option(
    "--advanced-query",
    default=None,
    help=(
        "A raw JSON file events query. Useful for when the provided query parameters do not satisfy your requirements.  "
        "Argument can be passed as a string, read from stdin by passing '-', or from a filename if prefixed with '@',"
        "e.g. '--advanced-query @query.json'. WARNING: Using advanced queries is incompatible with other query-"
        "building arguments.  Any additional filter options will be ignored."
    ),
)


def filter_options(f):
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
    f = include_all_option(f)
    return f