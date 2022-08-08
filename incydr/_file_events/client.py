from .models import FileEventResponseV2
from typing import Union

from .._queries._file_events.query import EventQuery
from .models import FileEventResponseV2
from incydr._queries._file_events.models import Query


class FileEventsV2:
    """File Events V2 Client"""

    def __init__(self, session):
        self._session = session
        self._saved_search = session

    def search(self, query):
        response = self._session.post("/v2/file-events", json=query)
        return FileEventResponseV2.parse_raw(response.text)

    def export_csv(self, query):
        # TODO: what does this look like
        response = self._session.post("/v2/file-events/export", json=query)
        return response

    def group_search_results(self, query):
        response = self._session.post("/v2/file-events/grouping", json=query)
        return FileEventResponseV2.parse_raw(response.text)

    def get_all_saved_searches(self):
        response = self._session.get("/v2/file-events/saved-searches")
        return FileEventResponseV2.parse_raw(response.text)

<<<<<<< HEAD
    def get_saved_search_by_id(self, search_id: str):
        response = self._session.get(f"/v2/file-events/saved-searches/{search_id}")
        return FileEventResponseV2.parse_raw(response.text)

    def execute_saved_search(self, search_id: str):
        pass

    def get_saved_search_as_query(self):
        # could this just be an option of the get_by_id?
        pass
=======
    def search(
        self,
        query: Union[Query, EventQuery],
    ):
        if isinstance(query, EventQuery):
            query = query.dict()
        response = self._session.post("/v2/file-events", json=query)
        return FileEventResponseV2.parse_raw(response.text)
>>>>>>> feature/filter-building


class FileEventsClient:
    def __init__(self, session):
        self._session = session
        self._v2 = None

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = FileEventsV2(self._session)
        return self._v2
