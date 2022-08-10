from itertools import count
from typing import Iterator

from .models import Device
from .models import DevicesPage
from .models import QueryDevicesRequest
from .models import SortKeys
from incydr._core.util import SortDirection


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
    """Client for `/v1/devices` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.devices.v1.get_page()
    """

    default_page_size = 100

    def __init__(self, session):
        self._session = session

    def get_device(self, device_id: str) -> Device:
        """Get a single device.

        **Parameters:**

        * **device_id**: `str` (required) - The unique ID for the device.

        **Returns**: A [`Device`][device-model] object representing the device.

        """
        response = self._session.get(f"/v1/devices/{device_id}")
        return Device.parse_response(response)

    def get_page(
        self,
        active: bool = None,
        blocked: bool = None,
        page_num: int = 1,
        page_size: int = default_page_size,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
    ) -> DevicesPage:
        """
        Get a page of devices.

        Filter results by passing the appropriate parameters:

        **Parameters**:
        * **active**: `bool` -
        * **blocked**: `bool` -
        * **page_num**: `int` -
        * **page_size**: `int` -
        * **sort_dir**: `SortDirection` - 'asc' or 'desc'. The direction in which to sort the response based on the corresponding key. Defaults to 'asc'.
        * **sort_key**: `SortKeys` - One or more values on which the response will be sorted. Defaults to device name.

        **Returns**: A ['DevicesPage'][devicespage-model] object.
        """

        data = QueryDevicesRequest(
            page=page_num,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_dir,
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
        """
        Iterate over all devices.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Device`][device-model] objects.
        """
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
