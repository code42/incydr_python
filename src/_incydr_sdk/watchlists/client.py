from itertools import count
from typing import Iterator
from typing import List
from typing import Union

from _incydr_sdk.enums.watchlists import WatchlistType
from _incydr_sdk.exceptions import WatchlistNotFoundError
from _incydr_sdk.watchlists.models.requests import CreateWatchlistRequest
from _incydr_sdk.watchlists.models.requests import ListWatchlistsRequest
from _incydr_sdk.watchlists.models.requests import UpdateExcludedUsersRequest
from _incydr_sdk.watchlists.models.requests import UpdateIncludedDepartmentsRequest
from _incydr_sdk.watchlists.models.requests import UpdateIncludedDirectoryGroupsRequest
from _incydr_sdk.watchlists.models.requests import UpdateIncludedUsersRequest
from _incydr_sdk.watchlists.models.requests import UpdateWatchlistRequest
from _incydr_sdk.watchlists.models.responses import ExcludedUsersList
from _incydr_sdk.watchlists.models.responses import IncludedDepartment
from _incydr_sdk.watchlists.models.responses import IncludedDepartmentsList
from _incydr_sdk.watchlists.models.responses import IncludedDirectoryGroup
from _incydr_sdk.watchlists.models.responses import IncludedDirectoryGroupsList
from _incydr_sdk.watchlists.models.responses import IncludedUsersList
from _incydr_sdk.watchlists.models.responses import Watchlist
from _incydr_sdk.watchlists.models.responses import WatchlistMembersList
from _incydr_sdk.watchlists.models.responses import WatchlistsPage
from _incydr_sdk.watchlists.models.responses import WatchlistUser


class WatchlistsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = WatchlistsV1(self._parent)
        return self._v1


class WatchlistsV1:
    """
    Client for `/v1/watchlists` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.watchlists.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent
        self._watchlist_type_id_map = {}
        self._uri = "/v1/watchlists"

    def get_page(
        self, page_num: int = 1, page_size: int = None, user_id: str = None
    ) -> WatchlistsPage:
        """
        Get a page of watchlists.

        Filter results by passing appropriate parameters:

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **user_id**: `str` - Matches watchlists where the user is a member.

        **Returns**: A [`WatchlistsPage`][watchlistspage-model] object.
        """
        page_size = page_size or self._parent.settings.page_size
        data = ListWatchlistsRequest(page=page_num, pageSize=page_size, userId=user_id)
        response = self._parent.session.get(self._uri, params=data.dict())
        return WatchlistsPage.parse_response(response)

    def iter_all(
        self, page_size: int = None, user_id: str = None
    ) -> Iterator[Watchlist]:
        """
        Iterate over all watchlists.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Watchlist`][watchlist-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                page_num=page_num, page_size=page_size, user_id=user_id
            )
            yield from page.watchlists
            if len(page.watchlists) < page_size:
                break

    def get(self, watchlist_id: str) -> Watchlist:
        """
        Get a single watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: A [`Watchlist`][watchlist-model] object.
        """
        response = self._parent.session.get(f"{self._uri}/{watchlist_id}")
        return Watchlist.parse_response(response)

    def create(
        self, watchlist_type: WatchlistType, title: str = None, description: str = None
    ) -> Watchlist:
        """
        Create a new watchlist.

        **Parameters**:

        * **watchlist_type**: [`WatchlistType`][watchlist-types] (required) - Type of the watchlist to create.
        * **title**: The required title for a custom watchlist.
        * **description**: The optional description for a custom watchlist.

        **Returns**: A ['Watchlist`][watchlist-model] object.
        """
        if watchlist_type == "CUSTOM":
            if title is None:
                raise ValueError("`title` value is required for custom watchlists.")

        data = CreateWatchlistRequest(
            description=description, title=title, watchlistType=watchlist_type
        )
        response = self._parent.session.post(url=self._uri, json=data.dict())
        watchlist = Watchlist.parse_response(response)
        self._watchlist_type_id_map[watchlist_type] = watchlist.watchlist_id
        return watchlist

    def delete(self, watchlist_id: str):
        """
        Delete a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.delete(f"{self._uri}/{watchlist_id}")

    def update(
        self, watchlist_id: str, title: str = None, description: str = None
    ) -> Watchlist:
        """
        Update a custom watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **title**: `str` - Updated title for a custom watchlist.  Defaults to None.
        * **description: `str` - Updated description for a custom watchlist.  Pass an empty string to clear this field.  Defaults to None.

        **Returns**: A [`Watchlist`][watchlist-model] object.
        """
        paths = []
        if title:
            paths += ["title"]
        if description:
            paths += ["description"]
        query = {"paths": paths}
        data = UpdateWatchlistRequest(description=description, title=title)
        response = self._parent.session.patch(
            f"{self._uri}/{watchlist_id}", params=query, json=data.dict()
        )
        return Watchlist.parse_response(response)

    def get_member(self, watchlist_id: str, user_id: str) -> WatchlistUser:
        """
        Get a single member of a watchlist. A member may have been added as an included user, or is a member of an included department, etc.

        **Parameters**:

         * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.

        **Returns**: A [`WatchlistUser`][watchlistuser-model] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/members/{user_id}"
        )
        return WatchlistUser.parse_response(response)

    def list_members(
        self, watchlist_id: Union[str, WatchlistType]
    ) -> WatchlistMembersList:
        """
        Get a list of all members of a watchlist. These users may have been added as an included user, or are members of an included department, etc.

        **Parameters**:

        * **watchlist_id**: `str`(required) - Watchlist ID.

        **Returns**: A [`WatchlistMembersList`][watchlistmemberslist-model] object.
        """
        response = self._parent.session.get(f"{self._uri}/{watchlist_id}/members")
        return WatchlistMembersList.parse_response(response)

    def add_included_users(self, watchlist_id: str, user_ids: Union[str, List[str]]):
        """
        Include individual users on a watchlist.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to include on the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateIncludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
            watchlistId=watchlist_id,
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-users/add", json=data.dict()
        )

    def remove_included_users(self, watchlist_id: str, user_ids: Union[str, List[str]]):
        """
        Remove included users from a watchlist.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to remove from the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """

        data = UpdateIncludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
            watchlistId=watchlist_id,
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-users/delete", json=data.dict()
        )

    def get_included_user(self, watchlist_id: str, user_id: str) -> WatchlistUser:
        """
        Get an included user from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.

        **Returns**: A [`WatchlistUser`][watchlistuser-model] object.
        """
        response = self._parent.session.get(
            url=f"{self._uri}/{watchlist_id}/included-users/{user_id}"
        )
        return WatchlistUser.parse_response(response)

    def list_included_users(self, watchlist_id: str) -> IncludedUsersList:
        """
        List individual users included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedUsersList`][includeduserslist-model] object.
        """

        response = self._parent.session.get(
            url=f"{self._uri}/{watchlist_id}/included-users"
        )
        return IncludedUsersList.parse_response(response)

    def add_excluded_users(self, watchlist_id: str, user_ids: Union[str, List[str]]):
        """
        Exclude individual users from a watchlist.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to exclude from the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateExcludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/excluded-users/add", json=data.dict()
        )

    def remove_excluded_users(self, watchlist_id: str, user_ids: Union[str, List[str]]):
        """
        Remove excluded users from a watchlist.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to remove from the exclusion list.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateExcludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/excluded-users/delete", json=data.dict()
        )

    def list_excluded_users(self, watchlist_id: str) -> ExcludedUsersList:
        """
        List individual users excluded from a watchlist.

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`ExcludedUsersList`][excludeduserslist-model] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/excluded-users"
        )
        return ExcludedUsersList.parse_response(response)

    def get_excluded_user(self, watchlist_id: str, user_id: str) -> WatchlistUser:
        """
        Get an excluded user from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.

        **Returns**: A [`WatchlistUser`][watchlistuser-model] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/excluded-users/{user_id}"
        )
        return WatchlistUser.parse_response(response)

    def add_directory_groups(self, watchlist_id: str, group_ids: Union[str, List[str]]):
        """
        Include directory groups on a watchlist. Use the `directory_groups` client to see available directory groups.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **group_ids**: `str`, `List[str]` (required) - List of directory group IDs to include on the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateIncludedDirectoryGroupsRequest(
            groupIds=group_ids if isinstance(group_ids, List) else [group_ids]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-directory-groups/add",
            json=data.dict(),
        )

    def remove_directory_groups(
        self, watchlist_id: str, group_ids: Union[str, List[str]]
    ):
        """
        Remove included directory groups from a watchlist.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **group_ids**: `str`, `List[str]` (required) - List of directory group IDs to remove from the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateIncludedDirectoryGroupsRequest(
            groupIds=group_ids if isinstance(group_ids, List) else [group_ids]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-directory-groups/delete",
            json=data.dict(),
        )

    def list_directory_groups(self, watchlist_id: str) -> IncludedDirectoryGroupsList:
        """
        List directory groups included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedUsersList`][includeduserslist-model] object.
        """

        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-directory-groups"
        )
        return IncludedDirectoryGroupsList.parse_response(response)

    def get_directory_group(
        self, watchlist_id: str, group_id: str
    ) -> IncludedDirectoryGroup:
        """
        Get an included directory group from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **group_id**: `str` (required) - Directory group ID.

        **Returns**: An [`IncludedDirectoryGroup`][includeddirectorygroup-model] object.
        """

        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-directory-groups/{group_id}"
        )
        return IncludedDirectoryGroup.parse_response(response)

    def add_departments(
        self,
        watchlist_id: str,
        departments: Union[str, List[str]],
    ):
        """
        Include departments on a watchlist. Use the `departments` client to see available departments.

        **Parameters**:

        * **watchlist**: `str` (required) - Watchlist ID.
        * **departments**: `str`, `List[str]` (required) - List of departments to include on the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateIncludedDepartmentsRequest(
            departments=departments if isinstance(departments, List) else [departments]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-departments/add", json=data.dict()
        )

    def remove_departments(
        self,
        watchlist_id: str,
        departments: Union[str, List[str]],
    ):
        """
        Remove included departments from a watchlist.

        **Parameters**:

        * **watchlist**: `str` - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **departments**: `str`, `List[str]` (required) - List of departments to remove from the watchlist.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateIncludedDepartmentsRequest(
            departments=departments if isinstance(departments, List) else [departments]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-departments/delete",
            json=data.dict(),
        )

    def list_departments(self, watchlist_id: str) -> IncludedDepartmentsList:
        """
        List departments included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedDepartmentsList`][includeddepartmentslist-model] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-departments"
        )
        return IncludedDepartmentsList.parse_response(response)

    def get_department(self, watchlist_id: str, department: str) -> IncludedDepartment:
        """
        Get an included department from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **department**: `str` (required) - A included department.

        **Returns**: An [`IncludedDepartment`][includeddepartment-model] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-departments/{department}"
        )
        return IncludedDepartment.parse_response(response)

    def get_id_by_name(self, name: Union[str, WatchlistType]):
        """
        Get a watchlist ID by either its type (ex: `DEPARTING_EMPLOYEE`) or its title in the case of `CUSTOM` watchlists.

        **Parameters**:

        * **name**: `str`, [`WatchlistType`][watchlist-types] (required) - A `WatchlistType` or in the case of `CUSTOM` watchlists, the watchlist `title`.

        **Returns**: A watchlist ID (`str`).
        """

        def _lookup_ids(self):
            """Map watchlist types to IDs, if they exist."""
            self._watchlist_type_id_map = {}
            watchlists = self.get_page(page_size=100).watchlists
            for item in watchlists:
                if item.list_type == "CUSTOM":
                    # store title for custom lists instead of list_type
                    self._watchlist_type_id_map[item.title] = item.watchlist_id
                self._watchlist_type_id_map[item.list_type] = item.watchlist_id

        watchlist_id = self._watchlist_type_id_map.get(name)
        if not watchlist_id:
            # if not found, reset ID cache
            _lookup_ids(self)
            watchlist_id = self._watchlist_type_id_map.get(name)
            if not watchlist_id:
                raise WatchlistNotFoundError(name)
        return watchlist_id
