from enum import Enum

from typer import Option


class TableFormat(Enum):
    table = "table"
    json = "json"
    raw_json = "raw-json"
    csv = "csv"


class SingleFormat(Enum):
    rich = "rich"
    json = "json"
    raw_json = "raw-json"


table_format_option = Option(
    "table",
    "--format",
    help="Format to print result. If environment has INCYDR_USE_RICH=false set, defaults to 'raw-json'",
    case_sensitive=False,
)
single_format_option = Option(
    "rich",
    "--format",
    help="Format to print result. If environment has INCYDR_USE_RICH=false set, defaults to 'raw-json'",
    case_sensitive=False,
)

columns_option = Option(
    None,
    help="Comma-delimited string of column names. Limits output to only specified fields",
    case_sensitive=False,
    callback=lambda s: None if not s else set(s.split(",")),
)
