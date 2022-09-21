import json
import sys
from typing import Iterable
from typing import Optional

from click import BadOptionUsage
from typer import echo

from incydr.cli import console
from incydr.cli import render
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.logger import try_get_logger_for_server
from incydr.utils import Model
from incydr.utils import write_dict_to_csv
from incydr.utils import write_models_to_csv

# CLI - specific utils.py file to avoid circular imports


def output_response_format(
    response,
    key: str,
    title: str,
    format_: TableFormat = TableFormat.table,
    columns: Optional[str] = None,
    use_rich=True,
):
    if format_ is None:
        format_ = TableFormat.table

    results = response.json()[key]

    if not any(results):
        echo("No results found.")
        return

    if format_ == TableFormat.table and use_rich:
        with console.pager():
            render.table_json(results, columns=columns, title=title)

    elif format_ == TableFormat.csv:
        write_dict_to_csv(results, sys.stdout, columns=columns)

    elif format_ == TableFormat.json:
        for result in results:
            if columns:
                result = {c: result[c] for c in columns}
            console.print_json(data=result)

    else:
        for result in results:
            if columns:
                result = {c: result[c] for c in columns}
            echo(json.dumps(result))


def output_models_format(
    models: Iterable[Model],
    title: str,
    format_: TableFormat = TableFormat.table,
    columns: Optional[str] = None,
    use_rich=True,
):
    if not format_:
        format_ = TableFormat.table

    if not any(models):
        echo("No results found.")
        return

    if format_ == TableFormat.table and use_rich:
        with console.pager():
            render.table(models, columns=columns, title=title)

    # doesn't work for nested objects
    elif format_ == TableFormat.csv:
        write_models_to_csv(models, sys.stdout, columns=columns)

    elif format_ == TableFormat.json:
        for model in models:
            console.print_json(model.json(include=columns))

    else:
        for model in models:
            echo(model.json(include=columns))


def output_format_logger(
    models: Iterable[Model],
    output: str,
    format_: TableFormat = TableFormat.json,
    columns: Optional[str] = None,
    certs: Optional[str] = None,
    ignore_cert_validation: Optional[bool] = None,
):
    if format_ in [TableFormat.csv, TableFormat.table]:
        raise BadOptionUsage(
            "--format",
            "--output can only be used with json and raw-json formats.  Defaults to json.",
        )

    logger = try_get_logger_for_server(output, certs, ignore_cert_validation)

    # TODO - do we need to provide two json formats, is there a use case for sending anything but raw data?
    # TODO - this would also let us ignore the format option
    if format_ == TableFormat.json:
        for result in models:
            if columns:
                result = {c: result[c] for c in columns}
            logger.info(json.dumps(result, indent=4))

    else:
        for result in models:
            if columns:
                result = {c: result[c] for c in columns}
            logger.info(json.dumps(result))
