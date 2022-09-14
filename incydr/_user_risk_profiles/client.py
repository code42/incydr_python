from datetime import datetime
from itertools import count
from typing import Iterator
from typing import List

from requests import Response

from incydr._user_risk_profiles.models import Date
from incydr._user_risk_profiles.models import QueryUserRiskProfilesRequest
from incydr._user_risk_profiles.models import UserRiskProfile
from incydr._user_risk_profiles.models import UserRiskProfilesPage


class UserRiskProfilesV1:
    """
    Client for `/v1/user-risk-profiles` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.user_risk_profiles.v1
    """

    def __init__(self, parent):
        self._parent = parent

    def get_user_risk_profile(self, user_id: str) -> UserRiskProfile:
        """
        Get a single user risk profile.
        **Parameters:**
        * **user_id**: `str` (required) - The unique ID for the user.
        **Returns**: A [`UserRiskProfile`][user-risk-profile-model] object representing the user risk profile.
        """
        response = self._parent.session.get(f"/v1/user-risk-profiles/{user_id}")
        return UserRiskProfile.parse_response(response)

    def get_page(
            self,
            page: int = 1,
            page_size: int = 100,
            manager_id: str = None,
            title: str = None,
            division: str = None,
            department: str = None,
            employment_type: str = None,
            country: str = None,
            region: str = None,
            locality: str = None,
            active: bool = None,
            deleted: bool = None,
            support_user: bool = None,
    ) -> UserRiskProfilesPage:
        """
        Get a page of user risk profiles.
        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **page**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **manager_id**: `str` - The Code42 user ID of the user's manager to search for.
        * **title**: `str` - The user's job title to search for.
        * **division**: `str` - The user's division to search for.
        * **department**: `str` - The user's department to search for.
        * **employment_type**: `str` - The user's employment type to search for.
        * **country**: `str` - The user's country to search for.
        * **region**: `str` - The user's region (state) to search for.
        * **locality**: `str` - The user's locality (city) to search for.
        * **active**: `bool` - When true, return only active users. When false, return only inactive users.
                               Defaults to returning both.
        * **deleted**: `bool` - When true, return only deleted users. When false, return only non-deleted users.
                                Defaults to returning both.
        * **support_user**: `bool` - When true, return only support users. When false, return only non-support users.
                                     Defaults to returning both

        **Returns**: A ['UserRiskProfilesPage'][users-risk-profiles-page-model] object.
        """
        page_size = page_size or self._parent.settings.page_size
        data = QueryUserRiskProfilesRequest(
            page=page,
            page_size=page_size,
            manager_id=manager_id,
            title=title,
            division=division,
            department=department,
            employment_type=employment_type,
            country=country,
            region=region,
            locality=locality,
            active=active,
            deleted=deleted,
            supportUser=support_user,
        )
        response = self._parent.session.get(
            "/v1/user-risk-profiles", params=data.dict()
        )
        return UserRiskProfilesPage.parse_response(response)

    def iter_all(
            self,
            page_size: int = 100,
            manager_id: str = None,
            title: str = None,
            division: str = None,
            department: str = None,
            employment_type: str = None,
            country: str = None,
            region: str = None,
            locality: str = None,
            active: bool = None,
            deleted: bool = None,
            support_user: bool = None,
    ) -> Iterator[UserRiskProfile]:
        """
        Iterate over all user risk profiles.
        Accepts the same parameters as `.get_page()` except `page_num`.
        **Returns**: A generator yielding individual [`UserRiskProfile`][user-risk-profile-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                page=page_num,
                page_size=page_size,
                manager_id=manager_id,
                title=title,
                division=division,
                department=department,
                employment_type=employment_type,
                country=country,
                region=region,
                locality=locality,
                active=active,
                deleted=deleted,
                support_user=support_user,
            )
            yield from page.userRiskProfiles
            if len(page.userRiskProfiles) < page_size:
                break

    def update(
            self,
            user_id: str,
            notes: str = None,
            start_date: datetime = None,
            end_date: datetime = None
    ) -> UserRiskProfile:
        """
        Updates a user risk profile.

        **Parameters**

        * **user_risk_profile**: [`UserRiskProfile`][user-risk-profile-model] The modified case object.

        Usage example:

            >>> client.user_risk_profiles.v1.update("34", "These are some notes",
            >>>      "2020-12-23T14:24:44.593Z", "2022-07-18T16:40:53.335132Z")

        **Returns**: A [`UserRiskProfile`][user-risk-profile-model] object with updated values from server.
        """

        datetime_start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        datetime_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ')

        response = self._parent.session.post(
            f"/v1/user-risk-profiles/{user_id}",
            json={"notes": notes,
                  "startDate": Date(day=datetime_start.day, month=datetime_start.month,
                                    year=datetime_start.year),
                  "endDate": Date(day=datetime_end.day, month=datetime_end.month, year=datetime_end.year)
                  },
        )
        return UserRiskProfile.parse_response(response)

    def add_cloud_aliases(self, user_id: str, cloud_aliases: List[str]) -> Response:
        """
        Add cloud aliases to user id

        **Parameters:**

        * **user_id**: `str` Unique numeric identifier for the user risk profile.
        * **cloud_aliases**: `str | List[str]` A string or list of strings representing the cloud aliases to attach
            to the user id.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(
            f"/v1/user-risk-profiles/{user_id}/add-cloud-aliases",
            json={"userId": user_id, "cloudAliases": cloud_aliases},
        )

    def delete_cloud_aliases(self, user_id: str, cloud_aliases: List[str]) -> Response:
        """
        Delete cloud aliases for user id

        **Parameters:**

        * **user_id**: `str` Unique numeric identifier for the user risk profile.
        * **cloud_aliases**: `str | List[str]` A string or list of strings representing the cloud aliases to delete
            from the user id.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(
            f"/v1/user-risk-profiles/{user_id}/delete-cloud-aliases",
            json={"userId": user_id, "cloudAliases": cloud_aliases},
        )


class UserRiskProfiles:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = UserRiskProfilesV1(self._parent)
        return self._v1
