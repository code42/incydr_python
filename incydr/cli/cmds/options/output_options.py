from enum import Enum

import click

from incydr.cli.logger import ServerProtocol


class TableFormat(str, Enum):
    table = "table"
    json = "json"
    raw_json = "raw-json"
    csv = "csv"


class SingleFormat(str, Enum):
    rich = "rich"
    json = "json"
    raw_json = "raw-json"


table_format_option = click.option(
    "--format",
    "-f",
    "format_",
    type=TableFormat,
    help="Format to print result. If environment has INCYDR_USE_RICH=false set, defaults to 'raw-json'",
    default=None,
)
single_format_option = click.option(
    "--format",
    "-f",
    "format_",
    default="rich",
    type=SingleFormat,
    help="Format to print result. If environment has INCYDR_USE_RICH=false set, defaults to 'raw-json'",
)

columns_option = click.option(
    "--columns",
    default=None,
    help="Comma-delimited string of column names. Limits output to only specified fields",
    callback=lambda ctx, param, value: value.split(",") if value is not None else None,
)

output_option = click.option(
    "--output",
    default=None,
    type=ServerProtocol,
    help="Use to send the data to a syslog server.  Pass a string in the format PROTOCOL:HOSTNAME:PORT to output "
    "to the specified server endpoint, where format is either UDP, TCP or TLS_TCP.  "
    "--certs or --ignore-cert-validation options can be used with TLS_TCP format.",
)
ignore_cert_validation_option = click.option(
    "--ignore-cert-validation",
    default=False,
    help="Set to skip CA certificate validation. Incompatible with the 'certs' option.",
)
certs_option = click.option(
    "--certs",
    default=None,
    help="A CA certificates-chain file for the TCP-TLS protocol.",
)


def output_options(f):
    f = output_option(f)
    f = certs_option(f)
    f = ignore_cert_validation_option(f)
    return f