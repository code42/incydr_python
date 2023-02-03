from itertools import count

from _incydr_sdk.departments.models import DepartmentsPage
from _incydr_sdk.departments.models import GetPageRequest


class DepartmentsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = DepartmentsV1(self._parent)
        return self._v1


class DepartmentsV1:
    """
    Client for `/v1/departments` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.departments.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_page(self, page_num: int = 1, page_size=None, name=None) -> DepartmentsPage:
        """
        Get a page of departments.  Retrieves department information that has been pushed to Code42 from SCIM or User Directory Sync.
        The resulting department names can be used to include departments on watchlists.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page.
        * **user_id**: `str` - Matches departments whose name is like the given value.

        **Returns**: A [`DepartmentsPage`][departmentspage-model] object.
        """
        data = GetPageRequest(
            page=page_num,
            page_size=page_size or self._parent.settings.page_size,
            name=name,
        )
        response = self._parent.session.get("/v1/departments", params=data.dict())
        return DepartmentsPage.parse_response(response)

    def iter_all(self, page_size=None, name=None):
        """
        Iterate over all departments.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual department names (`str`).
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(page_num=page_num, page_size=page_size, name=name)
            yield from page.departments
            if len(page.departments) < page_size:
                break
