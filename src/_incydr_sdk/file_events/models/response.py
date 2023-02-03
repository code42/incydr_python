from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.file_events.models.event import FileEventV2


class SearchFilter(ResponseModel):
    operator: Optional[str] = Field(
        description="The type of match to perform.  Default value is `IS`.",
        example="IS_NOT",
    )
    term: Optional[str] = Field(description="The field to match.", example="user.email")
    value: Optional[str] = Field(
        None, description="The input for the search.", example="ari@example.com"
    )


class SearchFilterGroup(ResponseModel):
    filter_clause: Optional[str] = Field(
        alias="filterClause",
        description="Grouping clause for filters.  Default is `AND`.",
        example="AND",
    )
    filters: List[SearchFilter] = Field(
        description="One or more SearchFilters to be combined in a query."
    )


class QueryProblem(ResponseModel):
    """
    A model containing data on a query problem.

    **Fields**:

    * **bad_filter**: `SearchFilter` - The search filter that caused the problem.
    * **description**: `str` - Additional description of the problem.
    * **type**: 'ProblemType' - The type of problem that occurred. Ex: `SEARCH_FAILED`

    """

    bad_filter: Optional[SearchFilter] = Field(
        alias="badFilter",
        description="The search filter that caused this problem.",
    )
    description: Optional[str] = Field(
        description="Additional description of the problem.",
        example="Request timed out.  Refine your filter criteria and try again.",
    )
    type: Optional[str] = Field(
        description="The type of problem that occured.", example="SEARCH_FAILED"
    )


class FileEventsPage(ResponseModel):
    """
    A model representing a page of `FileEventV2` objects.

    **Fields**:

    * **file_events**: `List[FileEventsV2]` - The list of `n` number of file events retrieved from the query, where `n=pg_size`.
    * **next_pg_token**: `str` - The pgToken value from another request to indicate the starting point the next page of results. `nextPgToken` is null if there are no more results or if pgToken was not supplied.
    * **problems**: `List[QueryProblem]` - "List of problems in the request.  A problem with a search request could be an invalid filter value, an operator that can't be used on a term, etc.
    * **total_count**: `int` - Total count of file events found by the query.
    """

    file_events: Optional[List[FileEventV2]] = Field(
        alias="fileEvents", description="List of file events in the response."
    )
    next_pg_token: Optional[str] = Field(
        alias="nextPgToken",
        description="Use as the pgToken value in another request to indicate the starting point for additional page results. nextPgToken is null if there are no more results or if pgToken was not supplied.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    problems: Optional[List[QueryProblem]] = Field(
        description="List of problems in the request.  A problem with a search request could be an invalid filter value, an operator that can't be used on a term, etc.",
    )
    total_count: Optional[int] = Field(
        alias="totalCount",
        description="Total number of file events in the response.",
        example=42,
    )


class SavedSearch(ResponseModel):
    """
    A model representing a saved search.

    **Fields**:

    * **api_version**: `int` - The version of the API used to create the search.
    * **columns**: `List[str]` - The list of columns to be displayed in the web app for the search.
    * **created_by_uid**: `str` - The ID of the user who created the saved search.
    * **created_by_username**: `str` - The username of the user who created the saved search.
    * **creation_timestamp**: `datetime` - The time at which the saved search was created.
    * **group_clause**: `GroupClause` - `AND` or `OR`. Grouping clause for any specified groups. Defaults to `AND`.
    * **groups**: `List[SearchFilterGroup]` - One or more FilterGroups to be combined in a query.
    * **id**: `str` - The ID for the saved search.
    * **modified_by_uid**: `str` - The ID of the user who last modified the saved search.
    * **modified_by_username**: `str` - The username of the user who last modified the saved search.
    * **modified_timestamp**: `datetime` - The time at which the saved search was last modified.
    * **name**: `str` - The name given to the saved search.
    * **notes**: `str` - Optional notes about the search.
    * **srt_dir**: `SortDirection` - `asc` or `desc`. The direction in which to sort the response based on the corresponding key. Defaults to 'asc'.
    * **srt_key**: `str` - One or more values on which the response will be sorted. Defaults to event ID.

    """

    api_version: Optional[int] = Field(
        alias="apiVersion",
        description="Version of the API used to create the search.",
        example=1,
    )
    columns: Optional[List[str]] = Field(
        description="List of columns to be displayed in the web app for the search.",
    )
    created_by_uid: Optional[str] = Field(
        alias="createdByUID",
        description="User UID of the user who created the saved search.",
        example=806150685834341101,
    )
    created_by_username: Optional[str] = Field(
        alias="createdByUsername",
        description="Username of the user who created the saved search.",
        example="adrian@example.com",
    )
    creation_timestamp: Optional[datetime] = Field(
        alias="creationTimestamp",
        description="Time at which the saved search was created.",
        example="2020-10-27T15:16:05.369203Z",
    )
    group_clause: Optional[str] = Field(
        alias="groupClause",
        description="Grouping clause for any specified groups.",
        example="OR",
    )
    groups: Optional[List[SearchFilterGroup]] = Field(
        description="One or more FilterGroups to be combined in a query."
    )
    id: Optional[str] = Field(
        description="Unique identifier for the saved search.",
        example="cde979fa-d551-4be9-b242-39e75b824089",
    )
    modified_by_uid: Optional[str] = Field(
        alias="modifiedByUID",
        description="User UID of the user who last modified the saved search.",
        example=421380797518239242,
    )
    modified_by_username: Optional[str] = Field(
        alias="modifiedByUsername",
        description="Username of the user who last modified the saved search.",
        example="ari@example.com",
    )
    modified_timestamp: Optional[datetime] = Field(
        alias="modifiedTimestamp",
        description="Time at which the saved search was last modified.",
        example="2020-10-27T15:20:26.311894Z",
    )
    name: Optional[str] = Field(
        description="Name given to the saved search.",
        example="Example saved search",
    )
    notes: Optional[str] = Field(
        description="Optional notes about the search.",
        example="This search returns all events.",
    )
    srt_dir: Optional[SortDirection] = Field(
        alias="srtDir", description="Sort direction.", example="asc"
    )
    srt_key: Optional[str] = Field(
        alias="srtKey", description="Search term for sorting.", example="event.id"
    )
