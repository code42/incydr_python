from typing import Union

from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .models.response import FileEventsPage
from .models.response import SavedSearch
from .models.response import SavedSearchesPage
from incydr._queries.file_events import EventQuery
from incydr._queries.file_events import Filter
from incydr._queries.file_events import FilterGroup
from incydr._queries.file_events import Query


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

    def search(
        self,
        query: Union[str, Query, EventQuery, SavedSearch],
    ) -> FileEventsPage:
        """
        Search file events.

        **Parameters**:

        * **query**: `EventQuery | SavedSearch | str` (required) - The query object to filter file events by
        different fields.

        **Returns**: A [`FileEventsPage`][fileeventspage-model] object.
        """
        self._mount_retry_adapter()

        if isinstance(query, SavedSearch):
            query = _create_query_from_saved_search(query)

        if isinstance(query, str):
            query = Query.parse_raw(query)

        if isinstance(query, dict):
            query = Query(**query)

        response = self._parent.session.post("/v2/file-events", json=query.dict())
        return FileEventsPage.parse_response(response)

    def list_saved_searches(self) -> SavedSearchesPage:
        """
        Get all saved searches.

        **Returns**: A [`SavedSearchesPage`][savedsearchespage-model] object.
        """
        response = self._parent.session.get("/v2/file-events/saved-searches")
        return SavedSearchesPage.parse_response(response)

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
        page = SavedSearchesPage.parse_response(response)
        return page.searches[0]

    def execute_saved_search(self, search_id: str) -> FileEventsPage:
        """
        Search file events using a saved search. A helper method which behaves the same as retrieving
        a saved search with the `get_saved_search_by_id()` and then passing the returned response object
        to the `search()` method.

        **Parameters**:

        * **search_id**: `str` - The unique ID of the saved search.

        **Returns**: A [`FileEventsPage`][fileeventspage-model] object.
        """
        return self.search(self.get_saved_search(search_id))

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


def _create_query_from_saved_search(saved_search: SavedSearch) -> Query:
    query = Query(groups=[])
    if saved_search.group_clause:
        query.groupClause = saved_search.group_clause
    if saved_search.groups:
        for i in saved_search.groups:
            filters = [
                Filter.construct(value=f.value, operator=f.operator, term=f.term)
                for f in i.filters
            ]
            query.groups.append(
                FilterGroup.construct(filterClause=i.filter_clause, filters=filters)
            )
    if saved_search.srt_dir:
        query.srtDir = saved_search.srt_dir
    if saved_search.srt_key:
        query.srtKey = saved_search.srt_key
    return query


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
