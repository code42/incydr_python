import json
from datetime import datetime
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.devices.models import Device
from _incydr_sdk.devices.models import DevicesPage
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.devices import SortKeys
from incydr import Client

TEST_DEVICE_ID = "device-1"

TEST_DEVICE_1 = {
    "deviceId": TEST_DEVICE_ID,
    "legacyDeviceId": "41",
    "name": "DESKTOP-H6V9R95",
    "osHostname": "DESKTOP-H6V9R95",
    "status": "Active",
    "active": True,
    "blocked": True,
    "alertState": 0,
    "userId": "user-1",
    "legacyUserId": "legacy-41",
    "orgId": "414141",
    "legacyOrgId": "41",
    "orgGuid": None,
    "externalReferenceInfo": None,
    "notes": None,
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "osVersion": "10.0.19043",
    "osArch": "amd64",
    "address": "192.168.10.128:4247",
    "remoteAddress": "50.237.14.12",
    "timeZone": "America/Chicago",
    "version": "10.3.0",
    "build": 81,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "loginDate": "2022-07-14T16:53:30.717000Z",
    "osName": "win64",
}


TEST_DEVICE_2 = {
    "deviceId": "device-2",
    "legacyDeviceId": "42",
    "name": "DESKTOP-H6V9R95",
    "osHostname": "DESKTOP-H6V9R95",
    "status": "Active",
    "active": True,
    "blocked": True,
    "alertState": 0,
    "userId": "user-2",
    "legacyUserId": "legacy-42",
    "orgId": "424242",
    "legacyOrgId": "42",
    "orgGuid": None,
    "externalReferenceInfo": None,
    "notes": None,
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "osVersion": "10.0.19043",
    "osArch": "amd64",
    "address": "192.168.10.128:4247",
    "remoteAddress": "50.237.14.12",
    "timeZone": "America/Chicago",
    "version": "10.3.0",
    "build": 81,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "loginDate": "2022-07-14T16:53:30.717000Z",
    "osName": "win64",
}

TEST_DEVICE_3 = {
    "deviceId": "device-3",
    "legacyDeviceId": "43",
    "name": "DESKTOP-H6V9R95",
    "osHostname": "DESKTOP-H6V9R95",
    "status": "Active",
    "active": True,
    "blocked": True,
    "alertState": 0,
    "userId": "user-2",
    "legacyUserId": "legacy-43",
    "orgId": "434343",
    "legacyOrgId": "43",
    "orgGuid": None,
    "externalReferenceInfo": None,
    "notes": None,
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "osVersion": "10.0.19043",
    "osArch": "amd64",
    "address": "192.168.10.128:4247",
    "remoteAddress": "50.237.14.12",
    "timeZone": "America/Chicago",
    "version": "10.3.0",
    "build": 81,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "loginDate": "2022-07-14T16:53:30.717000Z",
    "osName": "win64",
}


@pytest.fixture
def mock_get_all_default(httpserver_auth: HTTPServer):
    query = {
        "page": 1,
        "pageSize": 100,
        "sortDirection": "asc",
        "sortKey": "name",
    }

    devices_data = {"devices": [TEST_DEVICE_1, TEST_DEVICE_2], "totalCount": 2}
    httpserver_auth.expect_request(
        "/v1/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)


@pytest.fixture
def mock_get(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/devices/{TEST_DEVICE_ID}", method="GET"
    ).respond_with_json(TEST_DEVICE_1)


def test_get_device_returns_expected_data(mock_get):
    client = Client()
    device = client.devices.v1.get_device("device-1")
    assert isinstance(device, Device)
    assert device.device_id == "device-1"
    assert json.loads(device.json()) == TEST_DEVICE_1
    # test timestamp conversion
    assert device.last_connected == datetime.fromisoformat(
        TEST_DEVICE_1["lastConnected"].replace("Z", "+00:00")
    )
    assert device.login_date == datetime.fromisoformat(
        TEST_DEVICE_1["loginDate"].replace("Z", "+00:00")
    )
    assert device.creation_date == datetime.fromisoformat(
        TEST_DEVICE_1["creationDate"].replace("Z", "+00:00")
    )
    assert device.modification_date == datetime.fromisoformat(
        TEST_DEVICE_1["modificationDate"].replace("Z", "+00:00")
    )


def test_get_page_when_default_query_params_returns_expected_data(mock_get_all_default):
    client = Client()
    page = client.devices.v1.get_page()
    assert isinstance(page, DevicesPage)
    assert json.loads(page.devices[0].json()) == TEST_DEVICE_1
    assert json.loads(page.devices[1].json()) == TEST_DEVICE_2
    assert page.total_count == len(page.devices) == 2


def test_get_page_when_custom_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "active": True,
        "blocked": False,
        "page": 2,
        "pageSize": 10,
        "sortDirection": "desc",
        "sortKey": "lastConnected",
    }

    devices_data = {"devices": [TEST_DEVICE_1, TEST_DEVICE_2], "totalCount": 2}
    httpserver_auth.expect_request(
        uri="/v1/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)

    client = Client()
    page = client.devices.v1.get_page(
        active=True,
        blocked=False,
        page_num=2,
        page_size=10,
        sort_dir=SortDirection.DESC,
        sort_key=SortKeys.LAST_CONNECTED,
    )
    assert isinstance(page, DevicesPage)
    assert json.loads(page.devices[0].json()) == TEST_DEVICE_1
    assert json.loads(page.devices[1].json()) == TEST_DEVICE_2
    assert page.total_count == len(page.devices) == 2


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page": 1,
        "pageSize": 2,
        "sortDirection": "asc",
        "sortKey": "name",
    }
    query_2 = {
        "page": 2,
        "pageSize": 2,
        "sortDirection": "asc",
        "sortKey": "name",
    }

    devices_data_1 = {"devices": [TEST_DEVICE_1, TEST_DEVICE_2], "totalCount": 3}
    devices_data_2 = {"devices": [TEST_DEVICE_3], "totalCount": 3}

    httpserver_auth.expect_ordered_request(
        "/v1/devices", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(devices_data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/devices", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(devices_data_2)

    client = Client()
    iterator = client.devices.v1.iter_all(page_size=2)
    total_devices = 0
    expected_devices = [TEST_DEVICE_1, TEST_DEVICE_2, TEST_DEVICE_3]
    for item in iterator:
        total_devices += 1
        assert isinstance(item, Device)
        assert json.loads(item.json()) == expected_devices.pop(0)
    assert total_devices == 3


# ************************************************ CLI ************************************************


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_all_default
):
    result = runner.invoke(incydr, ["devices", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "active": True,
        "blocked": False,
        "page": 1,
        "pageSize": 100,
        "sortDirection": "asc",
        "sortKey": "name",
    }

    devices_data = {"devices": [TEST_DEVICE_1, TEST_DEVICE_2], "totalCount": 2}
    httpserver_auth.expect_request(
        uri="/v1/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)

    result = runner.invoke(incydr, ["devices", "list", "--active", "--unblocked"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get
):
    result = runner.invoke(incydr, ["devices", "show", TEST_DEVICE_ID])
    httpserver_auth.check()
    assert result.exit_code == 0
