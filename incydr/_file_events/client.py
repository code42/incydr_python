from typing import Union

from incydr._queries.file_events import EventQuery, Query
from .models import FileEventResponseV1
from .models import FileEventResponseV2


class FileEventsV1:
    """File Events V1 Client"""

    def __init__(self, session):
        self._session = session

    def search(self, query):
        response = self._session.post("/v1/file-events", json=query)
        return FileEventResponseV1.parse_raw(response.text)


class FileEventsV2:
    """File Events V2 Client"""

    def __init__(self, session):
        self._session = session

    def search(
        self,
        query: Union[str, Query, EventQuery],
    ):
        if isinstance(query, str):
            query = Query.parse_raw(query)
        response = self._session.post("/v2/file-events", json=query.dict())
        return FileEventResponseV2.parse_raw(response.text)


class FileEventsClient:
    def __init__(self, session):
        self._session = session
        self._v1 = None
        self._v2 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = FileEventsV1(self._session)
        return self._v1

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = FileEventsV2(self._session)
        return self._v2
