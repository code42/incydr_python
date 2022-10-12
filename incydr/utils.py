from __future__ import annotations

from collections.abc import MutableMapping
from csv import DictReader
from csv import DictWriter
from io import IOBase
from itertools import chain
from pathlib import Path
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import TextIO
from typing import Type
from typing import TypeVar
from typing import Union

from click import echo
from pydantic import BaseModel
from pydantic import ValidationError


Model = TypeVar("Model", bound=BaseModel)


# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
def flatten(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class CSVValidationError(ValidationError):
    def __init__(self, msg, row):
        self.msg = msg
        self.row = row

    def __str__(self):
        return self.msg


def read_models_from_csv(
    model: Type[BaseModel], path: Union[str, Path, IOBase]
) -> Generator[Model, None, None]:
    if isinstance(path, IOBase):
        file = path
    else:
        path = Path(path)
        file = path.open(mode="r", encoding="utf-8")
    reader = DictReader(file)

    error = None
    for row in reader:
        for key, val in row.items():
            if val == "":
                row[key] = None
        try:
            yield model(**row)  # noqa
        except ValidationError as err:
            error = CSVValidationError(
                f"Bad data in row {reader.line_num} of {path}\n{str(err)}", row=i
            )
    if error:
        raise error


def read_dict_from_csv(
    path: Union[str, Path, IOBase], field_names: List[str] = None
) -> Generator[dict, None, None]:
    if isinstance(path, IOBase):
        file = path
    else:
        path = Path(path)
        file = path.open(mode="r", encoding="utf-8")
    reader = DictReader(file, fieldnames=field_names)
    error = None
    for row in reader:
        for key, val in row.items():
            if val == "":
                row[key] = None
        try:
            yield row  # noqa
        except ValidationError as err:
            error = CSVValidationError(
                f"Bad data in row {reader.line_num} of {path}\n{str(err)}", row=i
            )
    if error:
        raise error


def write_models_to_csv(
    models: Iterable[Model],
    path: Union[str, Path, IOBase, TextIO],
    columns: List[str] = None,
):
    if columns:
        columns = set(columns)
    if isinstance(path, IOBase):
        file = path
    else:
        path = Path(path)
        file = path.open(mode="w", encoding="utf-8")
    models = iter(models)
    first = next(models)
    writer = DictWriter(file, fieldnames=list(first.__fields__))
    writer.writeheader()
    for model in chain([first], models):
        writer.writerow(model.dict(by_alias=False, include=columns))


def write_dict_to_csv(
    models: List[Dict],
    path: Union[str, Path, IOBase, TextIO] = None,
    columns: str = None,
):
    if columns:
        columns = [c.strip() for c in columns.split(",")]

    models = iter(models)
    first = next(models)

    if columns:
        first = {c: first[c] for c in columns}
    first = flatten(first)

    if isinstance(path, IOBase):
        file = path
    else:
        path = Path(path)
        file = path.open(mode="w", encoding="utf-8")

    writer = DictWriter(file, fieldnames=list(first.keys()))
    writer.writeheader()
    for model in chain([first], models):
        if columns:
            model = {c: model[c] for c in columns}
        writer.writerow(flatten(model))
