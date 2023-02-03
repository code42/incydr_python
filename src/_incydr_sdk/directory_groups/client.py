from itertools import count

from _incydr_sdk.departments.models import GetPageRequest
from _incydr_sdk.directory_groups.models import DirectoryGroupsPage


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

    def get_page(
        self, page_num: int = 1, page_size=None, name=None
    ) -> DirectoryGroupsPage:
        """
        Get a page of directory groups. Retrieves directory group information that has been pushed to Code42 from SCIM or User Directory Sync.
        The resulting group IDs can be used to include directory groups on watchlists.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **name**: `str` - Matches directory groups whose name is like the given value.

        **Returns**: A [`DirectoryGroupsPage`][directorygroupspage-model] object.
        """

        data = GetPageRequest(
            page=page_num,
            page_size=page_size or self._parent.settings.page_size,
            name=name,
        )
        response = self._parent.session.get("/v1/directory-groups", params=data.dict())
        return DirectoryGroupsPage.parse_response(response)

    def iter_all(self, page_size=None, name=None):
        """
        Iterate over all directory groups.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`DirectoryGroup`][directorygroup-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(page_num=page_num, page_size=page_size, name=name)
            yield from page.directory_groups
            if len(page.directory_groups) < page_size:
                break
