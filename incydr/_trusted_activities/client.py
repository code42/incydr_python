from itertools import count
from typing import Iterator
from typing import List

from requests import Response

from incydr._trusted_activities.models import ActivityActionGroup
from incydr._trusted_activities.models import CreateTrustedActivityRequest
from incydr._trusted_activities.models import QueryTrustedActivitiesRequest
from incydr._trusted_activities.models import TrustedActivitiesPage
from incydr._trusted_activities.models import TrustedActivity
from incydr._trusted_activities.models import UpdateTrustedActivity
from incydr.enums import SortDirection
from incydr.enums.trusted_activities import ActivityType
from incydr.enums.trusted_activities import SortKeys


class TrustedActivitiesV2:
    """
    Client for `/v2/trusted-activites` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.trusted_activities.v2.get_page()

    """

    def __init__(self, parent):
        self._parent = parent

    def get_trusted_activity(self, activity_id: str) -> TrustedActivity:
        """
        Get a single trusted activity.

        **Parameters:**

        * **activity_id**: `str` (required) - The unique ID for the trusted activity.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing the trusted activity.
        """

        response = self._parent.session.get(f"/v2/trusted-activities/{activity_id}")
        return TrustedActivity.parse_response(response)

    def get_page(
        self,
        page_num: int = 1,
        page_size: int = None,
        activity_type: ActivityType = None,
        sort_key: SortKeys = None,
        sort_direction: SortDirection = None,
    ) -> TrustedActivitiesPage:
        """
        Get a page of trusted activities.
        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **activity_type**: `str` - The type of the trusted activity.
        * **sort_key**: `str` - The key by which to sort the returned list.
        * **sort_direction**: `str` - The order in which to sort the returned list.

        **Returns**: A [`TrustedActivitiesPage`][trustedactivitiespage-model] object.
        """

        page_size = page_size or self._parent.settings.page_size
        data = QueryTrustedActivitiesRequest(
            page_num=page_num,
            page_size=page_size,
            activity_type=activity_type,
            sort_key=sort_key,
            sort_direction=sort_direction,
        )
        response = self._parent.session.get(
            "/v2/trusted-activities", params=data.dict()
        )
        return TrustedActivitiesPage.parse_response(response)

    def iter_all(
        self,
        page_size: int = None,
        activity_type: ActivityType = None,
        sort_key: SortKeys = None,
        sort_direction: SortDirection = None,
    ) -> Iterator[TrustedActivity]:
        """
        Iterate over all trusted activities.
        Accepts the same parameters as `.get_page()` except `page_num`.

        **Returns**: A generator yielding individual [`TrustedActivity`][trustedactivity-model] objects.
        """

        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                page_num=page_num,
                page_size=page_size,
                activity_type=activity_type,
                sort_key=sort_key,
                sort_direction=sort_direction,
            )
            yield from page.trusted_activities
            if len(page.trusted_activities) < page_size:
                break

    def create(
        self,
        activity_type: ActivityType,
        value: str,
        description: str = None,
        activity_action_groups: List[ActivityActionGroup] = None,
    ) -> TrustedActivity:
        """
        Create a trusted activity.

        **Parameters:**

        * **activity_type**: `ActivityType` The type of the trusted activity.
        * **value**: `str` The value of the trusted activity.
        * **description**: `str` A description of the trusted activity.
        * **activity_action_groups**: `List[ActivityActionGroup]` The list of activity
        actions associated with the activity.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        data = CreateTrustedActivityRequest(
            activity_type=activity_type,
            value=value,
            description=description,
            activity_action_groups=activity_action_groups,
        )
        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def delete(self, activity_id: int) -> Response:
        """
        Delete a trusted activity.

        **Parameters**:

        * **activity_id** `int` Unique numeric identifier for the trusted activity.

        Usage example:

            >>> client.trusted_activities.v2.delete(23)
            <Response [200]>

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.delete(f"/v2/trusted-activities/{activity_id}")

    def update(
        self, activity_id: int, trusted_activity: TrustedActivity
    ) -> TrustedActivity:
        """
        Updates a trusted activity.
        Valid updatable fields: description, value, activity_type, activity_action_group

        **Parameters**

        * **activity_id** `int` Unique numeric identifier for the trusted activity.
        * **trusted_activity**: [`TrustedActivity`][trustedactivity-model] The modified trusted activity object.

        Usage example:

            >>> activity = client.trusted_activities.get_trusted_activity(2)
            >>> activity.description = "New description"
            >>> client.trusted_activities.v2.update(2, activity)

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object with updated values from server.
        """

        data = UpdateTrustedActivity(**trusted_activity.dict())
        response = self._parent.session.patch(
            f"/v2/trusted-activities/{activity_id}", json=data.dict(by_alias=True)
        )
        return TrustedActivity.parse_response(response)


class TrustedActivitiesClient:
    def __init__(self, parent):
        self._parent = parent
        self._v2 = None

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = TrustedActivitiesV2(self._parent)
        return self._v2
