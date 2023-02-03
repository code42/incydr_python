from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums.watchlists import WatchlistType


class Date(ResponseModel):
    day: Optional[int] = Field(
        None,
        description="Day of month. Must be from 1 to 31 and valid for the year and month, or 0\n if specifying a year by itself or a year and month where the day is not\n significant.",
    )
    month: Optional[int] = Field(
        None,
        description="Month of year. Must be from 1 to 12, or 0 if specifying a year without a\n month and day.",
    )
    year: Optional[int] = Field(
        None,
        description="Year of date. Must be from 1 to 9999, or 0 if specifying a date without\n a year.",
    )


class IncludedDepartment(ResponseModel):
    """
    A model representing a department included on a watchlist.

    **Fields**:

    * **added_time**: `datetime` - The time the department was included on the watchlist.
    * **name**: `str` - Department name. Example: "Engineering".
    """

    added_time: datetime = Field(None, alias="addedTime")
    name: Optional[str] = Field(None, example="Engineering")


class IncludedDirectoryGroup(ResponseModel):
    """
    A model representing a directory group included on a watchlist.

    **Fields**:

    * **added_time**: `datetime` - The time the directory group was included on the watchlist.
    * **group_id**: `str` - A unique group ID for the directory group.
    * **is_deleted**: `bool` - Whether the included group was deleted by the directory provider but still referenced by the watchlist
    * **name**: `str` - The name of directory group. Example: "Research and Development".
    """

    added_time: datetime = Field(None, alias="addedTime")
    group_id: Optional[str] = Field(
        None, description="A unique group ID.", example="23", alias="groupId"
    )
    is_deleted: Optional[bool] = Field(
        None,
        description="Whether the included group was deleted by the directory provider but still referenced by the watchlist",
        alias="isDeleted",
    )
    name: Optional[str] = Field(None, example="Research and development")


class WatchlistUser(ResponseModel):
    """
    A model representing a user whose associated with a watchlist.

    **Fields**:

    * **added_time**: `datetime` - The time the user was associated with the watchlist.
    * **user_id**: `str` - Unique user ID.
    * **username**: `str - Username.
    """

    added_time: datetime = Field(None, alias="addedTime")
    user_id: Optional[str] = Field(
        None, description="A unique user ID.", example="23", alias="userId"
    )
    username: Optional[str] = Field(None, example="foo@bar.com")


class ExcludedUsersList(ResponseModel):
    """
    A model representing a list of users excluded from a watchlist.
    Excluded users are those that have been individually excluded from that list.

    **Fields**:

    * **excluded_users**: `List[WatchlistUser]` - The list of excluded users.
    * **total_count**: `int`
    """

    excluded_users: Optional[List[WatchlistUser]] = Field(None, alias="excludedUsers")
    total_count: Optional[int] = Field(
        None,
        description="The total count of all excluded users.",
        example=10,
        alias="totalCount",
    )


class IncludedDepartmentsList(ResponseModel):
    """
    A model representing a list of departments included on a watchlist.

    **Fields**:

    * **included_departments**: `List[IncludedDepartment]` - The list of included departments.
    * **total_count**: `int` - The total count of all included departments.
    """

    included_departments: Optional[List[IncludedDepartment]] = Field(
        None, alias="includedDepartments"
    )
    total_count: Optional[int] = Field(
        None,
        description="The total count of all included departments.",
        example=10,
        alias="totalCount",
    )


class IncludedDirectoryGroupsList(ResponseModel):
    """
    A model representing a list of directory groups included on a watchlist.

    **Fields**:

    * **included_directory_groups**: `List[IncludedDirectoryGroup]` - The list of included directory groups.
    * **total_count**: `int` - The total count of all included directory groups.
    """

    included_directory_groups: Optional[List[IncludedDirectoryGroup]] = Field(
        None, alias="includedDirectoryGroups"
    )
    total_count: Optional[int] = Field(
        None,
        description="The total count of all included directory groups.",
        example=10,
        alias="totalCount",
    )


class IncludedUsersList(ResponseModel):
    """
    A model representing a list of users included on a watchlist.
    Included users are those that have been individually included on that list.

    * **included_users**: `List[WatchlistUser]` - The list of included users.
    * **total_count**: `int` - The total count of all included users.
    """

    included_users: Optional[List[WatchlistUser]] = Field(None, alias="includedUsers")
    total_count: Optional[int] = Field(
        None,
        description="The total count of all included users.",
        example=10,
        alias="totalCount",
    )


class WatchlistStats(ResponseModel):
    """
    A model representing stats for a watchlist.

    **Fields**:

    * **excluded_users_count**: `int` - The number of users explicitly excluded from the watchlist.
    * **included_departments_count**: `int` - The number of departments explicitly included on the watchlist.
    * **included_directory_groups_count**: `int` - The number of directory groups explicitly included on the watchlist.
    * **included_users_count**: `int` - The number of users explicitly included on the watchlist.
    """

    excluded_users_count: Optional[int] = Field(
        None,
        description="The number of users explicitly excluded from the watchlist.",
        alias="excludedUsersCount",
        # displays a value of None as 0
        table=lambda excluded_users_count: excluded_users_count or 0,
    )
    included_departments_count: Optional[int] = Field(
        None,
        description="The number of departments explicitly included on the watchlist.",
        alias="includedDepartmentsCount",
        table=lambda included_departments_count: included_departments_count or 0,
    )
    included_directory_groups_count: Optional[int] = Field(
        None,
        description="The number of directory groups explicitly included on the watchlist.",
        alias="includedDirectoryGroupsCount",
        table=lambda included_directory_groups_count: included_directory_groups_count
        or 0,
    )
    included_users_count: Optional[int] = Field(
        None,
        description="The number of users explicitly included on the watchlist.",
        alias="includedUsersCount",
        table=lambda included_users_count: included_users_count or 0,
    )


class WatchlistMembersList(ResponseModel):
    """
    A model representing a list of watchlist members.
    Watchlist members are users who are on a list, whether it is because they are individually included,
    or because they are part of a department or directory group that is included.


    **Fields**:

    * **watchlist_members**: `List[WatchlistUser]` - The list of watchlist members.
    * **total_count**: `int` - Total count of members on the watchlist.
    """

    total_count: Optional[int] = Field(
        None,
        description="The total count of all included users..",
        example=10,
        alias="totalCount",
    )
    watchlist_members: Optional[List[WatchlistUser]] = Field(
        None, alias="watchlistMembers"
    )


class Watchlist(ResponseModel):
    """
    A model representing an Incydr Watchlist.

    **Fields**:

    * **description**: `str` - Optional description for a custom watchlist.
    * **list_type**: [`WatchlistType`][watchlist-types] - The watchlist type.
    * **stats**: `WatchlistStats` - Watchlist membership information.  Includes `included_user_count`, `included_department_count`, `included_directory_groups_count`, and `excluded_users_count`.
    * **tenant_id**: `str` - A unique tenant ID.
    * **title**: `str` - Title for a custom watchlist.
    * **watchlist_id**: `str` - A unique watchlist ID.
    """

    description: Optional[str] = Field(
        None, description="Description for a custom watchlist."
    )
    list_type: WatchlistType = Field(alias="listType")
    stats: Optional[WatchlistStats] = None
    tenant_id: Optional[str] = Field(
        None, description="A unique tenant ID.", alias="tenantId"
    )
    title: Optional[str] = Field(None, description="Title for a custom watchlist.")
    watchlist_id: Optional[str] = Field(
        None, description="A unique watchlist ID.", alias="watchlistId"
    )


class WatchlistsPage(ResponseModel):
    """
    A model representing a page of `Watchlist` objects.

    **Fields**:

    * **total_count**: `int` - Total count of watchlists found by the query.
    * **watchlists**: `List[Watchlist]` - The list `n` number of watchlists retrieved from the query, where `n=page_size`.
    """

    total_count: Optional[int] = Field(
        None,
        description="The total count of all watchlists.",
        example=10,
        alias="totalCount",
    )
    watchlists: Optional[List[Watchlist]] = Field(
        None, description="The list of watchlists."
    )
