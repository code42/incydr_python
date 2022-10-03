from datetime import datetime
from pathlib import Path
from typing import List

from incydr._audit_log.models import AuditEventsCount
from incydr._audit_log.models import AuditEventsExport
from incydr._audit_log.models import AuditEventsPage
from incydr._audit_log.models import DateRange
from incydr._audit_log.models import QueryAuditLogRequest
from incydr._audit_log.models import QueryExportRequest
from incydr._audit_log.models import UserTypes
from incydr._core.util import get_filename_from_content_disposition


class AuditLogV1:
    """
    Client for `/v1/audit` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.audit_log.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_page(
        self,
        page_num: int = 1,
        page_size: int = None,
        actor_ids: List[str] = None,
        actor_ip_addresses: List[str] = None,
        actor_names: List[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        event_types: List[str] = None,
        resource_ids: List[str] = None,
        user_types: List[UserTypes] = None,
    ) -> AuditEventsPage:
        """
        Search audit log entries.

        **Parameters:**

        * **page_num**: `int` - page_num number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **actor_ids**: `List[str]` - Finds events whose actor_id is one of the given ids.
        * **actor_ip_addresses**: `List[str]` - Finds events whose actor_ip_address is one of the given IP addresses.
        * **actor_names**: `List[str]` - Finds events whose actor_name is one of the given names.
        * **start_time**: `datetime`
        * **end_time**: `datetime`
        * **event_types**: `List[str]` - Finds events whose type is one of the given types.
        * **resource_ids**: `List[str]` - Filters searchable events that match resource_id.
        * **user_types**: `List[UserTypes]` - Filters searchable events that match actor type.

        **Returns**: A [`AuditEventsPage`][auditeventspage-model] object representing the search response.
        """

        page_size = page_size or self._parent.settings.page_size

        date_range = DateRange()
        if start_time:
            date_range.startTime = start_time
        if end_time:
            date_range.endTime = end_time

        data = QueryAuditLogRequest(
            actorIds=actor_ids,
            actorIpAddresses=actor_ip_addresses,
            actorNames=actor_names,
            dateRange=date_range,
            eventTypes=event_types,
            pageNum=page_num,
            pageSize=page_size,
            resourceIds=resource_ids,
            userTypes=user_types,
        )

        response = self._parent.session.post(
            "/v1/audit/search-audit-log", json=data.dict()
        )

        return AuditEventsPage.parse_response(response)

    def search_results_export(
        self,
        page_num: int = 1,
        page_size: int = None,
        actor_ids: List[str] = None,
        actor_ip_addresses: List[str] = None,
        actor_names: List[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        event_types: List[str] = None,
        resource_ids: List[str] = None,
        user_types: List[UserTypes] = None,
    ) -> AuditEventsPage:
        """
        Search audit log entries, specifically for large result sets.

        **Parameters:**

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **actor_ids**: `List[str]` - Finds events whose actor_id is one of the given ids.
        * **actor_ip_addresses**: `List[str]` - Finds events whose actor_ip_address is one of the given IP addresses.
        * **actor_names**: `List[str]` - Finds events whose actor_name is one of the given names.
        * **start_time**: `datetime`
        * **end_time**: `datetime`
        * **event_types**: `List[str]` - Finds events whose type is one of the given types.
        * **resource_ids**: `List[str]` - Filters searchable events that match resource_id.
        * **user_types**: `List[UserTypes]` - Filters searchable events that match actor type.

        **Returns**: A [`AuditEventsPage`][auditeventspage-model] object representing the search response.
        """

        page_size = page_size or self._parent.settings.page_size

        date_range = DateRange()
        if start_time:
            date_range.startTime = start_time
        if end_time:
            date_range.endTime = end_time

        data = QueryAuditLogRequest(
            actorIds=actor_ids,
            actorIpAddresses=actor_ip_addresses,
            actorNames=actor_names,
            dateRange=date_range,
            eventTypes=event_types,
            pageNum=page_num,
            pageSize=page_size,
            resourceIds=resource_ids,
            userTypes=user_types,
        )

        response = self._parent.session.post(
            "/v1/audit/search-results-export", json=data.dict()
        )

        return AuditEventsPage.parse_response(response)

    def search_results_count(
        self,
        page_num: int = 1,
        page_size: int = None,
        actor_ids: List[str] = None,
        actor_ip_addresses: List[str] = None,
        actor_names: List[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        event_types: List[str] = None,
        resource_ids: List[str] = None,
        user_types: List[UserTypes] = None,
    ) -> AuditEventsCount:
        """
        Get total result count of search.

        **Parameters:**

        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **actor_ids**: `List[str]` - Finds events whose actor_id is one of the given ids.
        * **actor_ip_addresses**: `List[str]` - Finds events whose actor_ip_address is one of the given IP addresses.
        * **actor_names**: `List[str]` - Finds events whose actor_name is one of the given names.
        * **start_time**: `datetime`
        * **end_time**: `datetime`
        * **event_types**: `List[str]` - Finds events whose type is one of the given types.
        * **resource_ids**: `List[str]` - Filters searchable events that match resource_id.
        * **user_types**: `List[UserTypes]` - Filters searchable events that match actor type.

        **Returns**: A [`AuditEventsCount`][auditeventscount-model] object
        representing the search response.
        """

        page_size = page_size or self._parent.settings.page_size

        date_range = DateRange()
        if start_time:
            date_range.startTime = start_time
        if end_time:
            date_range.endTime = end_time

        data = QueryAuditLogRequest(
            actorIds=actor_ids,
            actorIpAddresses=actor_ip_addresses,
            actorNames=actor_names,
            dateRange=date_range,
            eventTypes=event_types,
            pageNum=page_num,
            pageSize=page_size,
            resourceIds=resource_ids,
            userTypes=user_types,
        )

        response = self._parent.session.post(
            "/v1/audit/search-results-count", json=data.dict()
        )

        return AuditEventsCount.parse_response(response)

    def export_search_results(
        self,
        target_folder: Path,
        actor_ids: List[str] = None,
        actor_ip_addresses: List[str] = None,
        actor_names: List[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        event_types: List[str] = None,
        resource_ids: List[str] = None,
        user_types: List[UserTypes] = None,
    ) -> Path:
        """
        Export search results.

        **Parameters:**

        * **actor_ids**: `List[str]` - Finds events whose actor_id is one of the given ids.
        * **actor_ip_addresses**: `List[str]` - Finds events whose actor_ip_address is one of the given IP addresses.
        * **actor_names**: `List[str]` - Finds events whose actor_name is one of the given names.
        * **start_time**: `datetime`
        * **end_time**: `datetime`
        * **event_types**: `List[str]` - Finds events whose type is one of the given types.
        * **resource_ids**: `List[str]` - Filters searchable events that match resource_id.
        * **user_types**: `List[UserTypes]` - Filters searchable events that match actor type.

        **Returns**: A `pathlib.Path` object representing location of the downloaded csv file.
        """

        date_range = DateRange()
        if start_time:
            date_range.startTime = start_time
        if end_time:
            date_range.endTime = end_time

        data = QueryExportRequest(
            actorIds=actor_ids,
            actorIpAddresses=actor_ip_addresses,
            actorNames=actor_names,
            dateRange=date_range,
            eventTypes=event_types,
            resourceIds=resource_ids,
            userTypes=user_types,
        )

        export_response = self._parent.session.post(
            "/v1/audit/export", json=data.dict()
        )

        download_token = AuditEventsExport.parse_response(export_response)

        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        if not folder.is_dir():
            raise ValueError(
                f"`target_folder` argument must resolve to a folder: {target_folder}"
            )

        download_response = self._parent.session.get(
            "/v1/audit/redeemDownloadToken?downloadToken="
            + download_token.download_token
        )

        filename = get_filename_from_content_disposition(
            download_response, fallback="AuditLog_SearchResults.csv"
        )
        target = folder / filename
        target.write_bytes(download_response.content)

        return target


class AuditLogClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = AuditLogV1(self._parent)
        return self._v1
