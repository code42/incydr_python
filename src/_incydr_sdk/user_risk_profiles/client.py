from datetime import datetime
from itertools import count
from typing import Iterator
from typing import Union

from requests import Response

from _incydr_sdk.exceptions import DateParseError
from _incydr_sdk.queries.utils import DATE_STR_FORMAT
from _incydr_sdk.user_risk_profiles.models import Date
from _incydr_sdk.user_risk_profiles.models import QueryUserRiskProfilesRequest
from _incydr_sdk.user_risk_profiles.models import UpdateUserRiskProfileRequest
from _incydr_sdk.user_risk_profiles.models import UserRiskProfile
from _incydr_sdk.user_risk_profiles.models import UserRiskProfilesPage


class UserRiskProfiles:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = UserRiskProfilesV1(self._parent)
        return self._v1


class UserRiskProfilesV1:
    """
    Client for `/v1/user-risk-profiles` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.user_risk_profiles.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_user_risk_profile(self, user_id: str) -> UserRiskProfile:
        """
        Get a single user risk profile.

        **Parameters:**

        * **user_id**: `str` (required) - The unique ID for the user.

        **Returns**: A [`UserRiskProfile`][userriskprofile-model] object representing the user risk profile.
        """
        response = self._parent.session.get(f"/v1/user-risk-profiles/{user_id}")
        return UserRiskProfile.parse_response(response)

    def get_page(
        self,
        page_num: int = 1,
        page_size: int = None,
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

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **manager_id**: `str` - The Code42 user ID of the user's manager to search for.
        * **title**: `str` - The user's job title to search for.
        * **division**: `str` - The user's division to search for.
        * **department**: `str` - The user's department to search for.
        * **employment_type**: `str` - The user's employment type to search for.
        * **country**: `str` - The user's country to search for.
        * **region**: `str` - The user's region (state) to search for.
        * **locality**: `str` - The user's locality (city) to search for.
        ** **active**: `bool | None` - When true, return only active users. When false, return only inactive users.
                                       Defaults to `None` (returning both).
        * **deleted**: `bool | None` - When true, return only deleted users. When false, return only non-deleted users.
                                       Defaults to returning both.
        * **support_user**: `bool | None` - When true, return only support users. When false, return only non-support users.
                                            Defaults to returning both

        **Returns**: A ['UserRiskProfilesPage'][userriskprofilespage-model] object.
        """
        page_size = page_size or self._parent.settings.page_size
        data = QueryUserRiskProfilesRequest(
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
        response = self._parent.session.get(
            "/v1/user-risk-profiles", params=data.dict()
        )
        return UserRiskProfilesPage.parse_response(response)

    def iter_all(
        self,
        page_size: int = None,
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

        **Returns**: A generator yielding individual [`UserRiskProfile`][userriskprofile-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                page_num=page_num,
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
            yield from page.user_risk_profiles
            if len(page.user_risk_profiles) < page_size:
                break

    def update(
        self,
        user_id: str,
        notes: str = None,
        start_date: Union[datetime, str] = None,
        end_date: Union[datetime, str] = None,
    ) -> UserRiskProfile:
        """
        Updates a user risk profile.

        **Parameters**

        * **notes**: `str` - Additional notes for the user risk profile.
        * **start_date**: `datetime` - The starting date for the user. Accepts a datetime object or a string in the format yyyy-MM-dd (UTC) format. Pass an empty string to clear the field.
        * **end_date**: `datetime` - The departure date for the user.  Accepts a datetime object or a string in the format yyyy-MM-dd (UTC) format.  Pass an empty string to clear the field.

        **Returns**: A [`UserRiskProfile`][userriskprofile-model] object.
        """
        paths = []
        if start_date is not None:
            paths += ["startDate"]
            start_date = None if start_date == "" else _create_date(start_date)
        if end_date is not None:
            paths += ["endDate"]
            end_date = None if end_date == "" else _create_date(end_date)
        if notes is not None:
            paths += ["notes"]
            if notes == "":
                notes = None

        data = UpdateUserRiskProfileRequest(
            endDate=end_date, notes=notes, startDate=start_date
        )

        response = self._parent.session.patch(
            f"/v1/user-risk-profiles/{user_id}",
            params={"paths": paths},
            json=data.dict(),
        )
        return UserRiskProfile.parse_response(response)

    def add_cloud_alias(self, user_id: str, cloud_alias: str) -> Response:
        """
        Add cloud aliases to a user risk profile.

        A cloud alias is the username an employee uses to access cloud services such as Google Drive or Box.
        Adding a cloud alias allows Incydr to link a user's cloud activity with their Code42 username.
        Each user has a default cloud alias of their Code42 username. You can add one additional alias.

        **Parameters:**

        * **user_id**: `str` - User ID of the profile to update.
        * **cloud_alias**: `str` - The new cloud alias to add to the user risk profile.

        **Returns**: A `requests.Response` indicating success.
        """

        return self._parent.session.post(
            f"/v1/user-risk-profiles/{user_id}/add-cloud-aliases",
            json={"userId": user_id, "cloudAliases": [cloud_alias]},
        )

    def delete_cloud_alias(self, user_id: str, cloud_alias: str) -> Response:
        """
        Delete a cloud alias from a user risk profile.

        **Parameters:**

        * **user_id**: `str` - User ID of the profile to update.
        * **cloud_alias**: `str` - The cloud alias to remove from the user risk profile.

        **Returns**: A `requests.Response` indicating success.
        """

        return self._parent.session.post(
            f"/v1/user-risk-profiles/{user_id}/delete-cloud-aliases",
            json={"userId": user_id, "cloudAliases": [cloud_alias]},
        )


def _create_date(date: Union[datetime, str]):
    if not isinstance(date, datetime):
        try:
            date = datetime.strptime(date, DATE_STR_FORMAT)
        except ValueError:
            raise DateParseError(
                date,
                msg=f"DateParseError: Error parsing time data. Date '{date}' does not match format {DATE_STR_FORMAT}.",
            )
    return Date(day=date.day, month=date.month, year=date.year)
