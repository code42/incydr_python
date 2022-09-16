from typing import List

from incydr._queries.alerts import AlertQuery
from incydr._queries.alerts import Query
from .models.request import AddNoteRequest
from .models.request import AlertDetailsRequest
from .models.request import UpdateAlertStateRequest
from .models.response import AlertDetailsResponse
from .models.response import AlertQueryResponse
from incydr.enums.alerts import AlertState


class AlertsV1:
    def __init__(self, parent):
        self._parent = parent

    def search(self, query: AlertQuery):
        """
        Search for alerts.

        **Parameters**:

        * **query**: `AlertQuery | str` (required) - The query object to filter file events by
        different fields.

        **Returns**: A [`FileEventsPage`][fileeventspage-model] object.
        """
        if isinstance(query, str):
            query = Query.parse_raw(query)
            query.tenantId = self._parent.tenant_id
        if isinstance(query, AlertQuery):
            query._query.tenantId = self._parent.tenant_id
        response = self._parent.session.post(
            "/v1/alerts/query-alerts", json=query.dict()
        )
        return AlertQueryResponse.parse_response(response)

    def get_details(self, alert_ids: List[str]):
        data = AlertDetailsRequest(alertIds=alert_ids)
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

    def change_state(self, alert_ids: List[str], state: AlertState, note: str = None):
        if isinstance(alert_ids, str):
            alert_ids = [alert_ids]
        data = UpdateAlertStateRequest(
            tenant_id=self._parent.tenant_id,
            alert_ids=alert_ids,
            state=state,
            note=note,
        )
        return self._parent.session.post(
            "/v1/alerts/update-state", json=data.dict(by_alias=True)
        )


class AlertsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = AlertsV1(self._parent)
        return self._v1
