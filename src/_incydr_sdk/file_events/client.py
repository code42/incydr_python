from typing import List

from pydantic import parse_obj_as
from requests import HTTPError
from requests.adapters import HTTPAdapter

from ..exceptions import IncydrException
from .models.response import FileEventsPage
from .models.response import GroupedFileEventResponse
from .models.response import SavedSearch
from _incydr_sdk.core.utils import IncydrRequestRetryStrategy
from _incydr_sdk.queries.file_events import EventQuery
from _incydr_sdk.queries.file_events import GroupingEventQuery


class InvalidQueryException(IncydrException):
    """Raised when the file events search endpoint returns a 400."""

    def __init__(self, query=None, exception=None):
        self.query = query
        self.message = (
            "400 Response Error: Invalid query. Please double check your query filters are valid. "
            "\nTip: Make sure you're specifying your filter fields in dot notation. "
            "\nFor example, filter by 'file.archiveId' to filter by the archiveId field within the file object.)"
        )
        if "problems" in exception.response.json().keys():
            self.message += f"\nRaw problem data from the response: {exception.response.json()['problems']}"
        self.original_exception = exception
        super().__init__(self.message)


class FileEventsV2:
    """
    Client for `/v2/file-events` endpoints.

    Usage example:

        >>> import incydr
        >>> from incydr import EventQuery
        >>>
        >>> client = incydr.Client(**kwargs)
        >>> query = EventQuery(start_date='P30D').equals('file.category', ['Document', 'SourceCode'])
        >>> client.file_events.v2.search(query)
    """

    def __init__(self, parent):
        self._parent = parent
        self._retry_adapter_mounted = False

    def search(self, query: EventQuery) -> FileEventsPage:
        """
        Search for file events.

        If the search response contains a `next_page_token` value, it will automatically be set on the query object's
        `.page_token` field. So if a query results in more total events than your set page size, you can just make
        another call to `.search()` with the same query object to fetch the next page. To get all events from a query,
        continue calling search with the same `EventQuery` object until the response has an empty `.file_events` field.

        See [File Event Pagination][pagination] for more details.

        **Parameters**:

        * **query**: `EventQuery` (required) - The query object to filter file events by different fields.

        **Returns**: A [`FileEventsPage`][fileeventspage-model] object.
        """
        self._mount_retry_adapter()

        try:
            response = self._parent.session.post("/v2/file-events", json=query.dict())
        except HTTPError as err:
            if err.response.status_code == 400:
                raise InvalidQueryException(query=query, exception=err)
            raise err
        page = FileEventsPage.parse_response(response)
        query.page_token = page.next_pg_token
        return page

    def search_groups(self, query: GroupingEventQuery) -> GroupedFileEventResponse:
        """
        Search for file event counts by a grouping term.

        **Parameters**:

        * **query**: `GroupingEventQuery` (required) - The query object to group file events by a given field.

        **Returns**: A [`GroupedFileEventResponse`][groupedfileeventresponse-model] object."""
        self._mount_retry_adapter()

        try:
            response = self._parent.session.post(
                "/v2/file-events/grouping", json=query.dict()
            )
        except HTTPError as err:
            if err.response.status_code == 400:
                raise InvalidQueryException(query=query, exception=err)
            raise err
        response = GroupedFileEventResponse.parse_response(response)
        return response

    def list_saved_searches(self) -> List[SavedSearch]:
        """
        Get all saved searches.

        **Returns**: A list of [`SavedSearch`][savedsearch-model] objects.
        """
        response = self._parent.session.get("/v2/file-events/saved-searches")
        return parse_obj_as(List[SavedSearch], response.json()["searches"])

    def get_saved_search(self, search_id: str) -> SavedSearch:
        """
        Get a single saved search.

        **Parameters**:

        * **search_id**: `str` - The unique ID of the saved search.

        **Returns**: A [`SavedSearch`][savedsearch-model] object.
        """
        response = self._parent.session.get(
            f"/v2/file-events/saved-searches/{search_id}"
        )

        # the api response contains a page with a single search. Returns that single SavedSearch object.
        # the api will return a 404 if a no saved searches matching the id are found.
        page = parse_obj_as(List[SavedSearch], response.json()["searches"])
        return page[0]

    def _mount_retry_adapter(self):
        """Sets custom Retry strategy for FFS url requests to gracefully handle being rate-limited on FFS queries."""
        if (
            not self._retry_adapter_mounted
            and self._parent.settings.retry_on_rate_limit
        ):
            retry_strategy = IncydrRequestRetryStrategy(
                logger=self._parent.settings.logger,
                total=None,
                status=3,  # retry up to 3 times
                connect=False,
                read=False,
                redirect=False,
                other=False,  # We do not want to retry on non-status causes.
                backoff_factor=5,  # if `retry-after` header isn't present, use 5 second exponential backoff
                allowed_methods=[
                    "GET",
                    "POST",
                ],  # POST isn't a default allowed method due to it usually modifying resources.
                status_forcelist=[
                    429
                ],  # this only handles 429 errors. Does not retry 5xx.
            )
            file_event_adapter = HTTPAdapter(
                pool_connections=200,
                pool_maxsize=4,
                pool_block=True,
                max_retries=retry_strategy,
            )
            self._parent.session.mount(
                f"{self._parent.session.base_url}/v2/file-events", file_event_adapter
            )
            self._retry_adapter_mounted = True


class FileEventsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v2 = None

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = FileEventsV2(self._parent)
        return self._v2
