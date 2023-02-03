from typing import List

from pydantic import parse_obj_as
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .models.response import FileEventsPage
from .models.response import SavedSearch
from _incydr_sdk.queries.file_events import EventQuery


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

        response = self._parent.session.post("/v2/file-events", json=query.dict())
        page = FileEventsPage.parse_response(response)
        query.page_token = page.next_pg_token
        return page

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
        if not self._retry_adapter_mounted:
            retry_strategy = FFSQueryRetryStrategy(
                status=3,  # retry up to 3 times
                backoff_factor=5,  # if `retry-after` header isn't present, use 5 second exponential backoff
                allowed_methods=[
                    "POST"
                ],  # POST isn't a default allowed method due to it usually modifying resources
                status_forcelist=[
                    429
                ],  # this only handles 429 errors, it won't retry on 5xx
            )
            file_event_adapter = HTTPAdapter(
                pool_connections=200,
                pool_maxsize=4,
                pool_block=True,
                max_retries=retry_strategy,
            )
            self._parent.session.mount(self._parent.settings.url, file_event_adapter)
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


class FFSQueryRetryStrategy(Retry):
    """The forensic search service helpfully responds with a 'retry-after' header, telling us how long until the rate
    limiter is reset. We subclass :class:`urllib3.Retry` just to add a bit of logging so the user can tell why the
    request might look like it's hanging.
    """

    # TODO: Handle debug logging

    def get_retry_after(self, response):
        retry_after = super().get_retry_after(response)
        # if retry_after is not None:
        #     debug.logger.info(
        #         f"Forensic search rate limit hit, retrying after: {int(retry_after)} seconds."
        #     )
        return retry_after

    def get_backoff_time(self):
        backoff_time = super().get_backoff_time()
        # debug.logger.info(
        #     f"Forensic search rate limit hit, retrying after: {backoff_time} seconds."
        # )
        return backoff_time
