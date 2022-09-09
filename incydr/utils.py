from __future__ import annotations

from csv import DictReader
from csv import DictWriter
from io import IOBase
from itertools import chain
from pathlib import Path
from typing import Generator
from typing import Iterable
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic import ValidationError

Model = TypeVar("Model", bound=BaseModel)


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
    for i, row in enumerate(reader, 1):
        for key, val in row.items():
            if val == "":
                row[key] = None
        try:
            yield model(**row)  # noqa
        except ValidationError as err:
            error = CSVValidationError(
                f"Bad data in row {i} of {path}\n{str(err)}", row=i
            )
    if error:
        raise error


def write_models_to_csv(
    models: Iterable[Model],
    path: Union[str, Path, IOBase],
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
