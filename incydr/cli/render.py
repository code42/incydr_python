import os
import sys
import platform
from csv import DictWriter
from datetime import datetime
from itertools import chain
from typing import Iterable
from typing import Set
from typing import Type

from pydantic import BaseModel
from rich.table import Table
from rich.console import RenderableType

from incydr.utils import get_fields
from incydr.cli import console
from incydr.utils import iter_model_formatted
from incydr.utils import model_as_card
from incydr._core.models import Model

if platform.system() in ("Darwin", "Linux"):
    os.environ["MANPAGER"] = "less -S"
else:
    ...
    # TODO: figure out Windows pager to use


def date(dt: datetime):
    """render locale appropriate date"""
    return dt.strftime("%x")


def date_time(dt: datetime):
    """render locale appropriate date & time (w/ time truncated to minute precision)"""
    return dt.isoformat(sep=" ")[:16] + " UTC"


def table(
    model: Type[Model],
    models: Iterable[Model],
    columns: list[str] = None,
    title=None,
    flat=False,
):
    headers = list(get_fields(model, include=columns, flat=flat))
    header_padding = len(headers) * 3
    max_width = 0
    tbl = Table(*headers, title=title, show_lines=True)
    for m in models:
        values = []
        row_width = 0
        for name, value in iter_model_formatted(
            m, include=headers, flat=flat, render="table"
        ):
            if isinstance(value, BaseModel):
                value = model_as_card(value)
            elif not isinstance(value, RenderableType):
                value = str(value)
            value_size = console.measure(value).maximum
            row_width += value_size
            values.append(value)
        if row_width + header_padding > max_width:
            max_width = row_width + header_padding
        tbl.add_row(*values)

    console.width = max_width
    tbl.width = max_width
    with console.pager():
        console.print(tbl, soft_wrap=False)


def table_json(results: Iterable, columns: Set[str] = None, title=None):
    models = iter(results)
    first = next(models)
    if columns:
        first = {c: first[c] for c in columns}
    header = first.keys()
    tbl = Table(*header, title=title)
    for model in chain([first], models):
        row = []
        for k, v in model.items():
            if columns and k not in columns:
                continue
            else:
                row.append(str(v))
        tbl.add_row(*row)
    console.print(tbl)


def csv(
    model: Type[Model],
    models: Iterable[Model],
    columns: list[str] = None,
    flat: bool = False,
):
    headers = list(get_fields(model, columns, flat=flat))
    writer = DictWriter(sys.stdout, fieldnames=headers, extrasaction="ignore")

    writer.writeheader()
    for m in models:
        flat_event = dict(
            iter_model_formatted(m, flat=flat, render="csv", include=headers)
        )
        writer.writerow(flat_event)
