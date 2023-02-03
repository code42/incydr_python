import itertools
from itertools import count
from typing import Iterator
from typing import List
from typing import Union

import requests
from pydantic import parse_obj_as

from .models.alert import AlertSummary
from .models.request import AddNoteRequest
from .models.request import AlertDetailsRequest
from .models.request import UpdateAlertStateRequest
from .models.response import AlertDetails
from .models.response import AlertQueryPage
from _incydr_sdk.enums.alerts import AlertState
from _incydr_sdk.queries.alerts import AlertQuery


class AlertsV1:
    """
    Client for `/v1/alerts` endpoints.

    Usage example:

        >>> import incydr
        >>> from incydr.enums.alerts import AlertState
        >>> client = incydr.Client(**kwargs)
        >>> client.alerts.v1.change_state("<alert_id>", AlertState.RESOLVED)
    """

    def __init__(self, parent):
        self._parent = parent

    def search(self, query: AlertQuery) -> AlertQueryPage:
        """
        Search for alerts.

        **Parameters**:

        * **query**: `AlertQuery` (required) - The query object to filter alerts by different fields.

        **Returns**: An [`AlertQueryPage`][alertquerypage-model] object.
        """
        if not isinstance(query, AlertQuery):
            raise ValueError("query must be an `incydr.AlertQuery` object.")
        query.tenant_id = self._parent.tenant_id
        response = self._parent.session.post(
            "/v1/alerts/query-alerts", json=query.dict()
        )
        return AlertQueryPage.parse_response(response)

    def iter_all(self, query: AlertQuery) -> Iterator[AlertSummary]:
        """
        Retrieve all alerts for a given query, automatically retrieving multiple pages if they exist.

        * **query**: `AlertQuery` (required) - The query object used to filter alerts by different fields.

        **Returns**: A generator yielding individual [`AlertSummary`][alertsummary-model] objects.
        """
        if not isinstance(query, AlertQuery):
            raise ValueError("query must be an `incydr.AlertQuery` object.")
        query.tenant_id = self._parent.tenant_id
        for page_num in count(0):
            query.page_num = page_num
            response = self._parent.session.post(
                "/v1/alerts/query-alerts", json=query.dict()
            )
            page = AlertQueryPage.parse_response(response)
            yield from page.alerts
            if len(page.alerts) < query.page_size:
                break

    def get_details(self, alert_ids: Union[str, List[str]]) -> List[AlertDetails]:
        """
        Get full details for a set of alerts.

        The `query-details` endpoint accepts a maximum of 100 ids per request, if `alert_ids` is > 100, multiple
        requests will be made and results will be combined into a single list.

        **Parameters**:

        * **alert_ids**: `str | List[str]` (required) - Single alertId or list of alertId strings.

        **Returns**: A list of [`AlertDetails`][alertdetails-model] objects.
        """
        if isinstance(alert_ids, str):
            alert_ids = [alert_ids]
        results = []
        ids = iter(alert_ids)
        while True:
            chunk = list(itertools.islice(ids, 100))
            if not chunk:
                break
            else:
                data = AlertDetailsRequest(alertIds=chunk)
            response = self._parent.session.post(
                "/v1/alerts/query-details", json=data.dict(by_alias=True)
            )
            results.extend(parse_obj_as(List[AlertDetails], response.json()["alerts"]))
        return results

    def add_note(self, alert_id: str, note: str) -> requests.Response:
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

    def change_state(
        self, alert_ids: Union[str, List[str]], state: AlertState, note: str = None
    ) -> requests.Response:
        """
        Change the state of a set of alerts (and optionally add note indicating reason for change in the same request).

        **Parameters**:

        * **alert_id**: `str | List[str]` (required) - ID or list of IDs of the alert(s) to update.
        * **state**: [`AlertState`][alert-state] (required) - State to set alert(s) to.
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
