from incydr._departments.models import GetPageRequest
from incydr._directory_groups.models import DirectoryGroupsPage


class DirectoryGroupsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = DirectoryGroupsV1(self._parent)
        return self._v1


class DirectoryGroupsV1:
    """
    Client for `/v1/departments` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.directory_groups.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_directory_groups_page(
        self, page_num: int = 1, page_size=None, name=None
    ) -> DirectoryGroupsPage:
        """
        Get a page of directory groups. Retrieves directory group information that has been pushed to Code42 from SCIM or User Directory Sync.
        The resulting group IDs can be used to include directory groups on watchlists.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **user_id**: `str` - Matches directory groups whose name is like the given value.

        **Returns**: A [`DirectoryGroupsPage`] object.
        """

        data = GetPageRequest(
            page=page_num,
            page_size=page_size or self._parent.settings.page_size,
            name=name,
        )
        response = self._parent.session.get("/v1/directory-groups", params=data.dict())
        return DirectoryGroupsPage.parse_response(response)
