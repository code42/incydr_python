from itertools import count
from typing import Iterator
from typing import List

from pydantic import parse_obj_as
from requests import Response

from incydr._devices.models import DevicesPage
from incydr._devices.models import QueryDevicesRequest
from incydr._users.models import MoveUserRequest
from incydr._users.models import QueryUsersRequest
from incydr._users.models import Role
from incydr._users.models import UpdateRolesRequest
from incydr._users.models import UpdateRolesResponse
from incydr._users.models import User
from incydr._users.models import UsersPage
from incydr.enums import SortDirection
from incydr.enums.devices import SortKeys


class UsersV1:
    """Client for `/v1/users` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.users.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_user(self, user_id: str = None, username: str = None) -> User:
        """
        Get a single user. At least one parameter is required.

        **Parameters:**

        * **user_id**: `str` - The unique ID for the user.
        * **username**: `str`- The username for the user.  Performs an additional lookup to first get user ID.  Ignored if user_id is also passed.

        **Returns**: A [`User`][user-model] object representing the user.

        """
        if not any([user_id, username]):
            raise ValueError(
                "At least one parameter, user_id or username, is required for get_user()."
            )

        if not user_id:
            users = self.get_page(username=username).users
            if len(users) < 1:
                raise ValueError(f"User with username '{username}' not found.")
            return users[0]

        response = self._parent.session.get(f"/v1/users/{user_id}")
        return User.parse_response(response)

    def get_page(
        self,
        active: bool = None,
        blocked: bool = None,
        username: str = None,
        page_num: int = 1,
        page_size: int = None,
    ) -> UsersPage:
        """
        Get a page of users.

        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **active**: `bool | None` - When true, return only active users. When false, return only inactive users. Defaults to returning both.
        * **blocked**: `bool | None` - When true, return only blocked users. When false, return only unblocked users. Defaults to returning both.
        * **username**: `str` - The username of a user to search for.
        * **page_num**: `int` - Page number for results. Defaulting to 1.
        * **page_size**: `int` - Max number of results to return per page. Defaulting to client's `page_size` setting.

        **Returns**: A [`UsersPage`][userspage-model] object.
        """
        page_size = page_size or self._parent.settings.page_size
        data = QueryUsersRequest(
            active=active,
            blocked=blocked,
            username=username,
            page=page_num,
            pageSize=page_size,
        )
        response = self._parent.session.get("/v1/users", params=data.dict())
        return UsersPage.parse_response(response)

    def get_devices(
        self,
        user_id: str,
        active: bool = None,
        blocked: bool = None,
        page_num: int = 1,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
    ) -> User:
        """
        Get a page of devices associated with a specific user.

        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.
        * **active**: `bool` - Whether or not the device is active. If true, the device will show up on reports, etc.
        * **blocked**: `bool` - Whether or not the device is blocked.  If true, restores and logins are disabled.
        * **page_num**: `int` - Page number for results. Defaulting to 1.
        * **page_size**: `int` - Max number of results to return per page. Defaulting to client's `page_size` settings.
        * **sort_dir**: `SortDirection` - 'asc' or 'desc'. The direction in which to sort the response based on the corresponding key. Defaults to 'asc'.
        * **sort_key**: `SortKeys` - One or more values on which the response will be sorted. Defaults to device name.

        **Returns**: A [`DevicesPage`][devicespage-model] object.
        """
        page_size = page_size or self._parent.settings.page_size
        data = QueryDevicesRequest(
            page=page_num,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_dir,
            active=active,
            blocked=blocked,
        )
        response = self._parent.session.get(
            f"/v1/users/{user_id}/devices", params=data.dict()
        )
        return DevicesPage.parse_response(response)

    def iter_all(
        self,
        active: bool = None,
        blocked: bool = None,
        username: str = None,
        page_size: int = None,
    ) -> Iterator[User]:
        """
        Iterate over all users.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`User`][user-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                active=active,
                blocked=blocked,
                username=username,
                page_num=page_num,
                page_size=page_size,
            )
            yield from page.users
            if len(page.users) < page_size:
                break

    def get_roles(
        self,
        user_id: str,
    ) -> List[Role]:
        """
        Get a list of roles associated with a specific user.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.

        **Returns**: A list of [`Role`][role-model] objects.
        """
        response = self._parent.session.get(f"/v1/users/{user_id}/roles")
        return parse_obj_as(List[Role], response.json()["roles"])

    def update_roles(self, user_id: str, role_ids: List[str]) -> UpdateRolesResponse:
        """
        Update the roles associated with a user.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.
        * **roles_ids**: `List[str]` The new role IDs to assign the user (ex: desktop-user). These will replace the existing roles assigned to the user."

        **Returns**: A [`UpdateRolesResponse`][updaterolesresponse-model] object.
        """
        data = UpdateRolesRequest(roleIds=role_ids)
        response = self._parent.session.put(
            f"/v1/users/{user_id}/roles", json=data.dict()
        )
        return UpdateRolesResponse.parse_response(response)

    def move(self, user_id: str, org_guid: str) -> Response:
        """
        Move a user to a specified organization

        **Parameters**:

        * **user_id**: `str` - The unique ID for the user.
        * **org_guid**: `str` The orgGuid of the org to move the user to."

        **Returns**: A `requests.Response` indicating success.
        """
        data = MoveUserRequest(orgGuid=org_guid)

        return self._parent.session.post(f"/v1/users/{user_id}/move", json=data.dict())

    def activate(self, user_id: str) -> Response:
        """
        Activate a user.

        **Parameters:**

        * **user_id**: `str` (required) - The unique ID for the user.

        **Returns**: A `requests.Response` indicating success.

        """
        return self._parent.session.post(f"/v1/users/{user_id}/activate")

    def deactivate(self, user_id: str) -> Response:
        """
        Deactivate a user.

        **Parameters:**

        * **user_id**: `str` (required) - The unique ID for the user.

        **Returns**: A `requests.Response` indicating success.

        """
        return self._parent.session.post(f"/v1/users/{user_id}/deactivate")


class UsersClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = UsersV1(self._parent)
        return self._v1
