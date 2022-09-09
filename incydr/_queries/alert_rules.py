from datetime import datetime
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel

from incydr.enums.file_events import Operator


class Filter(BaseModel):
    term: str
    operator: Operator
    value: Optional[Union[int, str]] = None

    class Config:
        use_enum_values = True


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class Query(BaseModel):
    tenantId: str
    groupClause: str = "AND"
    groups: Optional[List[FilterGroup]]
    pgNum: int = 0
    pgSize: int = 100
    pgToken: Optional[str]
    srtDirection: str = "asc"
    srtKey: str = "CreatedAt"

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}
