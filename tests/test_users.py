import json
from datetime import datetime
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._devices.models import DevicesPage
from incydr._devices.models import SortKeys
from incydr._users.models import RolesPage
from incydr._users.models import UpdateRolesResponse
from incydr._users.models import User
from incydr._users.models import UsersPage
from incydr.enums import SortDirection

TEST_USER_1 = {
    "legacyUserId": "legacyUserId-1",
    "userId": "user-1",
    "username": "username-1",
    "firstName": "firstName-1",
    "lastName": "lastName-1",
    "legacyOrgId": "legacyOrgId-1",
    "orgId": "orgId-1",
    "orgGuid": "orgGuid-1",
    "orgName": "orgName-1",
    "notes": "notes-1",
    "active": True,
    "blocked": True,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}

TEST_USER_2 = {
    "legacyUserId": "legacyUserId-2",
    "userId": "user-2",
    "username": "username-2",
    "firstName": "firstName-2",
    "lastName": "lastName-2",
    "legacyOrgId": "legacyOrgId-2",
    "orgId": "orgId-2",
    "orgGuid": "orgGuid-2",
    "orgName": "orgName-2",
    "notes": "notes-2",
    "active": True,
    "blocked": True,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}

TEST_USER_3 = {
    "legacyUserId": "legacyUserId-3",
    "userId": "user-3",
    "username": "username-3",
    "firstName": "firstName-3",
    "lastName": "lastName-3",
    "legacyOrgId": "legacyOrgId-3",
    "orgId": "orgId-3",
    "orgGuid": "orgGuid-3",
    "orgName": "orgName-3",
    "notes": "notes-3",
    "active": True,
    "blocked": True,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}

TEST_USER_1_DEVICE_1 = {
    "deviceId": "device-1",
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

TEST_USER_1_DEVICE_2 = {
    "deviceId": "device-2",
    "legacyDeviceId": "42",
    "name": "DESKTOP-H6V9R95",
    "osHostname": "DESKTOP-H6V9R95",
    "status": "Active",
    "active": True,
    "blocked": True,
    "alertState": 0,
    "userId": "user-1",
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

TEST_USER_1_ROLE_1 = {
    "roleId": "role-1",
    "roleName": "rolename-1",
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "permissionIds": ["permission-1", "permission-2", "permission-3"],
}

TEST_USER_1_ROLE_2 = {
    "roleId": "role-2",
    "roleName": "rolename-2",
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "permissionIds": ["permission-1", "permission-2", "permission-3"],
}

TEST_USER_ROLE_UPDATE = {
    "processedReplacementRoleIds": [
        "processedReplacementRoleIds-1",
        "processedReplacementRoleIds-2",
    ],
    "newlyAssignedRoles": ["newlyAssignedRoles-1", "newlyAssignedRoles-2"],
    "unassignedRoles": ["unassignedRoles-1", "unassignedRoles-2"],
    "ignoredRoles": ["ignoredRoles-1", "ignoredRoles-2"],
}


def test_get_user_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri="/v1/users/user-1", method="GET"
    ).respond_with_json(TEST_USER_1)
    client = Client()
    user = client.users.v1.get_user("user-1")
    assert isinstance(user, User)
    assert user.user_id == "user-1"
    assert user.json() == json.dumps(TEST_USER_1)

    # test timestamp conversion
    assert user.creation_date == datetime.fromisoformat(
        TEST_USER_1["creationDate"].replace("Z", "+00:00")
    )
    assert user.modification_date == datetime.fromisoformat(
        TEST_USER_1["modificationDate"].replace("Z", "+00:00")
    )


def test_get_page_when_default_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "page": 1,
        "pageSize": 100,
    }

    users_data = {"users": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    httpserver_auth.expect_request(
        "/v1/users", method="GET", query_string=urlencode(query)
    ).respond_with_json(users_data)

    client = Client()
    page = client.users.v1.get_page()
    assert isinstance(page, UsersPage)
    assert page.users[0].json() == json.dumps(TEST_USER_1)
    assert page.users[1].json() == json.dumps(TEST_USER_2)
    assert page.total_count == len(page.users) == 2


def test_get_page_when_custom_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {"active": True, "blocked": False, "page": 2, "pageSize": 10}

    users_data = {"users": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    httpserver_auth.expect_request(
        uri="/v1/users", method="GET", query_string=urlencode(query)
    ).respond_with_json(users_data)

    client = Client()
    page = client.users.v1.get_page(
        active=True, blocked=False, page_num=2, page_size=10
    )
    assert isinstance(page, UsersPage)
    assert page.users[0].json() == json.dumps(TEST_USER_1)
    assert page.users[1].json() == json.dumps(TEST_USER_2)
    assert page.total_count == len(page.users) == 2


def test_get_page_when_custom_username_query_param_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {"username": "username-1", "page": 1, "pageSize": 100}

    users_data = {"users": [TEST_USER_1], "totalCount": 1}
    httpserver_auth.expect_request(
        uri="/v1/users", method="GET", query_string=urlencode(query)
    ).respond_with_json(users_data)

    client = Client()
    page = client.users.v1.get_page(username="username-1")
    assert isinstance(page, UsersPage)
    assert page.users[0].json() == json.dumps(TEST_USER_1)
    assert page.total_count == len(page.users) == 1


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page": 1,
        "pageSize": 2,
    }
    query_2 = {"page": 2, "pageSize": 2}

    users_data_1 = {"users": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    users_data_2 = {"users": [TEST_USER_3], "totalCount": 1}

    httpserver_auth.expect_ordered_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(users_data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/users", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(users_data_2)

    client = Client()
    iterator = client.users.v1.iter_all(page_size=2)
    total_users = 0
    expected_users = [TEST_USER_1, TEST_USER_2, TEST_USER_3]
    for item in iterator:
        total_users += 1
        assert isinstance(item, User)
        assert item.json() == json.dumps(expected_users.pop(0))
    assert total_users == 3


def test_get_devices_when_default_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "page": 1,
        "pageSize": 100,
        "sortDirection": "asc",
        "sortKey": "name",
    }

    devices_data = {
        "devices": [TEST_USER_1_DEVICE_1, TEST_USER_1_DEVICE_2],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v1/users/user-1/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)

    client = Client()
    page = client.users.v1.get_devices(user_id="user-1")
    assert isinstance(page, DevicesPage)
    assert page.devices[0].json() == json.dumps(TEST_USER_1_DEVICE_1)
    assert page.devices[1].json() == json.dumps(TEST_USER_1_DEVICE_2)
    assert page.total_count == len(page.devices) == 2


def test_get_devices_when_custom_query_params_returns_expected_data(
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

    devices_data = {
        "devices": [TEST_USER_1_DEVICE_1, TEST_USER_1_DEVICE_2],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        uri="/v1/users/user-1/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)

    client = Client()
    page = client.users.v1.get_devices(
        user_id="user-1",
        active=True,
        blocked=False,
        page_num=2,
        page_size=10,
        sort_dir=SortDirection.DESC,
        sort_key=SortKeys.LAST_CONNECTED,
    )
    assert isinstance(page, DevicesPage)
    assert page.devices[0].json() == json.dumps(TEST_USER_1_DEVICE_1)
    assert page.devices[1].json() == json.dumps(TEST_USER_1_DEVICE_2)
    assert page.total_count == len(page.devices) == 2


def test_get_roles_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    roles_data = {
        "roles": [TEST_USER_1_ROLE_1, TEST_USER_1_ROLE_2],
    }
    httpserver_auth.expect_request(
        "/v1/users/user-1/roles", method="GET"
    ).respond_with_json(roles_data)

    client = Client()
    page = client.users.v1.get_roles(user_id="user-1")
    assert isinstance(page, RolesPage)
    assert page.roles[0].json() == json.dumps(TEST_USER_1_ROLE_1)
    assert page.roles[1].json() == json.dumps(TEST_USER_1_ROLE_2)


def test_update_roles_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    roles_data = TEST_USER_ROLE_UPDATE

    httpserver_auth.expect_request(
        "/v1/users/user-1/roles", method="PUT"
    ).respond_with_json(roles_data)

    client = Client()
    response = client.users.v1.update_roles(
        user_id="user-1", role_ids=["newlyAssignedRoles-1", "newlyAssignedRoles-2"]
    )
    assert isinstance(response, UpdateRolesResponse)
    assert response.json() == json.dumps(TEST_USER_ROLE_UPDATE)
