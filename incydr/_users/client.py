from itertools import count
from typing import Iterator

from incydr._devices.models import DevicesPage, QueryDevicesRequest, SortKeys
from incydr._users.models import User, UsersPage, QueryUsersRequest
from incydr.enums import SortDirection


class UsersV1:
    """Users V1 Client"""

    default_page_size = 100
    endpoint_prefix = "/v1/users"

    def __init__(self, session):
        self._session = session

    def get_user(self, user_id: str) -> User:
        response = self._session.get(f"/v1/users/{user_id}")
        return User.parse_response(response)

    def get_page(
            self,
            active: bool = None,
            blocked: bool = None,
            username: str = None,
            page_num: int = 1,
            page_size: int = default_page_size,
    ) -> UsersPage:
        """Get a page of users."""

        data = QueryUsersRequest(
            active=active,
            blocked=blocked,
            username=username,
            page=page_num,
            pageSize=page_size,
        )
        response = self._session.get("/v1/users", params=data.dict())
        return UsersPage.parse_response(response)

    def get_devices(self,
                    user_id: str,
                    active: bool = None,
                    blocked: bool = None,
                    page_num: int = 1,
                    page_size: int = default_page_size,
                    sort_dir: SortDirection = SortDirection.ASC,
                    sort_key: SortKeys = SortKeys.NAME, ) -> User:
        """Get a page of devices for a specific user."""

        data = QueryDevicesRequest(
            page=page_num,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_dir,
            active=active,
            blocked=blocked,
        )
        response = self._session.get(f"/v1/users/{user_id}/devices", params=data.dict())
        return DevicesPage.parse_response(response)

    def iter_all(
            self,
            active: bool = None,
            blocked: bool = None,
            username: str = None,
            page_size: int = default_page_size,
    ) -> Iterator[User]:
        """Iterate over all users"""

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


class UsersClient:
    def __init__(self, session):
        self._session = session
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = UsersV1(self._session)
        return self._v1
