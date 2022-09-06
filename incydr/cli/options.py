from typer import Option
from enum import Enum


class Format(Enum):
    table = "table"
    json = "json"
    raw_json = "raw-json"
    csv = "csv"


format_option = Option(
    "table", "--format", help="Format to print result.", case_sensitive=False
)
columns_option = Option(
    None,
    help="Comma-delimited string of column names. Limits output to only specified fields",
    case_sensitive=False,
)
