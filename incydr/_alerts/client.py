from typing import List

from .models.request import AddNoteRequest
from .models.request import AlertDetailsRequest
from .models.request import UpdateAlertStateRequest
from .models.response import AlertDetailsPage
from .models.response import AlertQueryPage
from incydr._queries.alerts import AlertQuery
from incydr._queries.alerts import Query
from incydr.enums.alerts import AlertState


class AlertsV1:
    def __init__(self, parent):
        self._parent = parent

    def search(self, query: AlertQuery):
        """
        Search for alerts.

        **Parameters**:

        * **query**: `AlertQuery | str` (required) - The query object to filter alerts by
        different fields.

        **Returns**: An [`AlertQueryPage`][alertquerypage-model] object.
        """
        if isinstance(query, str):
            query = Query.parse_raw(query)
            query.tenantId = self._parent.tenant_id
        if isinstance(query, AlertQuery):
            query._query.tenantId = self._parent.tenant_id
        response = self._parent.session.post(
            "/v1/alerts/query-alerts", json=query.dict()
        )
        return AlertQueryPage.parse_response(response)

    def get_details(self, alert_ids: List[str]):
        """
        Get full details for a set of alerts.

        **Parameters**:

        * **alert_ids**: `List[str]` (required) - List of alertId strings.

        **Returns**: A [`AlertDetailsPage`][alertdetailspage-model] object.
        """
        data = AlertDetailsRequest(alertIds=alert_ids)
        response = self._parent.session.post(
            "/v1/alerts/query-details", json=data.dict(by_alias=True)
        )
        return AlertDetailsPage.parse_response(response)

    def add_note(self, alert_id: str, note: str):
        """
        Add a note to an alert.

        **Parameters**:

        * **alert_id**: `List[str]` (required) -

        **Returns**: A `Response` object indicating success.
        """
        data = AddNoteRequest(
            alertId=alert_id,
            note=note,
            tenantId=self._parent.tenant_id,
        )
        return self._parent.session.post(
            "/v1/alerts/add-note", json=data.dict(by_alias=True)
        )

    def change_state(self, alert_ids: List[str], state: AlertState, note: str = None):
        """
        Change the state of an alert (and optionally add note indicating reason for change in the same request).

        **Parameters**:

        * **alert_id**: `List[str]` (required) - ID of the alert to update.
        * **state**: `AlertState` (required) - State to set alert to.
        * **note**: `str` - Optional note text.

        **Returns**: A `Response` object indicating success.
        """
        if isinstance(alert_ids, str):
            alert_ids = [alert_ids]
        data = UpdateAlertStateRequest(
            tenantId=self._parent.tenant_id,
            alertIds=alert_ids,
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
