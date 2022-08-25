from typing import List
from typing import Union

from incydr._watchlists.models.requests import CreateWatchlistRequest
from incydr._watchlists.models.requests import GetPageRequest
from incydr._watchlists.models.requests import ListWatchlistsRequest
from incydr._watchlists.models.requests import UpdateExcludedUsersRequest
from incydr._watchlists.models.requests import UpdateIncludedDepartmentsRequest
from incydr._watchlists.models.requests import UpdateIncludedDirectoryGroupsRequest
from incydr._watchlists.models.requests import UpdateIncludedUsersRequest
from incydr._watchlists.models.requests import UpdateWatchlistRequest
from incydr._watchlists.models.responses import DepartmentsPage
from incydr._watchlists.models.responses import DirectoryGroupsPage
from incydr._watchlists.models.responses import ExcludedUser
from incydr._watchlists.models.responses import ExcludedUsersList
from incydr._watchlists.models.responses import IncludedDepartment
from incydr._watchlists.models.responses import IncludedDepartmentsList
from incydr._watchlists.models.responses import IncludedDirectoryGroup
from incydr._watchlists.models.responses import IncludedDirectoryGroupsList
from incydr._watchlists.models.responses import IncludedUser
from incydr._watchlists.models.responses import IncludedUsersList
from incydr._watchlists.models.responses import Watchlist
from incydr._watchlists.models.responses import WatchlistMember
from incydr._watchlists.models.responses import WatchlistMembersList
from incydr._watchlists.models.responses import WatchlistsPage
from incydr.enums.watchlists import WatchlistType


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

    @property
    def watchlist_type_id_map(self):
        """Map watchlist types to IDs, if they exist."""
        if not self._watchlist_type_id_map:
            self._watchlist_type_id_map = {}
            watchlists = self.get_page(page_size=100).watchlists
            for item in watchlists:
                # We will need to custom handle CUSTOM types when they come around
                if item.list_type == "CUSTOM":
                    pass

                self._watchlist_type_id_map[item.list_type] = item.watchlist_id
        return self._watchlist_type_id_map

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

    def get(self, watchlist_id: str) -> Watchlist:
        """
        Get a single watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: A [`Watchlist`] object.
        """
        response = self._parent.session.get(f"{self._uri}/{watchlist_id}")
        return Watchlist.parse_response(response)

    def create(
        self, watchlist_type: WatchlistType, title: str = None, description: str = None
    ) -> Watchlist:
        """
        Create a new watchlist.

        **Parameters**:

        * **watchlist_type**: `WatchlistType` (required) - Type of the watchlist to create.
        * **title**: The required title for a custom watchlist.
        * **description**: The optional description for a custom watchlist.

        **Returns**: A ['Watchlist`] object.
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

        **Returns**: A [`Watchlist`] object.
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

    def get_member(self, watchlist_id: str, user_id: str) -> WatchlistMember:
        """
        Get a single member of a watchlist.

        **Parameters**:

         * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.

        **Returns**: A [`WatchlistMember`] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/members/{user_id}"
        )
        return WatchlistMember.parse_response(response)

    def list_members(
        self, watchlist_id: Union[str, WatchlistType]
    ) -> WatchlistMembersList:
        """
        Get a list of all members of a watchlist.

        **Parameters**:

        * **watchlist_id**: `str`(required) - Watchlist ID.

        **Returns**: A [`WatchlistMembersList`] object.
        """
        response = self._parent.session.get(f"{self._uri}/{watchlist_id}/members")
        return WatchlistMembersList.parse_response(response)

    def add_included_users(
        self, watchlist: Union[str, WatchlistType], user_ids: Union[str, List[str]]
    ):
        """
        Include individual users on a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.   An ID must be provided for custom watchlists.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to add.
        """
        watchlist = self._check_watchlist_id(watchlist)

        data = UpdateIncludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
            watchlistId=watchlist,
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/included-users/add", json=data.dict()
        )

    def remove_included_users(
        self, watchlist: Union[str, WatchlistType], user_ids: Union[str, List[str]]
    ):
        """
        Remove users from a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to remove.
        """
        watchlist = self._check_watchlist_id(watchlist)

        data = UpdateIncludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
            watchlistId=watchlist,
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/included-users/delete", json=data.dict()
        )

    def get_included_user(self, watchlist_id: str, user_id: str) -> IncludedUser:
        """
        Get an included user from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.

        **Returns**: An [`IncludedUser`] object.
        """
        response = self._parent.session.get(
            url=f"{self._uri}/{watchlist_id}/included-users/{user_id}"
        )
        return IncludedUser.parse_response(response)

    def list_included_users(self, watchlist_id: str) -> IncludedUsersList:
        """
        List individual users included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedUsersList`] object.
        """

        response = self._parent.session.get(
            url=f"{self._uri}/{watchlist_id}/included-users"
        )
        return IncludedUsersList.parse_response(response)

    def add_excluded_users(
        self, watchlist: Union[str, WatchlistType], user_ids: Union[str, List[str]]
    ):
        """
        Exclude individual users from a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to exclude.
        """
        data = UpdateExcludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/excluded-users/add", json=data.dict()
        )

    def remove_excluded_users(
        self, watchlist: Union[str, WatchlistType], user_ids: Union[str, List[str]]
    ):
        """
        Remove excluded users from a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **user_ids**: `str`, `List[str]` (required) - List of unique user IDs to remove from the exclusion list.
        """
        data = UpdateExcludedUsersRequest(
            userIds=user_ids if isinstance(user_ids, List) else [user_ids],
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/excluded-users/delete", json=data.dict()
        )

    def list_excluded_users(self, watchlist_id: str) -> ExcludedUsersList:
        """
        List individual users excluded from a watchlist.

        * **watchlist_id**: `str` (required) - Watchlist ID.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/excluded-users"
        )
        return ExcludedUsersList.parse_response(response)

    def get_excluded_user(self, watchlist_id: str, user_id: str) -> ExcludedUser:
        """
        Get an excluded user from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **user_id**: `str` (required) - Unique user ID.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/excluded-users/{user_id}"
        )
        return ExcludedUser.parse_response(response)

    # TODO: should these be called add_included_directory_groups/remove_included_directory_groups and add_included_departments/remove_departments

    def add_directory_groups(
        self, watchlist: Union[str, WatchlistType], group_ids: Union[str, List[str]]
    ):
        """
        Include directory group on a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **group_ids**: `str`, `List[str]` (required) - List of directory group IDs to add to the watchlist.
        """
        watchlist = self._check_watchlist_id(watchlist)

        data = UpdateIncludedDirectoryGroupsRequest(
            groupIds=group_ids if isinstance(group_ids, List) else [group_ids]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/included-directory-groups/add",
            json=data.dict(),
        )

    def remove_directory_groups(
        self, watchlist: Union[str, WatchlistType], group_ids: Union[str, List[str]]
    ):
        """
        Remove an included directory group from a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **group_ids**: `str`, `List[str]` (required) - List of directory group IDs to remove from the watchlist.
        """
        watchlist = self._check_watchlist_id(watchlist, create_if_not_found=False)

        data = UpdateIncludedDirectoryGroupsRequest(
            groupIds=group_ids if isinstance(group_ids, List) else [group_ids]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist}/included-directory-groups/delete",
            json=data.dict(),
        )

    def list_included_directory_groups(
        self, watchlist_id: str
    ) -> IncludedDirectoryGroupsList:
        """
        List directory groups included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedUsersList`] object.
        """

        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-directory-groups"
        )
        return IncludedDirectoryGroupsList.parse_response(response)

    def get_included_directory_group(
        self, watchlist_id: str, group_id: str
    ) -> IncludedDirectoryGroup:
        """
        Get an included directory group from a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **group_id**: `str` (required) - Directory group ID.

        **Returns**: An [`IncludedDirectoryGroup`] object.
        """

        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-directory-groups/{group_id}"
        )
        return IncludedDirectoryGroup.parse_response(response)

    def add_departments(
        self,
        watchlist_id: Union[str, WatchlistType],
        departments: Union[str, List[str]],
    ):
        """
        Include a department on a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **departments**: `str`, `List[str]` (required) - List of departments to add to the watchlist.
        """
        watchlist_id = self._check_watchlist_id(watchlist_id)

        data = UpdateIncludedDepartmentsRequest(
            departments=departments if isinstance(departments, List) else [departments]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-departments/add", json=data.dict()
        )

    def remove_departments(
        self,
        watchlist_id: Union[str, WatchlistType],
        departments: Union[str, List[str]],
    ):
        """
        Remove an included department from a watchlist.

        **Parameters**:

        * **watchlist**: `str`, `WatchlistType` (required) - Watchlist ID or a watchlist type.  An ID must be provided for custom watchlists.
        * **departments**: `str`, `List[str]` (required) - List of departments to remove from the watchlist.
        """
        watchlist_id = self._check_watchlist_id(watchlist_id, create_if_not_found=False)

        data = UpdateIncludedDepartmentsRequest(
            departments=departments if isinstance(departments, List) else [departments]
        )
        return self._parent.session.post(
            url=f"{self._uri}/{watchlist_id}/included-departments/delete",
            json=data.dict(),
        )

    def list_included_departments(self, watchlist_id: str) -> IncludedDepartmentsList:
        """
        List departments included on a watchlist.

        **Parameters**:

        * **watchlist_id**: `str` (required) - Watchlist ID.

        **Returns**: An [`IncludedDepartmentsList`] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-departments"
        )
        return IncludedDepartmentsList.parse_response(response)

    def get_included_department(
        self, watchlist_id: str, department: str
    ) -> IncludedDepartment:
        """
        Get an included department from a watchlist.

        * **watchlist_id**: `str` (required) - Watchlist ID.
        * **department**: `str` (required) - A included department.

        **Returns**: An [`IncludedDepartment`] object.
        """
        response = self._parent.session.get(
            f"{self._uri}/{watchlist_id}/included-departments/{department}"
        )
        return IncludedDepartment.parse_response(response)

    # TODO: do we want departments page and directory-groups page methods in the watchlists client?

    def get_departments_page(
        self, page_num: int = 1, page_size=None, name=None
    ) -> DepartmentsPage:
        """
        Get a page of departments.  Retrieves department information that has been pushed to Code42 from SCIM or User Directory Sync.
        The resulting department names can be used to include departments on watchlists.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **user_id**: `str` - Matches departments whose name is like the given value.

        **Returns**: A [`DepartmentsPage`] object.
        """
        data = GetPageRequest(
            page=page_num,
            page_size=page_size or self._parent.settings.page_size,
            name=name,
        )
        response = self._parent.session.get("/v1/departments", params=data.dict())
        return DepartmentsPage.parse_response(response)

    def get_directory_groups_page(
        self, page_num: int = 1, page_size=None, name=None
    ) -> DirectoryGroupsPage:
        """
        Get a page of directory groups. Retrieves directory group information that has been pushed to Code42 from SCIM or User Directory Sync.
        The resulting group IDs can be used to include directory groups on watchlists.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **user_id**: `str` - Matches directory groups whose name is like the given value.

        **Returns**: A [`DirectoryGroupsPage`] object.
        """

        data = GetPageRequest(
            page=page_num,
            page_size=page_size or self._parent.settings.page_size,
            name=name,
        )
        response = self._parent.session.get("/v1/directory-groups", params=data.dict())
        return DirectoryGroupsPage.parse_response(response)

    # TODO: Do we want to allow people to pass watchlist types instead of IDs? If yes - in what cases?

    def _check_watchlist_id(
        self, watchlist: Union[str, WatchlistType], create_if_not_found=True
    ):
        """
        Check if the watchlist identifier is an ID or a type enum.
        Default to creating the watchlist of the specified type if it doesn't exist.
        """

        # if not watchlist type enum, then its an ID
        try:
            WatchlistType(watchlist)
        except ValueError:
            return watchlist

        if watchlist == "CUSTOM":
            raise ValueError(
                "The Watchlist ID is required to update custom watchlists."
            )

        watchlist_id = self.watchlist_type_id_map.get(watchlist)
        if not watchlist_id:
            if create_if_not_found:
                return self.create(watchlist).watchlist_id
            else:
                raise ValueError(f"Watchlist of type `{watchlist}` not found.")
