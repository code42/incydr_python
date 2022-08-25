# generated by datamodel-codegen:
#   filename:  watchlists.json
#   timestamp: 2022-08-25T19:03:22+00:00
from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from incydr._core.models import ResponseModel
from incydr.enums.watchlists import WatchlistType


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


class DirectoryGroup(ResponseModel):
    group_id: Optional[str] = Field(
        None, description="A unique group ID.", example="23", alias="groupId"
    )
    name: Optional[str] = Field(None, example="Research and development")


class ExcludedUser(ResponseModel):
    """
    A model representing a user excluded from a watchlist.

    **Fields**:

    * **added_time**: `datetime` - The time the user was excluded from the watchlist.
    * **user_id**: `str` - Unique user ID.
    * **username**: `str - The username of the excluded user.
    """

    added_time: datetime = Field(None, alias="addedTime")
    user_id: Optional[str] = Field(
        None, description="A unique user ID.", example="23", alias="userId"
    )
    username: Optional[str] = Field(None, example="foo@bar.com")


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


class IncludedUser(ResponseModel):
    """
    A model representing a user included on a watchlist.

    **Fields**:

    * **added_time**: `datetime` - The time the user was included on the watchlist.
    * **user_id**: `str` - Unique user ID.
    * **username**: `str - The username of the excluded user.
    """

    added_time: datetime = Field(None, alias="addedTime")
    user_id: Optional[str] = Field(
        None, description="A unique user ID.", example="23", alias="userId"
    )
    username: Optional[str] = Field(None, example="foo@bar.com")


class DepartmentsPage(ResponseModel):
    """
    A model representing a list of departments.

    **Fields**:

    * **directory_groups**: `List[str]` - The list of `n` department names retrieved by the query, where `n=page_size`.
    * **total_count**: `int` - Total count of departments retrieved by the query.
    """

    departments: Optional[List[str]] = None
    total_count: Optional[int] = Field(
        None,
        description="The total count of all departments.",
        example=10,
        alias="totalCount",
    )


class DirectoryGroupsPage(ResponseModel):
    """
    A model representing a list of directory groups.

    **Fields**:

    * **directory_groups**: `List[DirectoryGroup`] - The list of `n` directory groups retrieved by the query, where `n=page_size`.
    * **total_count**: `int` - Total count of directory groups retrieved by the query.
    """

    directory_groups: Optional[List[DirectoryGroup]] = Field(
        None, alias="directoryGroups"
    )
    total_count: Optional[int] = Field(
        None,
        description="The total count of all directory groups.",
        example=10,
        alias="totalCount",
    )


class ExcludedUsersList(ResponseModel):
    """A model representing a list of users excluded from a watchlist."""

    excluded_users: Optional[List[ExcludedUser]] = Field(None, alias="excludedUsers")
    total_count: Optional[int] = Field(
        None,
        description="The total count of all excluded users.",
        example=10,
        alias="totalCount",
    )


class IncludedDepartmentsList(ResponseModel):
    """A model representing a list of departments included on a watchlist."""

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
    """A model representing a list of directory groups included on a watchlist."""

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
    """A model representing a list of users included on a watchlist."""

    included_users: Optional[List[IncludedUser]] = Field(None, alias="includedUsers")
    total_count: Optional[int] = Field(
        None,
        description="The total count of all included users.",
        example=10,
        alias="totalCount",
    )


class WatchlistMember(ResponseModel):
    """
    A model representing an Incydr Watchlist member.

    **Fields**:

    * **added_time**: `datetime` - The time the user was added to the watchlist.
    * **user_id**: `str` - Unique user ID.
    * **username** `str` - Username for the user.
    """

    added_time: datetime = Field(None, alias="addedTime")
    user_id: Optional[str] = Field(
        None, description="A unique user ID.", example="23", alias="userId"
    )
    username: Optional[str] = Field(None, example="foo@bar.com")


class WatchlistStats(ResponseModel):
    """
    A model representing stats for a watchlist.

    **Fields**:

    * **excluded_users_count**: The number of users explicitly excluded from the watchlist.
    * **included_departments_count**: The number of departments explicitly included on the watchlist.
    * **included_directory_groups_count**: The number of directory groups explicitly included on the watchlist.
    * **included_users_count**: The number of users explicitly included on the watchlist.
    """

    excluded_users_count: Optional[int] = Field(
        None,
        description="The number of users explicitly excluded from the watchlist.",
        alias="excludedUsersCount",
    )
    included_departments_count: Optional[int] = Field(
        None,
        description="The number of departments explicitly included on the watchlist.",
        alias="includedDepartmentsCount",
    )
    included_directory_groups_count: Optional[int] = Field(
        None,
        description="The number of directory groups explicitly included on the watchlist.",
        alias="includedDirectoryGroupsCount",
    )
    included_users_count: Optional[int] = Field(
        None,
        description="The number of users explicitly included on the watchlist.",
        alias="includedUsersCount",
    )


class WatchlistMembersList(ResponseModel):
    """
    A model representing a list of `WatchlistMember` objects.

    **Fields**:

    * **total_count**: `int` - Total count of members o.
    """

    total_count: Optional[int] = Field(
        None,
        description="The total count of all included users..",
        example=10,
        alias="totalCount",
    )
    watchlist_members: Optional[List[WatchlistMember]] = Field(
        None, alias="watchlistMembers"
    )


class Watchlist(ResponseModel):
    """
    A model representing an Incydr Watchlist.

    **Fields**:

    * **description**: `str` - Optional description for a custom watchlist.
    * **list_type**: `WatchlistType` - The watchlist type.
    * **stats**: `WatchlistStats` - Watchlist membership information.  Includes `included_user_count`, `included_department_count`, etc.
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
