from itertools import count
from typing import Iterator

from requests import Response

from _incydr_sdk.legal_hold.models import AddCustodianResponse
from _incydr_sdk.legal_hold.models import Custodian
from _incydr_sdk.legal_hold.models import CustodianMatter
from _incydr_sdk.legal_hold.models import CustodianMattersPage
from _incydr_sdk.legal_hold.models import CustodiansPage
from _incydr_sdk.legal_hold.models import LegalHoldPolicy
from _incydr_sdk.legal_hold.models import LegalHoldPolicyPage
from _incydr_sdk.legal_hold.models import Matter
from _incydr_sdk.legal_hold.models import MattersPage


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
    """Client for `/v1/orgs` endpoints.

    Usage example:

        >>> import incydr
        >>>
        >>> client = incydr.Client(**kwargs)
        >>> client.legal_hold.v1.get_matter("matter_id")
    """

    def __init__(self, parent):
        self._parent = parent

    def get_memberships_page_for_user(
        self, user_id: str, page_num: int = None, page_size: int = None
    ) -> CustodianMattersPage:
        """Get a page of matter memberships for a given user

        **Parameters:**

        * **user_id**: `str` (required) - The user ID for the user being queried.
        * **page_num**: `int` - The page number to request.
        * **page_size**: `int` - The page size to request

        **Returns**: A [`CustodianMattersPage`][custodianmatterspage-model] object with the page of memberships for that user.
        """
        return CustodianMattersPage.parse_response(
            self._parent.session.get(
                f"/v1/legal-hold/custodians/{user_id}",
                params={"page": page_num, "pageSize": page_size},
            )
        )

    def iter_all_memberships_for_user(
        self, user_id: str, page_size: int = None
    ) -> Iterator[CustodianMatter]:
        """Get all matter memberships for a given user

        **Parameters:**

        * **user_id**: `str` (required) - The user ID for the user being queried.
        * **page_size**: `int` - The page size to request

        **Returns**: A generator object that yields [`CustodianMatter`][custodianmatter-model] objects with the memberships for the given user.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_memberships_page_for_user(
                user_id=user_id, page_num=page_num, page_size=page_size
            )
            yield from page.matters
            if len(page.matters) < page_size:
                break

    def get_custodians_page(
        self, matter_id: str, page_num: int = None, page_size: int = None
    ):
        """Get a page of custodians for a given matter

        **Parameters:**

        * **matter_id**: `str` (required) - The matter ID being queried.
        * **page_num**: `int` - The page number to request.
        * **page_size**: `int` - The page size to request

        **Returns**: A [`CustodiansPage`][custodianspage-model] object with the page of memberships for that matter.
        """
        return CustodiansPage.parse_response(
            self._parent.session.get(
                f"/v1/legal-hold/matters/{matter_id}/custodians",
                params={"page": page_num, "pageSize": page_size},
            )
        )

    def iter_all_custodians(
        self, matter_id: str, page_size: int = None
    ) -> Iterator[Custodian]:
        """Get all custodians for a given matter

        **Parameters:**

        * **matter_id**: `str` (required) - The matter ID being queried.
        * **page_size**: `int` - The page size to request

        **Returns**: A generator object that yields [`Custodian`][custodian-model] objects with the memberships for the given matter.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_custodians_page(
                matter_id=matter_id, page_num=page_num, page_size=page_size
            )
            yield from page.custodians
            if len(page.custodians) < page_size:
                break

    def add_custodian(self, matter_id: str, user_id: str) -> AddCustodianResponse:
        """Add a user to a matter

        **Parameters:**

        * **matter_id**: `str` (required) - The matter ID.
        * **user_id**: `str` (required) - The user ID of the user to add to the matter.

        **Returns**: An [`AddCustodianResponse`][addcustodianresponse-model] object with the membership for the given matter and user.
        """
        return AddCustodianResponse.parse_response(
            self._parent.session.post(
                f"/v1/legal-hold/matters/{matter_id}/custodians",
                json={"userId": user_id},
            )
        )

    def get_matters_page(
        self,
        creator_user_id: str = None,
        active: bool = None,
        name: str = None,
        page_num: int = None,
        page_size: int = None,
    ) -> MattersPage:
        """Get a page of matters

        **Parameters:**

        * **creator_user_id**: `str` - Find legal hold matters that were created by the user with this unique identifier.
        * **active**: `bool` - When true, return only active matters. When false, return inactive legal hold matters. Defaults to returning all matters.
        * **name**: `str` - Find legal hold matters whose 'name' either equals or partially contains this value.
        * **page_num**: `int` - The page number to request.
        * **page_size**: `int` - The page size to request

        **Returns**: A [`MattersPage`][matterspage-model] object with the page of matters.
        """
        return MattersPage.parse_response(
            self._parent.session.get(
                "/v1/legal-hold/matters",
                params={
                    "creatorUserId": creator_user_id,
                    "active": active,
                    "name": name,
                    "page": page_num,
                    "pageSize": page_size,
                },
            )
        )

    def iter_all_matters(
        self,
        creator_user_id: str = None,
        active: bool = None,
        name: str = None,
        page_size: int = None,
    ) -> Iterator[Matter]:
        """Get all matters

        **Parameters:**

        * **creator_user_id**: `str` - Find legal hold matters that were created by the user with this unique identifier.
        * **active**: `bool` - When true, return only active matters. When false, return inactive legal hold matters. Defaults to returning all matters.
        * **name**: `str` - Find legal hold matters whose 'name' either equals or partially contains this value.
        * **page_num**: `int` - The page number to request.
        * **page_size**: `int` - The page size to request

        **Returns**: A generator object that yields [`Matter`][matter-model] objects with the details of each matter.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_matters_page(
                creator_user_id=creator_user_id,
                active=active,
                name=name,
                page_num=page_num,
                page_size=page_size,
            )
            yield from page.matters
            if len(page.matters) < page_size:
                break

    def create_matter(
        self, policy_id: str, name: str, description: str = None, notes: str = None
    ) -> Matter:
        """Create a matter.

        **Parameters:**

        * **policy_id**: `str` (Required) - The policy ID to be used by the created matter.
        * **name**: `str` (Required) - The name of the matter to be created.
        * **description**: `str` - The description of the matter to be created.
        * **notes**: `str` - The notes for the matter to be created.

        **Returns**: A [`Matter`][matter-model] object with details of the created matter.
        """
        return Matter.parse_response(
            self._parent.session.post(
                "/v1/legal-hold/matters",
                json={
                    "policyId": policy_id,
                    "name": name,
                    "description": description,
                    "notes": notes,
                },
            )
        )

    def deactivate_matter(self, matter_id: str) -> Response:
        """
        Deactivate a matter.

        **Parameters:**

        * **matter_id**: `str` (required) - The unique ID for the matter.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(
            f"/v1/legal-hold/matters/{matter_id}/deactivate"
        )

    def remove_custodian(self, matter_id: str, user_id: str) -> Response:
        """
        Remove a custodian from a matter.

        **Parameters:**

        * **matter_id**: `str` (required) - The unique ID for the matter.
        * **user_id**: `str` (required) - The unique ID of the user.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(
            f"/v1/legal-hold/matters/{matter_id}/custodians/remove",
            json={"userId": user_id},
        )

    def get_matter(self, matter_id) -> Matter:
        """Get a matter

        **Parameters:**

        * **matter_id**: `str` (required) - The ID of the matter.

        **Returns**: A [`Matter`][matter-model] object with matter details.
        """
        return Matter.parse_response(
            self._parent.session.get(f"/v1/legal-hold/matters/{matter_id}")
        )

    def reactivate_matter(self, matter_id: str) -> Response:
        """
        Reactivate a matter.

        **Parameters:**

        * **matter_id**: `str` (required) - The unique ID for the matter.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(
            f"/v1/legal-hold/matters/{matter_id}/reactivate"
        )

    def get_policies_page(
        self, page_num: int = None, page_size: int = None
    ) -> LegalHoldPolicyPage:
        """Get a page of policies

        **Parameters:**

        * **page_num**: `int` - The page number to request.
        * **page_size**: `int` - The page size to request

        **Returns**: A [`LegalHoldPolicyPage`][legalholdpolicypage-model] object with the page of policies.
        """
        return LegalHoldPolicyPage.parse_response(
            self._parent.session.get(
                "/v1/legal-hold/policies",
                params={"page": page_num, "pageSize": page_size},
            )
        )

    def iter_all_policies(self, page_size: int = None) -> Iterator[LegalHoldPolicy]:
        """Iterate through all policies

        **Parameters:**

        * **page_size**: `int` - The page size to request

        **Returns**: A generator that yields [`LegalHoldPolicy`][legalholdpolicy-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_policies_page(page_num=page_num, page_size=page_size)
            yield from page.policies
            if len(page.policies) < page_size:
                break

    def create_policy(self, name: str) -> LegalHoldPolicy:
        """Create a legal hold policy.

        **Parameters:**

        * **name**: `str` (Required) - The name of the policy to create.

        **Returns**: A [`LegalHoldPolicy`][legalholdpolicy-model] object with details of the created policy.
        """
        return LegalHoldPolicy.parse_response(
            self._parent.session.post("/v1/legal-hold/policies", json={"name": name})
        )

    def get_policy(self, policy_id: str) -> LegalHoldPolicy:
        """Get details of a legal hold policy.

        **Parameters:**

        * **policy_id**: `str` (Required) - The unique ID of the policy.

        **Returns**: A [`LegalHoldPolicy`][legalholdpolicy-model] object with details of the policy.
        """
        return LegalHoldPolicy.parse_response(
            self._parent.session.get(f"/v1/legal-hold/policies/{policy_id}")
        )
