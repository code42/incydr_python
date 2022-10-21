import itertools
import json
import sys
from typing import Iterable
from typing import Optional

from typer import echo

from incydr.cli import console
from incydr.cli import render
from incydr.cli.cmds.options.output_options import TableFormat
from incydr.cli.logger import try_get_logger_for_server
from incydr.utils import Model
from incydr.utils import write_dict_to_csv
from incydr.utils import write_models_to_csv

# CLI - specific utils.py file to avoid circular imports


def peek(iterable):
    # See https://stackoverflow.com/questions/661603/how-do-i-know-if-a-generator-is-empty-from-the-start
    # Note: this does not work for empty iterators
    # empty iterator: one which yields nothing (different from yielding None)
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return itertools.chain([first], iterable)


def output_response_format(
    results,
    title: str,
    format_: TableFormat = TableFormat.table,
    columns: Optional[str] = None,
    use_rich=True,
):
    # response should be an array of dict objects

    if format_ is None:
        format_ = TableFormat.table

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


# WARNING: CSV output will not work for nested objects
def output_models_format(
    models: Iterable[Model],
    title: str,
    format_: TableFormat = TableFormat.table,
    columns: Optional[str] = None,
    use_rich=True,
):
    if not format_:
        format_ = TableFormat.table

    models = peek(models)
    if models is None:
        echo("No results found.")
        return

    if format_ == TableFormat.table and use_rich:
        with console.pager():
            render.table(models, columns=columns, title=title)

    elif format_ == TableFormat.csv:
        write_models_to_csv(models, sys.stdout, columns=columns)

    elif format_ == TableFormat.json:
        for model in models:
            console.print_json(model.json(include=columns))

    else:
        for model in models:
            echo(model.json(include=columns))


def output_format_logger(
    results,
    output: str,
    columns: Optional[str] = None,
    certs: Optional[str] = None,
    ignore_cert_validation: Optional[bool] = None,
):

    if not any(results):
        echo("No results found.")
        return

    logger = try_get_logger_for_server(output, certs, ignore_cert_validation)

    for result in results:
        if columns:
            result = {c: result[c] for c in columns}
        logger.info(json.dumps(result))
