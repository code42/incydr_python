from itertools import count
from typing import Iterator
from typing import List
from typing import Union

from pydantic import parse_obj_as
from requests import Response

from _incydr_sdk.devices.models import DevicesPage
from _incydr_sdk.devices.models import QueryDevicesRequest
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.devices import SortKeys
from _incydr_sdk.exceptions import IncydrException
from _incydr_sdk.users.models import QueryUsersRequest
from _incydr_sdk.users.models import Role
from _incydr_sdk.users.models import UpdateRolesResponse
from _incydr_sdk.users.models import User
from _incydr_sdk.users.models import UserRole
from _incydr_sdk.users.models import UsersPage


class UsersClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = UsersV1(self._parent)
        return self._v1


class UsersV1:
    """Client for `/v1/users` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.users.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent
        self._available_roles = {}

    def get_user(self, user: str) -> User:
        """
        Get a single user.

        **Parameters:**

        * **user**: `str` - The unique ID for the user or the username for the user.

        **Returns**: A [`User`][user-model] object representing the user.
        """

        # if username, lookup with get page api
        if "@" in user:
            users = self.get_page(username=user).users
            if len(users) < 1:
                raise ValueError(f"User with username '{user}' not found.")
            return users[0]

        # if user ID, use GET api
        response = self._parent.session.get(f"/v1/users/{user}")
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

    def list_user_roles(
        self,
        user_id: str,
    ) -> List[UserRole]:
        """
        Get a list of roles associated with a specific user.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.

        **Returns**: A list of [`UserRole`][role-model] objects.
        """
        response = self._parent.session.get(f"/v1/users/{user_id}/roles")
        return parse_obj_as(List[UserRole], response.json()["roles"])

    def update_roles(
        self, user_id: str, roles: Union[str, List[str]]
    ) -> UpdateRolesResponse:
        """
        Replace the roles associated with a user.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.
        * **roles**: `str | List[str]` The new roles to assign the user (ex: desktop-user). These will replace the existing roles assigned to the user. Accepts either role IDs or role names."

        **Returns**: A [`UpdateRolesResponse`][updaterolesresponse-model] object.
        """
        if not isinstance(roles, List):
            roles = [roles]

        roles = [self._get_id_by_name(role) for role in roles]

        response = self._parent.session.put(
            f"/v1/users/{user_id}/roles", json={"roleIds": roles}
        )
        return UpdateRolesResponse.parse_response(response)

    def add_roles(
        self, user_id: str, roles: Union[str, List[str]]
    ) -> UpdateRolesResponse:
        """
        Add a role, or multiple roles, to a user's existing roles.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.
        * **roles**: `str | List[str]` The roles to add to the user. Accepts either role IDs or role names (case-sensitive)."

        **Returns**: A [`UpdateRolesResponse`][updaterolesresponse-model] object.
        """
        roles = self._update_role_ids_for_user(roles, user_id, add=True)
        response = self._parent.session.put(
            f"/v1/users/{user_id}/roles", json={"roleIds": roles}
        )
        return UpdateRolesResponse.parse_response(response)

    def remove_roles(
        self, user_id: str, roles: Union[str, List[str]]
    ) -> UpdateRolesResponse:
        """
        Remove a role, or multiple roles, from a user's current roles.

        **Parameters**:

        * **user_id**: `str` (required) - The unique ID for the user.
        * **roles**: `str | List[str]` The roles to remove from the user. Accepts either role IDs or role names."
        """
        roles = self._update_role_ids_for_user(roles, user_id, add=False)
        response = self._parent.session.put(
            f"/v1/users/{user_id}/roles", json={"roleIds": roles}
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
        return self._parent.session.post(
            f"/v1/users/{user_id}/move", json={"orgGuid": org_guid}
        )

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

    def list_roles(self) -> List[Role]:
        """
        Get a list of all available roles that can be assigned by the current user.

        **Parameters**:

        **Returns**: A list of [`UserRole`][role-model] objects.
        """
        response = self._parent.session.get("/v1/users/roles")
        return parse_obj_as(List[Role], response.json())

    def get_role(self, role: str) -> Role:
        """
        Get details for a single role.

        **Parameters**:

        * **role**: `str` (required) - Role ID or role name (case-sensitive).
        """
        response = self._parent.session.get(
            f"/v1/users/roles/{self._get_id_by_name(role)}"
        )
        return Role.parse_response(response)

    def _get_id_by_name(self, role_name: str):
        """
        Get a role ID by its name.

        Returns the role ID unchanged if it doesn't match any names of available roles.
        """
        if not self._available_roles:
            self._lookup_roles()
        for name, id_ in self._available_roles.items():
            if (role_name == name) or (role_name == id_):
                return id_
        raise RoleNotFoundError(role_name)

    def _update_role_ids_for_user(self, roles, user_id, add=True):
        """
        Adds or removes a role ID specified by `role` to the list of user's role IDs,
        which can be passed to the update roles method.

        Where `role_name` is either a role name or a role ID.

        Returns the updated list of role IDs for a user.
        """
        errors = []

        role_ids = [i.role_id for i in self.list_user_roles(user_id)]

        if not self._available_roles:
            self._lookup_roles()

        if not isinstance(roles, List):
            roles = [roles]

        for role in roles:
            try:
                id_ = self._get_id_by_name(role)
            except RoleNotFoundError as err:
                errors.append(err)
                continue
            if add:
                role_ids.append(id_)
            else:
                try:
                    role_ids.remove(id_)
                except ValueError:
                    errors.append(UserNotAssignedRoleError(id_))

        if errors:
            raise RoleProcessingError(errors)

        return role_ids

    def _lookup_roles(self):
        """Map role names to role ID."""
        self._available_roles = {}
        available_roles = self.list_roles()
        for r in available_roles:
            self._available_roles[r.role_name] = r.role_id


class RoleProcessingError(IncydrException):
    """
    Outputs list of errors that arose during processing.

    Example output:
        incydr._users.client.RoleProcessingError: The following errors arose during role processing:
            * User is not currently assigned the following role: 'alert-emails'. Role cannot be removed.
            * No role matching the following was found: 'fake', or you do not have permission to assign this role.
    """

    def __init__(self, errors):
        message = (
            "The following errors arose during role processing:\n\t* "
            + "\n\t* ".join([str(e) for e in errors])
        )
        super().__init__(message)
        self._errors = errors

    @property
    def errors(self):
        """List of errors that arose during role processing."""
        return self._errors


class UserNotAssignedRoleError(IncydrException):
    def __init__(self, role):
        message = f"User Not Assigned Role Error: User is not currently assigned the following role: '{role}'. Role cannot be removed."
        super().__init__(message)
        self._role = role

    @property
    def role(self):
        """The role which cannot be assigned."""
        return self._role


class RoleNotFoundError(IncydrException):
    def __init__(self, role):
        message = f"Role Not Found Error: No role matching the following was found: '{role}', or you do not have permission to assign this role. Roles can be specified by case-sensitive name (ie. 'Cloud Admin') or ID (ie. cloud-admin)."
        super().__init__(message)
        self._role = role

    @property
    def role(self):
        """The role which could not be found"""
        return self._role
