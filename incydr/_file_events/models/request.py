from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel
from incydr._file_events.models.enums import GroupClause
from incydr.enums import SortDirection
from incydr.enums.file_events import EventSearchTerm
from incydr.enums.file_events import Operator


class SearchFilter(ResponseModel):
    operator: Optional[Operator] = Field(
        description="The type of match to perform.  Default value is `IS`.",
        example="IS_NOT",
    )
    term: Optional[EventSearchTerm] = Field(
        description="The field to match.", example="user.email"
    )
    value: Optional[str] = Field(
        None, description="The input for the search.", example="ari@example.com"
    )

    class Config:
        use_enum_values = True


class SearchFilterGroup(ResponseModel):
    filter_clause: Optional[GroupClause] = Field(
        alias="filterClause",
        description="Grouping clause for filters.  Default is `AND`.",
        example="AND",
    )
    filters: List[SearchFilter] = Field(
        description="One or more SearchFilters to be combined in a query."
    )

    class Config:
        use_enum_values = True


class SearchRequest(BaseModel):
    group_clause: Optional[GroupClause] = Field(
        alias="groupClause",
        description="Grouping clause for any specified groups.  Default is `AND`.",
        example="OR",
    )
    groups: List[SearchFilterGroup] = Field(
        description="One or more FilterGroups to be combined in a query."
    )
    pg_num: Optional[int] = Field(
        alias="pgNum",
        description="Page number for search; ignored if pgToken is included.  Default is 1.",
        example=1,
    )
    pg_size: Optional[int] = Field(
        alias="pgSize",
        description="Max number of results to return for a page.  Default is 100.",
        example=100,
    )
    pg_token: Optional[str] = Field(
        alias="pgToken",
        description="A token used to indicate the starting point for additional page results. Typically, you obtain the pgToken value from the nextPgToken provided in a previous request. A pgToken is the only way to page past 10,000 results. If pgToken is supplied, pgNum is ignored. Provide empty string to retrieve the 'first page of results and null to use the pgNum value.  Default is null.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    srt_dir: Optional[SortDirection] = Field(
        alias="srtDir",
        description="Sort direction.  Default is `desc`.",
        example="asc",
    )
    srt_key: Optional[EventSearchTerm] = Field(
        alias="srtKey", description="Search term for sorting.", example="event.id"
    )

    class Config:
        use_enum_values = True
