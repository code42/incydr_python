from typing import List
from .models import AlertQueryResponse
from .models import DetailsQuery
from .models import AlertDetailsResponse
from .models import AddNoteRequest
from incydr._queries.alerts import AlertQuery


class AlertsV1:
    def __init__(self, parent):
        self._parent = parent

    def search(self, query: AlertQuery):
        query._query.tenantId = self._parent.tenant_id
        response = self._parent.session.post(
            "/v1/alerts/query-alerts", json=query.dict()
        )
        return AlertQueryResponse.parse_response(response)

    def get_details(self, alert_ids: List[str]):
        data = DetailsQuery(alertIds=alert_ids)
        response = self._parent.session.post(
            "/v1/alerts/query-details", json=data.dict(by_alias=True)
        )
        return AlertDetailsResponse.parse_response(response)

    def add_note(self, alert_id: str, note: str):
        data = AddNoteRequest(
            alertId=alert_id,
            note=note,
            tenantId=self._parent.tenant_id,
        )
        return self._parent.session.post(
            "/v1/alerts/add-note", json=data.dict(by_alias=True)
        )

    def change_state(self, alert_id: str, state):
        ...


class AlertsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = AlertsV1(self._parent)
        return self._v1
