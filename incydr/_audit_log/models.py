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
    end_time: Optional[datetime] = Field(
        None,
        alias="endTime"
    )
    start_time: Optional[datetime] = Field(
        None,
        alias="startTime"
    )


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


class ExportRequest(BaseModel):
    actor_ids: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_id is one of the given ids. An actor may be a human user or a service.',
        example='albertha.rice@yahoo.com',
        alias="actorIds"
    )
    actor_ip_addresses: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_ip_address is one of the given IP addresses.',
        example='127.0.0.1',
        alias="actorIpAddresses"
    )
    actor_names: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_name is one of the given names. An actor may be a human user or a '
                    'service.',
        example='JinJenz',
        alias="actorNames"
    )
    date_range: Optional[DateRange] = Field(
        None,
        alias="dateRange"
    )
    event_types: Optional[List[str]] = Field(
        None,
        description='Finds events whose type is one of the given types.',
        example='support_user_access_disabled',
        title='Some examples: support_user_access_disabled, alert_note_edited, api_client_created, logged_in, '
              'case_archived, account_name_added, file_download, search_issued, federation_created, user_activated, '
              'risk_profile_cloud_alias_added',
        alias="eventTypes"
    )
    resource_ids: Optional[List[str]] = Field(
        None,
        description='Filters export events that match resource_id',
        example=1523,
        alias="resourceIds"
    )
    user_types: Optional[List[UserTypes]] = Field(
        None,
        description='Filters export events that match actor type',
        example='User',
        alias="userTypes"
    )


class SearchAuditLogRequest(BaseModel):
    actor_ids: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_id is one of the given ids. An actor may be a human user or a service.',
        example='albertha.rice@yahoo.com',
        alias="actor_ids"
    )
    actor_ip_addresses: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_ip_address is one of the given IP addresses.',
        example='127.0.0.1',
        alias="actorIpAddresses"
    )
    actor_names: Optional[List[str]] = Field(
        None,
        description='Finds events whose actor_name is one of the given names. An actor may be a human user or a '
                    'service.',
        example='JinJenz',
        alias="actorNames"
    )
    date_range: Optional[DateRange] = Field(
        None,
        alias="dateRange"
    )
    event_types: Optional[List[str]] = Field(
        None,
        description='Finds events whose type is one of the given types.',
        example='support_user_access_disabled',
        title='Some examples: support_user_access_disabled, alert_note_edited, api_client_created, logged_in, '
              'case_archived, account_name_added, file_download, search_issued, federation_created, user_activated, '
              'risk_profile_cloud_alias_added',
        alias="eventTypes"
    )
    page: int = Field(
        None,
        description='Which page of events to view.'
    )
    page_size: int = Field(
        None,
        description='How many elements to return on each page.',
        alias="pageSize"
    )
    resource_ids: Optional[List[str]] = Field(
        None,
        description='Filters searchable events that match resource_id.',
        example=1523,
        alias="resourceIds"
    )
    user_types: Optional[List[UserTypes]] = Field(
        None,
        description='Filters searchable events that match actor type.',
        example='User',
        alias="userTypes"
    )
