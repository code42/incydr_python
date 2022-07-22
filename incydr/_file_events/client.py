from .models import FileEventResponseV1


class FileEventsV1:
    """File Events V1 Client"""

    def __init__(self, session):
        self._session = session

    def search(self, query):
        response = self._session.post(
            "/v1/file-events", data=query, headers={"content-type": "application/json"}
        )

        return FileEventResponseV1.parse_raw(response.text)
