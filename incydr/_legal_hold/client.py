from itertools import count
from typing import Iterator
from typing import List

from pydantic import parse_obj_as

from incydr._legal_hold.models import CreateMatterRequest
from incydr._legal_hold.models import Custodian
from incydr._legal_hold.models import CustodianMembership
from incydr._legal_hold.models import ListMattersRequest
from incydr._legal_hold.models import Matter
from incydr._legal_hold.models import MatterMembership
from incydr._legal_hold.models import Policy
from incydr._legal_hold.models import ReactivateMatterResponse


class LegalHoldClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = LegalHoldV1(self._parent)
        return self._v1


class LegalHoldV1:
    """
    Client for `/v1/legal-hold` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.legal_hold.v1.list_policies()
    """

    def __init__(self, parent):
        self._parent = parent

    def list_policies(self) -> List[Policy]:
        """
        Get a list of policies.

        **Returns**: A list of [`Policy`][policy-model] objects.
        """
        response = self._parent.session.get(url="/v1/legal-hold/policies")
        return parse_obj_as(List[Policy], response.json()["policies"])

    def get_policy(self, policy_id: str) -> Policy:
        """
        Get an individual policy.

        **Parameters**:

        * **policy_id**: `str` (required) - Unique ID of a legal hold policy.

        **Returns**: A [`Policy`][policy-model] object.
        """
        response = self._parent.session.get(url=f"/v1/legal-hold/policies/{policy_id}")
        return Policy.parse_response(response)

    def get_page_matters(
        self,
        user_id: str = None,
        active: bool = None,
        name: str = None,
        page_num: int = 1,
        page_size: int = None,
    ) -> List[Matter]:
        """
        Get a page of matters.

        Filter results by passing appropriate parameters:

        **Parameters**:

        * **user_id**: `str` - Get matters that were created by the user with this unique ID.
        * **active**: `bool | None` - When true, get only active matters. When false, returns only inactive matters.  Defaults to None, returns all matters.
        * **name**: `str` - Get matters whose `name` either equals or partially contains this value.
        * **page_num**: `int` - Page number for results, starting at 1. Defaults to None
        * **page_size**: `int` - Max number of results to return for a page. Defaults to client's `page_size` setting.

        **Returns**: A list of [`Matter`][matter-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        data = ListMattersRequest(
            creatorUserId=user_id,
            active=active,
            name=name,
            page=page_num,
            pageSize=page_size,
        )
        response = self._parent.session.get(
            url="/v1/legal-hold/matters", params=data.dict()
        )
        return parse_obj_as(List[Matter], response.json()["matters"])

    def iter_all_matters(
        self,
        user_id: str = None,
        active: bool = None,
        name: str = None,
        page_size: int = None,
    ) -> Iterator[Matter]:
        """
        Iterate over all legal hold matters.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Matter`][matter-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page_matters(
                user_id=user_id,
                active=active,
                name=name,
                page_num=page_num,
                page_size=page_size,
            )
            yield from page
            if len(page) < page_size:
                break

    def create_matter(
        self, policy_id: str, name: str, description: str = None, notes: str = None
    ) -> Matter:
        """
        Create a matter.

        **Parameters**:

        * **policy_id**: `str` (required) - The unique ID of the policy involved in the matter.
        * **name**: `str` (required) - Name of the matter.
        * **description**: `str` - Optional description.
        * **notes**: `str` - Optional additional notes.

        **Returns**: A [`Matter`][matter-model] object.
        """
        data = CreateMatterRequest(
            policyId=policy_id, name=name, description=description, notes=notes
        )
        response = self._parent.session.post(
            url="/v1/legal-hold/matters", json=data.dict()
        )
        return Matter.parse_response(response)

    def get_matter(self, matter_id: str):
        """
        Get an individual matter.

        **Parameters**:

        * **matter_id**: `str` (required) - Unique ID of a legal hold matter.

        **Returns**: A [`Matter`][matter-model] object.
        """
        response = self._parent.session.get(url=f"/v1/legal-hold/matters/{matter_id}")
        return Matter.parse_response(response)

    def deactivate_matter(self, matter_id: str):
        """
        Deactivate a matter.

        **Parameters**:

        * **matter_id**: `str` (required) - Unique ID of a legal hold matter.

        **Returns**: A `request.Response` indicating success.
        """
        return self._parent.session.post(
            url=f"/v1/legal-hold/matters/{matter_id}/deactivate"
        )

    def reactivate_matter(self, matter_id: str) -> ReactivateMatterResponse:
        """
        Reactivate a matter.

        **Parameters**:

        * **matter_id**: `str` (required) - Unique ID of a legal hold matter.

        **Returns**: A `ReactivateMatterResponse` object that indicates if any memberships were changed as a result of the matter reactivation.
        """
        response = self._parent.session.post(
            url=f"/v1/legal-hold/matters/{matter_id}/reactivate"
        )
        return ReactivateMatterResponse.parse_response(response)

    def get_page_custodians(
        self, matter_id: str, page_num: int = 1, page_size: int = None
    ) -> List[Custodian]:
        """
        Get a list of custodians on a matter.

        **Parameters**:

        * **matter_id**: `str` (required) - Unique ID of a legal hold matter.
        * **page_num**: `int` - Page number for results, starting at 1. Defaults to None
        * **page_size**: `int` - Max number of results to return for a page. Defaults to client's `page_size` setting.

        **Returns**: A list of [`Custodian`][custodian-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        data = {"page": page_num, "pageSize": page_size}
        response = self._parent.session.get(
            url=f"/v1/legal-hold/matters/{matter_id}/custodians", params=data
        )
        return parse_obj_as(List[Custodian], response.json()["custodians"])

    def iter_all_custodians(
        self, matter_id: str, page_size: int = None
    ) -> Iterator[Custodian]:
        """
        Iterate over all legal hold custodians for a legal hold matter.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Custodian`][custodian-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page_custodians(
                matter_id=matter_id, page_num=page_num, page_size=page_size
            )
            yield from page
            if len(page) < page_size:
                break

    def add_user_to_matter(self, matter_id: str, user_id: str) -> MatterMembership:
        """
        Add a user to a matter.

        **Parameters**:

        * **matter_id**: `str` (required) - Unique ID of a legal hold matter.
        * **user_id**: `int` (required) - Unique ID of the user to add to the matter.

        **Returns**: A [`MatterMembership`][mattermembership-model] object.
        """
        data = {"userId": user_id}
        response = self._parent.session.post(
            url=f"/v1/legal-hold/matters/{matter_id}/custodians", json=data
        )
        return MatterMembership.parse_response(response)

    def list_matters_for_user(
        self, user_id: str, page_num: int = 1, page_size: int = None
    ) -> List[CustodianMembership]:
        """
        Get a list of matters for a user.

        **Parameters**:

        * **user_id**: `int` (required) - Unique ID of a user.
        * **page_num**: `int` - Page number for results, starting at 1. Defaults to None
        * **page_size**: `int` - Max number of results to return for a page. Defaults to client's `page_size` setting.

        **Returns**: A list of [`CustodianMembership`][custodianmembership-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        data = {"page": page_num, "pageSize": page_size}
        response = self._parent.session.get(
            f"/v1/legal-hold/custodians/{user_id}", params=data
        )
        return parse_obj_as(List[CustodianMembership], response.json()["matters"])
