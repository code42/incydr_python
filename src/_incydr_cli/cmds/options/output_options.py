from enum import Enum

import click

from _incydr_cli.core import incompatible_with


class TableFormat(str, Enum):
    table = "table"
    json_pretty = "json-pretty"
    json_lines = "json-lines"
    csv = "csv"


class SingleFormat(str, Enum):
    rich = "rich"
    json_pretty = "json-pretty"
    json_lines = "json-lines"


input_format_option = click.option(
    "--format",
    "-f",
    "format_",
    type=click.Choice(["csv", "json-lines"]),
    default="csv",
    help="Specify format of input file: 'csv' or 'json-lines'.  Defaults to 'csv'.",
)

table_format_option = click.option(
    "--format",
    "-f",
    "format_",
    type=TableFormat,
    help="Format to print result. One of 'table', 'json-pretty', 'json-lines', or 'csv. If environment has INCYDR_USE_RICH=false set, defaults to 'json-lines', else defaults to 'table'.",
    default=TableFormat.table,
)
single_format_option = click.option(
    "--format",
    "-f",
    "format_",
    default="rich",
    type=SingleFormat,
    help="Format to print result. One of 'rich', 'json-pretty', or 'json-lines'. If environment has INCYDR_USE_RICH=false set, defaults to 'json-lines', else defaults to 'rich'.",
)

columns_option = click.option(
    "--columns",
    default=None,
    help="Comma-delimited string of column names. Nested values should be specified in dot-notation. "
    "Limits output to contain only the specified columns in CSV or Table format.  Ignored for JSON output formats.",
    callback=lambda ctx, param, value: value.split(",") if value is not None else None,
)

output_option = click.option(
    "--output",
    default=None,
    help="Use to send the raw-json data in to a syslog server.  Pass a string in the format PROTOCOL:HOSTNAME:PORT to output "
    "to the specified server endpoint, where format is either TCP, TLS-TCP, or UDP (ex: TCP:localhost:5000). "
    "Also accepts strings of the format HOSTNAME and HOSTNAME:PORT. Defaults to TCP protocol on port 601. "
    "The --certs or --ignore-cert-validation option can be used with TLS-TCP format.  Note that most data will be too large to be sent "
    "via UDP protocol.",
    cls=incompatible_with(["format"]),
)
ignore_cert_validation_option = click.option(
    "--ignore-cert-validation",
    default=False,
    help="Set to skip CA certificate validation for the TLS-TCP protocol. Incompatible with the 'certs' option.",
    cls=incompatible_with(["certs"]),
)
certs_option = click.option(
    "--certs",
    default=None,
    help="A CA certificates-chain file for the TLS-TCP protocol.",
)


def output_options(f):
    f = output_option(f)
    f = certs_option(f)
    f = ignore_cert_validation_option(f)
    return f
