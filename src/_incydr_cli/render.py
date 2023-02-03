import sys
from csv import DictWriter
from datetime import datetime
from io import TextIOWrapper
from itertools import chain
from typing import Iterable
from typing import List
from typing import Type

from pydantic import BaseModel
from rich.console import Console
from rich.console import ConsoleRenderable
from rich.console import RichCast
from rich.table import Table

from _incydr_cli import console
from _incydr_sdk.utils import get_fields
from _incydr_sdk.utils import iter_model_formatted
from _incydr_sdk.utils import model_as_card


def date(dt: datetime):
    """render locale appropriate date"""
    return dt.strftime("%x")


def date_time(dt: datetime):
    """render locale appropriate date & time (w/ time truncated to minute precision)"""
    return dt.isoformat(sep=" ")[:16] + " UTC"


def measure_renderable(r: ConsoleRenderable):
    # the console.measure() method limits the max measurement size to the current size of the console
    # so to get the _actual_ size that a table would occupy with no wrapping, we need to make a large
    # console object
    return Console(width=100_000).measure(r).maximum


def models_as_table(
    model: Type[BaseModel],
    models: Iterable[BaseModel],
    columns: List[str] = None,
    title=None,
    flat=False,
):
    headers = list(get_fields(model, include=columns, flat=flat))
    tbl = Table(*headers, title=title, show_lines=True)
    for m in models:
        values = []
        for _name, value in iter_model_formatted(
            m, include=headers, flat=flat, render="table"
        ):
            if isinstance(value, BaseModel):
                value = model_as_card(value)
            elif not isinstance(value, (ConsoleRenderable, RichCast, str)):
                value = str(value)
            values.append(value)
        tbl.add_row(*values)
    return tbl


def table(
    model: Type[BaseModel],
    models: Iterable[BaseModel],
    columns: List[str] = None,
    title=None,
    flat=False,
):
    tbl = models_as_table(model, models, columns, title, flat)

    if not tbl.rows:
        console.print("No results found.")
        return
    with console.pager():
        # expand console and table so no values get truncated due to size of console, since we're using a pager
        console.width = tbl.width = measure_renderable(tbl)
        console.print(tbl, crop=False, soft_wrap=False, overflow="fold")


def csv(
    model: Type[BaseModel],
    models: Iterable[BaseModel],
    columns: List[str] = None,
    flat: bool = False,
    file: TextIOWrapper = sys.stdout,
):
    models = iter(models)
    try:
        first = next(models)
        models = chain([first], models)
    except StopIteration:
        console.print("No results found.")
        return
    headers = list(get_fields(model, columns, flat=flat))
    writer = DictWriter(file, fieldnames=headers, extrasaction="ignore")

    writer.writeheader()
    for m in models:
        flat_event = dict(
            iter_model_formatted(m, flat=flat, render="csv", include=headers)
        )
        writer.writerow(flat_event)
