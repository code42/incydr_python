from datetime import datetime
from itertools import chain
from typing import Iterable
from typing import Set

from pydantic import BaseModel
from rich.table import Table

from incydr.cli import console


def date(dt: datetime):
    """render locale appropriate date"""
    return dt.strftime("%x")


def date_time(dt: datetime):
    """render locale appropriate date & time (w/ time truncated to minute precision)"""
    return dt.isoformat(sep=" ")[:16] + " UTC"


def model_as_row(model: BaseModel, columns: Set[str] = None):
    for name, value in model:
        if columns and name not in columns:
            continue
        if isinstance(value, datetime):
            yield date_time(value)
        else:
            yield str(value)


def table(models: Iterable[BaseModel], columns: Set[str] = None, title=None):
    models = iter(models)
    first = next(models)
    header = first.dict(by_alias=False, include=columns).keys()
    tbl = Table(*header, title=title)
    for model in chain([first], models):
        tbl.add_row(*model_as_row(model, columns=columns))
    console.print(tbl)


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
