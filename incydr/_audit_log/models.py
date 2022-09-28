from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from incydr._core.models import ResponseModel
from pydantic import BaseModel, Field


class UserTypes(Enum):
    USER = 'USER'
    SUPPORT_USER = 'SUPPORT_USER'
    API_CLIENT = 'API_CLIENT'
    SYSTEM = 'SYSTEM'
    UNKNOWN = 'UNKNOWN'


class DateRange(BaseModel):
    endTime: Optional[datetime]
    startTime: Optional[datetime]


class RpcExportResponse(ResponseModel):
    download_token: str = Field(
        None,
        description='Download token to execute an export, acquired from the export api.',
        example='07FIbJogTJ2aHTBcyreAbYOvsd0FlEKuLyNumVvkbOQ=',
        alias="downloadToken"
    )


class RpcSearchResponse(ResponseModel):
    events: List[Dict[Optional[str], Optional[str]]] = Field(
        None,
        description='A list of zero or more events matching the given criteria.'
    )
    pagination_range_end_index: int = Field(
        None,
        description='The index of the last result returned, in relation to total results found',
        example=62,
        alias="paginationRangeEndIndex"
    )
    pagination_range_start_index: int = Field(
        None,
        description='The index of the first result returned, in relation to total results found',
        example=0,
        alias="paginationRangeStartIndex"
    )


class RpcSearchResultsCountResponse(ResponseModel):
    total_result_count: int = Field(
        None,
        description='The total number of results found by this search',
        example=104,
        alias="totalResultCount"
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
