from itertools import count
from typing import Union

from .models import FileEventResponseV1FileEvents

from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from py42.sdk.queries.fileevents.v1 import *

class FileEventsV1:
    """File Events V1 Client"""

    def __init__(self, session):
        self._session = session

    def search(self, query):
        response = self._session.post("/v1/file-events", data=query, headers={"content-type": "application/json"})

        return FileEventResponseV1FileEvents.parse_raw(response.text)

