from requests import Response

from _incydr_sdk.orgs.models import Org
from _incydr_sdk.orgs.models import OrgsList


class OrgsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = OrgsV1(self._parent)
        return self._v1


class OrgsV1:
    """Client for `/v1/orgs` endpoints.

    Usage example:

        >>> import incydr
        >>>
        >>> client = incydr.Client(**kwargs)
        >>> client.orgs.v1.list_orgs()
    """

    def __init__(self, parent):
        self._parent = parent

    def activate(self, org_guid: str) -> Response:
        """
        Activate an org.

        **Parameters:**

        * **org_guid**: `str` (required) - The unique ID for the org.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(f"/v1/orgs/{org_guid}/activate")

    def list(self, active: bool = None) -> OrgsList:
        """
        List orgs.

        **Parameters:**

        * **active**: `bool` - Return only orgs matching this active state. Defaults to None, which will return both active and inactive orgs.

        **Returns**: An [`OrgsList`][orgslist-model] object.
        """
        return OrgsList.parse_response(
            self._parent.session.get("/v1/orgs", params={"active": active})
        )

    def create(
        self,
        org_name: str,
        org_ext_ref: str = None,
        parent_org_guid: str = None,
        notes: str = None,
    ) -> Org:
        """
        Create an org.

        **Parameters:**

        * **org_name**: `str` (required) - The name of the org to create.
        * **org_ext_ref**: `str` - The external reference of the org to create. Defaults to None.
        * **parent_org_guid**: `str` - The parent ID of the org to create. Defaults to None.
        * **notes**: `str` - The notes of the org to create. Defaults to None.
        pa
        **Returns**: An [`Org`][org-model] object representing the created org.
        """
        # Ensure parent org guid
        if not parent_org_guid:
            orgslist = self.list().orgs
            id_list = list(map(lambda x: x.org_guid, orgslist))
            for org in orgslist:
                if org.parent_org_guid not in id_list:
                    parent_org_guid = org.org_guid
                    break
        payload = {
            "orgName": org_name,
            "orgExtRef": org_ext_ref,
            "parentOrgGuid": parent_org_guid,
            "notes": notes,
        }
        return Org.parse_response(self._parent.session.post("/v1/orgs", json=payload))

    def deactivate(self, org_guid: str) -> Response:
        """
        Deactivate an org.

        **Parameters:**

        * **org_guid**: `str` (required) - The unique ID for the org.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.post(f"/v1/orgs/{org_guid}/deactivate")

    def get_org(self, org_guid: str) -> Org:
        """
        Get a specific organization.

        **Parameters**:

        * **org_guid**: `str` (required) - The unique ID for the org.

        **Returns**: An [`Org`][org-model] object representing the org.
        """
        return Org.parse_response(self._parent.session.get(f"/v1/orgs/{org_guid}"))

    def update(
        self, org_guid: str, org_name: str, org_ext_ref: str = None, notes: str = None
    ) -> Org:
        """
        Update an org.

        **Parameters:**

        * **org_guid**: `str` (required) - The unique ID for the org to update.
        * **org_name**: `str` (required) - The name of the org to update.
        * **org_ext_ref**: `str` - The external reference of the org to update. Defaults to None.
        * **notes**: `str` - The notes of the org to update. Defaults to None.

        **Returns**: An [`Org`][org-model] object representing the created org.
        """
        payload = {"orgName": org_name, "orgExtRef": org_ext_ref, "notes": notes}
        return Org.parse_response(
            self._parent.session.put(f"/v1/orgs/{org_guid}", json=payload)
        )
