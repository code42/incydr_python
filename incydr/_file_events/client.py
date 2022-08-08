from typing import Union

from .._queries._file_events.query import EventQuery
from .models import FileEventResponseV2, GroupingResponseV2, SavedSearchesPage
from .models import SavedSearch
from incydr._queries._file_events.models import Query
from urllib3 import Retry


class FileEventsV2:
    """File Events V2 Client"""

    def __init__(self, session):
        self._session = session
        self._saved_search = session

    def search(
        self,
        query: Union[Query, EventQuery],
    ) -> FileEventResponseV2:
        if isinstance(query, EventQuery):
            query = query.dict()
        response = self._session.post("/v2/file-events", json=query)
        return FileEventResponseV2.parse_response(response)

    def export_csv(self, query: Union[Query, EventQuery]):
        # TODO: what does this look like, do we want this do this
        response = self._session.post("/v2/file-events/export", json=query)
        return response

    def group_search_results(self, query: Union[Query, EventQuery]) -> GroupingResponseV2:
        """
        Search file events, providing a group parameter to bucket results into
        unique values and approximate counts for each value.
        """
        response = self._session.post("/v2/file-events/grouping", json=query)
        return GroupingResponseV2.parse_response(response)

    def get_all_saved_searches(self) -> SavedSearchesPage:
        response = self._session.get("/v2/file-events/saved-searches")
        return SavedSearchesPage.parse_response(response)

    def get_saved_search_by_id(self, search_id: str) -> SavedSearch:
        response = self._session.get(f"/v2/file-events/saved-searches/{search_id}")
        return SavedSearch.parse_response(response)

    def execute_saved_search(self, search_id: str) -> FileEventResponseV2:
        query = _create_query_from_saved_search(self.get_saved_search_by_id(search_id))
        return self.search(query)

    def get_saved_search_as_query(self):
        # could this just be an option of the get_by_id?
        pass


class FileEventsClient:
    def __init__(self, session):
        self._session = session
        self._v2 = None

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = FileEventsV2(self._session)
        return self._v2


def _create_query_from_saved_search(saved_search: SavedSearch) -> Query:
    return Query(
        groupClause=saved_search.group_clause,
        groups=saved_search.groups,
        srtDir=saved_search.srt_dir,
        srtKey=saved_search.srt_key
    )

class FFSQueryRetryStrategy(Retry):
    """The forensic search service helpfully responds with a 'retry-after' header, telling us how long until the rate
    limiter is reset. We subclass :class:`urllib3.Retry` just to add a bit of logging so the user can tell why the
    request might look like it's hanging.
    """

    def get_retry_after(self, response):
        retry_after = super().get_retry_after(response)
        if retry_after is not None:
            debug.logger.info(
                f"Forensic search rate limit hit, retrying after: {int(retry_after)} seconds."
            )
        return retry_after

    def get_backoff_time(self):
        backoff_time = super().get_backoff_time()
        debug.logger.info(
            f"Forensic search rate limit hit, retrying after: {backoff_time} seconds."
        )
        return backoff_time
