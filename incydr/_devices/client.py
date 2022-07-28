from incydr._core.util import SortDirection
from typing import Iterator
from itertools import count
from .models import Device
from .models import DevicesPage
from .models import QueryDevicesRequest
from .models import SortKeys


class DevicesClient:
    def __init__(self, session):
        self._session = session
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = DevicesV1(self._session)
        return self._v1


class DevicesV1:
    """Devices V1 Client"""

    default_page_size = 100

    def __init__(self, session):
        self._session = session

    def get_device(self, device_id: str) -> Device:
        """Get a single device."""
        response = self._session.get(f"/v1/devices/{device_id}")
        return Device(**response.json())

    def get_page(
        self,
        active: bool = None,
        blocked: bool = None,
        page_num: int = 1,
        page_size: int = default_page_size,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
    ) -> DevicesPage:
        """Get a page of devices."""

        data = QueryDevicesRequest(
            pgNum=page_num,
            pgSize=page_size,
            srtKey=sort_key,
            srtDir=sort_dir,
            active=active,
            blocked=blocked,
        )
        response = self._session.get("/v1/devices", params=data.dict())
        return DevicesPage.parse_response(response)

    def iter_all(
        self,
        active: bool = None,
        blocked: bool = None,
        page_size: int = default_page_size,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
    ) -> Iterator[Device]:
        """Iterate over all devices"""
        for page_num in count(1):
            page = self.get_page(
                active=active,
                blocked=blocked,
                page_num=page_num,
                page_size=page_size,
                sort_dir=sort_dir,
                sort_key=sort_key,
            )
            yield from page.devices
            if len(page.devices) < page_size:
                break
