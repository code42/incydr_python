from itertools import count
from typing import Iterator
from typing import List

from requests import Response

from incydr._trusted_activities.models import ActivityAction
from incydr._trusted_activities.models import ActivityActionGroup
from incydr._trusted_activities.models import CreateTrustedActivityRequest
from incydr._trusted_activities.models import ProviderObject
from incydr._trusted_activities.models import QueryTrustedActivitiesRequest
from incydr._trusted_activities.models import TrustedActivitiesPage
from incydr._trusted_activities.models import TrustedActivity
from incydr._trusted_activities.models import UpdateTrustedActivity
from incydr.enums import SortDirection
from incydr.enums.trusted_activities import ActivityType
from incydr.enums.trusted_activities import DomainCloudSync
from incydr.enums.trusted_activities import Name
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
        * **page_size**: `int` - Max number of results to return per page. Defaults to client's `page_size` setting.
        * **activity_type**: `ActivityType` - The type of the trusted activity.
        * **sort_key**: `SortKeys` - The key by which to sort the returned list.
        * **sort_direction**: `SortDirection` - The order in which to sort the returned list.

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

    def create_trusted_activity_for_domain(
        self,
        domain: str,
        description: str = None,
        file_upload: bool = None,
        cloud_sync_list: List[DomainCloudSync] = None,
        git_push: bool = None,
    ) -> TrustedActivity:
        """
        Create a trusted activity.

        **Parameters:**

        * **domain**: `str` (required) - The domain of the trusted activity.
        * **description**: `str` - A description of the trusted activity.
        * **file_upload**: `bool` - Whether to trust activity if the tab URL or tab title includes this domain.
        * **cloud_sync_list**: `List[DomainCloudSync]` - Activity is trusted if the username signed in to the
        sync app is one of the listed domains (`BOX`, `GOOGLE_DRIVE`, `ICLOUD` and/or `ONEDRIVE`).
        If list is empty, all supported cloud sync domains are trusted.
        * **git_push**: `bool` - Whether to trust Git push events to this domain.


        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        activity_actions = []

        if file_upload:
            activity_actions.append(ActivityAction(type=ActivityType.FILE_UPLOAD))

        if git_push:
            activity_actions.append(ActivityAction(type=ActivityType.GIT_PUSH))

        if len(cloud_sync_list) != 0:
            providers = []

            for cloud_sync in cloud_sync_list:
                if cloud_sync in DomainCloudSync.__members__:
                    providers.append(ProviderObject(name=Name[cloud_sync]))

            activity_actions.append(
                ActivityAction(providers=providers, type=ActivityType.CLOUD_SYNC)
            )

        activity_action_group = ActivityActionGroup(
            activityActions=activity_actions, name=Name.DEFAULT
        )

        data = CreateTrustedActivityRequest(
            type=ActivityType.DOMAIN,
            value=domain,
            description=description,
            activityActionGroups=[activity_action_group],
        )

        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def create_trusted_activity_for_specific_url_path(
        self,
        url: str,
        description: str = None,
    ) -> TrustedActivity:
        """
        Create a trusted activity.

        **Parameters:**

        * **url**: `str` (required) - The url of the trusted activity.
        * **description**: `str` - A description of the trusted activity.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        data = CreateTrustedActivityRequest(
            type=ActivityType.URL_PATH,
            value=url,
            description=description,
            activityActionGroups=[],
        )

        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def create_trusted_activity_for_slack(
        self,
        workspace_name: str,
        description: str = None,
    ) -> TrustedActivity:
        """
        Create a trusted activity.

        **Parameters:**

        * **workspace_name**: `str` (required) - The workspace name of the trusted activity.
        * **description**: `str` - A description of the trusted activity.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        data = CreateTrustedActivityRequest(
            type=ActivityType.SLACK,
            value=workspace_name,
            description=description,
            activityActionGroups=[],
        )

        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def create_trusted_activity_for_account_name(
        self,
        account_name: str,
        description: str = None,
        dropbox: bool = False,
        one_drive: bool = False,
    ) -> TrustedActivity:
        """
        Create a trusted activity for account name.

        **Parameters:**

        * **account_name**: `str` (required) - The account name of the trusted activity.
        * **description**: `str` A description of the trusted activity.
        * **dropbox**: `bool` - Whether to trust Dropbox as a cloud sync service.  Defaults to False.
        * **one_drive** `bool` - Whether to trust OneDrive as a cloud sync service.  Defaults to False.

        At least 1 activity action group (dropbox, one_drive) is required to be trusted.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        providers = []

        if dropbox:
            providers.append(ProviderObject(name=Name.DROPBOX))

        if one_drive:
            providers.append(ProviderObject(name=Name.ONE_DRIVE))

        # At least 1 activity action group is required
        if len(providers) < 1:
            raise ValueError(
                "At least 1 cloud sync service (dropbox, one_drive) must be trusted."
            )
        assert len(providers) != 0

        activity_action_group = ActivityActionGroup(
            activityActions=[
                ActivityAction(providers=providers, type=ActivityType.CLOUD_SYNC)
            ],
            name=Name.DEFAULT,
        )

        data = CreateTrustedActivityRequest(
            type=ActivityType.ACCOUNT_NAME,
            value=account_name,
            description=description,
            activityActionGroups=[activity_action_group],
        )

        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def create_trusted_activity_for_git_repository_uri(
        self,
        git_uri: str,
        description: str = None,
    ) -> TrustedActivity:
        """
        Create a trusted activity.

        **Parameters:**

        * **git_uri**: `str` - (required) The Git URI of the trusted activity.
        * **description**: `str` - A description of the trusted activity.

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object representing
        the newly created trusted activity.
        """

        activity_action_group = ActivityActionGroup(
            activityActions=[ActivityAction(providers=[], type=ActivityType.GIT_PUSH)],
            name=Name.DEFAULT,
        )

        data = CreateTrustedActivityRequest(
            type=ActivityType.GIT_REPOSITORY_URI,
            value=git_uri,
            description=description,
            activityActionGroups=[activity_action_group],
        )

        response = self._parent.session.post(
            url="/v2/trusted-activities", json=data.dict()
        )
        return TrustedActivity.parse_response(response)

    def delete(self, activity_id: int) -> Response:
        """
        Delete a trusted activity.

        **Parameters**:

        * **activity_id** `int` (required) - Unique ID for the trusted activity.

        Usage example:

            >>> client.trusted_activities.v2.delete(23)
            <Response [200]>

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.delete(f"/v2/trusted-activities/{activity_id}")

    def update(self, trusted_activity: TrustedActivity) -> TrustedActivity:
        """
        Updates a trusted activity.
        Valid updatable fields: description, value, activity_type, activity_action_group

        **Parameters**

        * **activity_id** `int` (required) - Unique numeric identifier for the trusted activity.
        * **trusted_activity**: [`TrustedActivity`][trustedactivity-model] (required) - The modified trusted activity object.

        Usage example:

            >>> activity = client.trusted_activities.get_trusted_activity(2)
            >>> activity.description = "New description"
            >>> client.trusted_activities.v2.update(2, activity)

        **Returns**: A [`TrustedActivity`][trustedactivity-model] object with updated values from server.
        """

        data = UpdateTrustedActivity(**trusted_activity.dict())
        response = self._parent.session.patch(
            f"/v2/trusted-activities/{trusted_activity.activity_id}",
            json=data.dict(by_alias=True),
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
