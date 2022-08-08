from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel

from incydr._queries._file_events.enums import EventTerms
from incydr._queries._file_events.enums import Operator


class Filter(BaseModel):
    term: EventTerms
    operator: Operator
    value: Optional[Union[str, int]]

    class Config:
        use_enum_values = True


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class Query(BaseModel):
    groupClause: str = "AND"
    groups: Optional[List[FilterGroup]]
    pgNum: int = 1
    pgSize: int = 100
    pgToken: Optional[str]
    srtDir: str = "asc"
    srtKey: EventTerms = "event.id"

    class Config:
        use_enum_values = True
