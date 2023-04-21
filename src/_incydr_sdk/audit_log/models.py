from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel


class UserTypes(str, Enum):
    USER = "USER"
    SUPPORT_USER = "SUPPORT_USER"
    API_CLIENT = "API_CLIENT"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class DateRange(BaseModel):
    endTime: Optional[float]
    startTime: Optional[float]


class AuditEventsPage(ResponseModel):
    """
    A model representing a page of audit events.

    **Fields**:

    * **events**: `List[Dict[Optional[str], Any]]` A list of zero or more events matching the given criteria.
        Each event is represented as a dictionary of property names associated with that event.  These fields may differ
        from event to event.
    * **pagination_range_end_index**: `int` The index of the last result returned, in relation to total results found.
    * **pagination_range_start_index**: `int` The index of the first result returned, in relation to total results found.
    """

    events: List[Dict[Optional[str], Any]] = Field(
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


class QueryExportRequest(Model):
    actorIds: Optional[List[str]]
    actorIpAddresses: Optional[List[str]]
    actorNames: Optional[List[str]]
    dateRange: Optional[DateRange]
    eventTypes: Optional[List[str]]
    resourceIds: Optional[List[str]]
    userTypes: Optional[List[UserTypes]]


class QueryAuditLogRequest(Model):
    actorIds: Optional[List[str]]
    actorIpAddresses: Optional[List[str]]
    actorNames: Optional[List[str]]
    dateRange: Optional[DateRange]
    eventTypes: Optional[List[str]]
    page: int
    pageSize: int
    resourceIds: Optional[List[str]]
    userTypes: Optional[List[UserTypes]]
