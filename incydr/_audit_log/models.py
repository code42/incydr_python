from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel


class UserTypes(Enum):
    USER = "USER"
    SUPPORT_USER = "SUPPORT_USER"
    API_CLIENT = "API_CLIENT"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class DateRange(BaseModel):
    endTime: Optional[datetime]
    startTime: Optional[datetime]


class AuditEventsExport(ResponseModel):
    download_token: str = Field(
        None,
        description="Download token to execute an export, acquired from the export api.",
        example="07FIbJogTJ2aHTBcyreAbYOvsd0FlEKuLyNumVvkbOQ=",
        alias="downloadToken",
    )


class AuditEventsPage(ResponseModel):
    """
    A model representing a page of audit events.

    **Fields**:

    * **events**: `List[Dict[Optional[str], Optional[str]]]` A list of zero or more events matching the given criteria.
    * **pagination_range_end_index**: `int` The index of the last result returned, in relation to total results found.
    * **pagination_range_start_index**: `int` The index of the first result returned, in relation to total results found.
    """

    events: List[Dict[Optional[str], Optional[str]]] = Field(
        None, description="A list of zero or more events matching the given criteria."
    )
    pagination_range_end_index: int = Field(
        None,
        description="The index of the last result returned, in relation to total results found",
        example=62,
        alias="paginationRangeEndIndex",
    )
    pagination_range_start_index: int = Field(
        None,
        description="The index of the first result returned, in relation to total results found",
        example=0,
        alias="paginationRangeStartIndex",
    )


class AuditEventsCount(ResponseModel):
    """
    A model representing the total audit events result count.

    **Fields**:

    * **total_result_count**: `int` The total number of results found by this search.
    """

    total_result_count: int = Field(
        None,
        description="The total number of results found by this search",
        example=104,
        alias="totalResultCount",
    )


class QueryExportRequest(BaseModel):
    actorIds: Optional[List[str]]
    actorIpAddresses: Optional[List[str]]
    actorNames: Optional[List[str]]
    dateRange: Optional[DateRange]
    eventTypes: Optional[List[str]]
    resourceIds: Optional[List[str]]
    userTypes: Optional[List[UserTypes]]


class QueryAuditLogRequest(BaseModel):
    actorIds: Optional[List[str]]
    actorIpAddresses: Optional[List[str]]
    actorNames: Optional[List[str]]
    dateRange: Optional[DateRange]
    eventTypes: Optional[List[str]]
    pageNum: int
    pageSize: int
    resourceIds: Optional[List[str]]
    userTypes: Optional[List[UserTypes]]
