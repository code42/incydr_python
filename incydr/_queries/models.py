from enum import Enum
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel

from .terms import Terms


class Operator(str, Enum):
    IS = "IS"
    IS_NOT = "IS_NOT"
    EXISTS = "EXISTS"
    DOES_NOT_EXIST = "DOES_NOT_EXIST"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    ON = "ON"
    ON_OR_AFTER = "ON_OR_AFTER"
    ON_OR_BEFORE = "ON_OR_BEFORE"
    WITHIN_THE_LAST = "WITHIN_THE_LAST"


class _Filter(BaseModel):
    term: Terms
    operator: Operator
    value: Optional[Union[str, int]]

    class Config:
        use_enum_values = True


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[_Filter]]


class Query(BaseModel):
    groupClause: str = "AND"
    groups: Optional[FilterGroup]
    pgNum: int = 1
    pgSize: int = 100
    pgToken: Optional[str]
    srtDir: str = "asc"
    srtKey: Terms = "event.id"

    class Config:
        use_enum_values = True
