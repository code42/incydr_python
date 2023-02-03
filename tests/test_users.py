import json
from datetime import datetime
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.devices.models import DevicesPage
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.devices import SortKeys
from _incydr_sdk.users.client import RoleProcessingError
from _incydr_sdk.users.models import Role
from _incydr_sdk.users.models import UpdateRolesResponse
from _incydr_sdk.users.models import User
from _incydr_sdk.users.models import UserRole
from _incydr_sdk.users.models import UsersPage
from incydr import Client

TEST_USER_ID = "user-1"
TEST_ORG_GUID = "orgGuid-1"

TEST_USER_1 = {
    "legacyUserId": "legacyUserId-1",
    "userId": TEST_USER_ID,
    "username": "username-1",
    "firstName": "firstName-1",
    "lastName": "lastName-1",
    "legacyOrgId": "legacyOrgId-1",
    "orgId": "orgId-1",
    "orgGuid": TEST_ORG_GUID,
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

TEST_USER_ROLE_1 = {
    "roleId": "role-1",
    "roleName": "rolename-1",
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
    "permissionIds": ["permission-1", "permission-2", "permission-3"],
}

TEST_USER_ROLE_2 = {
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
    "newlyAssignedRolesIds": ["newlyAssignedRolesIds-1", "newlyAssignedRolesIds-2"],
    "unassignedRolesIds": ["unassignedRolesIds-1", "unassignedRolesIds-2"],
    "ignoredRolesIds": ["ignoredRolesIds-1", "ignoredRolesIds-2"],
}
TEST_ROLE_ID = "test-role"
TEST_ROLE_1 = {
    "roleId": TEST_ROLE_ID,
    "roleName": "Test Role",
    "creationDate": "2021-04-09T23:13:06.641000Z",
    "modificationDate": "2022-09-08T14:05:05.418000Z",
    "permissions": [
        {"permission": "test.write", "description": "Test write."},
        {"permission": "test.read", "description": "Test read."},
    ],
}
TEST_ROLE_2 = {
    "roleId": "watchlist-manager",
    "roleName": "Watchlist Manager",
    "creationDate": "2020-08-06T18:04:09.696000Z",
    "modificationDate": "2022-01-14T17:30:28.870000Z",
    "permissions": [
        {"permission": "watchlists.write", "description": "Manage watchlists."},
    ],
}


@pytest.fixture
def mock_list_roles(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/users/roles", method="GET").respond_with_json(
        [TEST_ROLE_1, TEST_ROLE_2]
    )


user_input = pytest.mark.parametrize("user", [TEST_USER_ID, "foo@bar.com"])


@pytest.fixture
def mock_get(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/users/{TEST_USER_ID}", method="GET"
    ).respond_with_json(TEST_USER_1)


@pytest.fixture
def mock_get_devices(httpserver_auth: HTTPServer):
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
        f"/v1/users/{TEST_USER_ID}/devices", method="GET", query_string=urlencode(query)
    ).respond_with_json(devices_data)


@pytest.fixture
def mock_get_user_roles(httpserver_auth: HTTPServer):
    roles_data = {
        "roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2],
    }
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json(roles_data)


@pytest.fixture
def mock_deactivate(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/deactivate", method="POST"
    ).respond_with_data()


@pytest.fixture
def mock_activate(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/activate", method="POST"
    ).respond_with_data()


@pytest.fixture
def mock_move(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/move", method="POST", json={"orgGuid": TEST_ORG_GUID}
    ).respond_with_data()


@pytest.fixture
def mock_get_role(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/users/roles/{TEST_ROLE_ID}", method="GET"
    ).respond_with_json(TEST_ROLE_1)


def test_get_user_when_user_id_returns_expected_data(mock_get):
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


def test_get_user_when_username_performs_get_page_lookup_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }
    data_1 = {"users": [TEST_USER_1], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    client = Client()
    client.users.v1.get_user("foo@bar.com")


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


def test_get_devices_when_default_query_params_returns_expected_data(mock_get_devices):
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


def test_get_roles_returns_expected_data(mock_get_user_roles):
    client = Client()
    roles = client.users.v1.list_user_roles(user_id="user-1")
    assert isinstance(roles, list)
    assert isinstance(roles[0], UserRole)
    assert isinstance(roles[1], UserRole)
    assert roles[0].json() == json.dumps(TEST_USER_ROLE_1)
    assert roles[1].json() == json.dumps(TEST_USER_ROLE_2)


@pytest.mark.parametrize(
    "input_roles,expected_roles",
    [
        ("test-role", ["test-role"]),
        (["Test Role", "watchlist-manager"], ["test-role", "watchlist-manager"]),
    ],
)
def test_update_roles_returns_expected_data(
    httpserver_auth: HTTPServer, mock_list_roles, input_roles, expected_roles
):
    httpserver_auth.expect_request(
        "/v1/users/user-1/roles", method="PUT", json={"roleIds": expected_roles}
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    client = Client()
    response = client.users.v1.update_roles(
        user_id="user-1",
        roles=input_roles,
    )
    assert isinstance(response, UpdateRolesResponse)
    assert response.json() == json.dumps(TEST_USER_ROLE_UPDATE)


def test_get_available_roles_returns_expected_data(mock_list_roles):
    client = Client()
    roles = client.users.v1.list_roles()
    assert isinstance(roles, list)
    assert isinstance(roles[0], Role)
    assert isinstance(roles[1], Role)
    assert roles[0].json() == json.dumps(TEST_ROLE_1)
    assert roles[1].json() == json.dumps(TEST_ROLE_2)


@pytest.mark.parametrize("role", ["test-role", "Test Role"])
def test_get_role_returns_expected_data(
    httpserver_auth: HTTPServer, mock_list_roles, role, mock_get_role
):
    client = Client()
    role = client.users.v1.get_role(role)
    assert isinstance(role, Role)
    assert role.json() == json.dumps(TEST_ROLE_1)


add_roles_input = pytest.mark.parametrize(
    "input_roles,expected_roles",
    [
        ("test-role", ["role-1", "role-2", "test-role"]),
        ("Test Role", ["role-1", "role-2", "test-role"]),
        (
            ["test-role", "watchlist-manager"],
            ["role-1", "role-2", "test-role", "watchlist-manager"],
        ),
        (
            ["test-role", "Watchlist Manager"],
            ["role-1", "role-2", "test-role", "watchlist-manager"],
        ),
        (
            ["Test Role", "Watchlist Manager"],
            ["role-1", "role-2", "test-role", "watchlist-manager"],
        ),
    ],
)


@add_roles_input
def test_add_roles_returns_expected_data(
    httpserver_auth: HTTPServer, mock_list_roles, input_roles, expected_roles
):
    # mock roles update
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": expected_roles},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})

    client = Client()
    response = client.users.v1.add_roles(TEST_USER_ID, input_roles)
    assert isinstance(response, UpdateRolesResponse)


def test_add_roles_when_role_not_found_raises_role_not_found_error(
    httpserver_auth, mock_list_roles
):
    # mock get user roles
    test_role = "a nonexistant role"
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})
    client = Client()
    with pytest.raises(RoleProcessingError) as e:
        client.users.v1.add_roles(TEST_USER_ID, test_role)
    assert f"No role matching the following was found: '{test_role}'" in str(e.value)


remove_roles_input = pytest.mark.parametrize(
    "input_roles,expected_roles",
    [
        ("test-role", ["watchlist-manager"]),
        ("Test Role", ["watchlist-manager"]),
        (["test-role", "watchlist-manager"], []),
        (["test-role", "Watchlist Manager"], []),
        (["Test Role", "Watchlist Manager"], []),
    ],
)


@remove_roles_input
def test_remove_roles_returns_expected_data(
    httpserver_auth: HTTPServer, mock_list_roles, input_roles, expected_roles
):
    # mock roles update
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": expected_roles},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_ROLE_1, TEST_ROLE_2]})

    client = Client()
    response = client.users.v1.remove_roles(TEST_USER_ID, input_roles)
    assert isinstance(response, UpdateRolesResponse)


def test_remove_roles_when_user_not_assigned_role_raises_error(
    httpserver_auth: HTTPServer, mock_list_roles
):
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_ROLE_2]})

    client = Client()
    with pytest.raises(RoleProcessingError) as e:
        client.users.v1.remove_roles(TEST_USER_ID, "test-role")
    assert (
        "User is not currently assigned the following role: 'test-role'. Role cannot be removed."
        in str(e.value)
    )


def test_activate_returns_expected_data(mock_activate):
    c = Client()
    assert c.users.v1.activate(TEST_USER_ID).status_code == 200


def test_deactivate_returns_expected_data(mock_deactivate):
    c = Client()
    assert c.users.v1.deactivate(TEST_USER_ID).status_code == 200


def test_move_returns_expected_data(mock_move):
    c = Client()
    assert c.users.v1.move(TEST_USER_ID, TEST_ORG_GUID).status_code == 200


# ************************************************ CLI ************************************************


@pytest.mark.parametrize("format_", ["table", "csv", "json-pretty", "json-lines"])
def test_cli_list_when_no_results_returns_expected_message(
    httpserver_auth, runner, format_
):
    httpserver_auth.expect_ordered_request("/v1/users", method="GET").respond_with_json(
        {"users": [], "totalCount": 0}
    )

    result = runner.invoke(incydr, ["users", "list", "-f", format_])
    httpserver_auth.check()
    assert result.exit_code == 0
    assert "No results found" in result.output


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    query_1 = {
        "page": 1,
        "pageSize": 100,
    }
    httpserver_auth.expect_ordered_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json({"users": [TEST_USER_1, TEST_USER_2], "totalCount": 2})

    result = runner.invoke(incydr, ["users", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "active_opt,blocked_opt,opt_value",
    [("--active", "--blocked", True), ("--inactive", "--unblocked", False)],
)
def test_cli_list_when_all_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, active_opt, blocked_opt, opt_value
):
    query = {
        "active": opt_value,
        "blocked": opt_value,
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }
    httpserver_auth.expect_request(
        uri="/v1/users", method="GET", query_string=urlencode(query)
    ).respond_with_json({"users": [TEST_USER_1], "totalCount": 1})

    result = runner.invoke(
        incydr, ["users", "list", active_opt, blocked_opt, "--username", "foo@bar.com"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_show_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get, user, mock_user_lookup
):
    result = runner.invoke(incydr, ["users", "show", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_list_devices_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_devices, user, mock_user_lookup
):
    result = runner.invoke(incydr, ["users", "list-devices", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_list_roles_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_user_roles, mock_user_lookup, user
):
    result = runner.invoke(incydr, ["users", "list-roles", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_update_roles_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    mock_user_lookup,
    user,
    mock_list_roles,
):
    httpserver_auth.expect_request(
        "/v1/users/user-1/roles",
        method="PUT",
        json={"roleIds": ["test-role", "watchlist-manager"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    result = runner.invoke(
        incydr, ["users", "update-roles", user, "test-role,Watchlist Manager"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
@add_roles_input
def test_cli_add_roles_makes_expected_call(
    httpserver_auth,
    runner,
    user,
    mock_user_lookup,
    mock_list_roles,
    input_roles,
    expected_roles,
):
    # mock roles update
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": expected_roles},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})

    if not isinstance(input_roles, str):
        input_roles = ",".join(input_roles)

    result = runner.invoke(
        incydr, ["users", "update-roles", user, input_roles, "--add"]
    )

    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_update_roles_when_role_not_found_raises_role_not_found_error(
    httpserver_auth,
    runner,
    mock_list_roles,
):
    test_role = "a nonexistant role"

    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})

    result = runner.invoke(
        incydr, ["users", "update-roles", TEST_USER_ID, test_role, "--add"]
    )
    assert result.exit_code == 1
    assert (
        "Role Not Found Error: No role matching the following was found: 'a nonexistant role', or you do not have permission to assign this role."
        in result.output
    )


def test_cli_remove_roles_when_user_not_assigned_role_raises_user_not_assigned_role_error(
    httpserver_auth, runner, mock_list_roles
):
    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_ROLE_2]})

    result = runner.invoke(
        incydr, ["users", "update-roles", TEST_USER_ID, TEST_ROLE_ID, "--remove"]
    )
    assert result.exit_code == 1
    assert (
        "User Not Assigned Role Error: User is not currently assigned the following role: 'test-role'. Role cannot be removed."
        in result.output
    )


@user_input
@remove_roles_input
def test_cli_remove_roles_makes_expected_call(
    httpserver_auth,
    runner,
    user,
    mock_user_lookup,
    input_roles,
    expected_roles,
    mock_list_roles,
):
    # mock roles update
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": expected_roles},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    # mock get user roles
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles", method="GET"
    ).respond_with_json({"roles": [TEST_ROLE_1, TEST_ROLE_2]})

    if not isinstance(input_roles, str):
        input_roles = ",".join(input_roles)

    result = runner.invoke(
        incydr, ["users", "update-roles", user, input_roles, "--remove"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_activate_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_activate, mock_user_lookup, user
):
    result = runner.invoke(incydr, ["users", "activate", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_deactivate_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_deactivate, mock_user_lookup, user
):
    result = runner.invoke(incydr, ["users", "deactivate", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_move_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_move, mock_user_lookup, user
):
    result = runner.invoke(incydr, ["users", "move", user, TEST_ORG_GUID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_update_roles_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    tmp_path,
    mock_user_lookup,
    mock_list_roles,
):
    httpserver_auth.expect_request(
        "/v1/users/test-1/roles",
        method="PUT",
        json={"roleIds": ["test-role", "watchlist-manager"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": ["test-role"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        "/v1/users/test-2/roles",
        method="PUT",
        json={"roleIds": ["watchlist-manager", "test-role"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    p = tmp_path / "users.csv"
    p.write_text(
        "user,role\ntest-1,test-role\ntest-1,watchlist-manager\nfoo@bar.com,Test Role\ntest-2,Watchlist Manager\ntest-2,test-role"
    )
    result = runner.invoke(incydr, ["users", "bulk-update-roles", str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_add_roles_makes_expected_call(
    httpserver_auth,
    runner,
    tmp_path,
    mock_user_lookup,
    mock_list_roles,
):
    # mock get user roles
    httpserver_auth.expect_request(
        "/v1/users/test-1/roles", method="GET"
    ).respond_with_json({"roles": []})
    httpserver_auth.expect_request(
        "/v1/users/user-1/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1]})
    httpserver_auth.expect_request(
        "/v1/users/test-2/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})

    httpserver_auth.expect_request(
        "/v1/users/test-1/roles",
        method="PUT",
        json={"roleIds": ["test-role", "watchlist-manager"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": [TEST_USER_ROLE_1["roleId"], "test-role"]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        "/v1/users/test-2/roles",
        method="PUT",
        json={
            "roleIds": [
                TEST_USER_ROLE_1["roleId"],
                TEST_USER_ROLE_2["roleId"],
                "watchlist-manager",
                "test-role",
            ]
        },
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    p = tmp_path / "users.csv"
    p.write_text(
        "user,role\ntest-1,test-role\ntest-1,watchlist-manager\nfoo@bar.com,Test Role\ntest-2,Watchlist Manager\ntest-2,test-role"
    )
    result = runner.invoke(incydr, ["users", "bulk-update-roles", str(p), "--add"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_remove_roles_makes_expected_call(
    httpserver_auth,
    runner,
    tmp_path,
    mock_user_lookup,
):
    # mock list roles
    httpserver_auth.expect_request("/v1/users/roles", method="GET").respond_with_json(
        [
            {
                "roleId": "role-1",
                "roleName": "rolename-1",
                "creationDate": "2022-07-14T16:49:11.166000Z",
                "modificationDate": "2022-07-14T17:05:44.524000Z",
                "permissions": [
                    {"permission": "test.read", "description": "Test read."},
                ],
            },
            {
                "roleId": "role-2",
                "roleName": "rolename-2",
                "creationDate": "2022-07-14T16:49:11.166000Z",
                "modificationDate": "2022-07-14T17:05:44.524000Z",
                "permissions": [
                    {"permission": "test.write", "description": "Test write."},
                ],
            },
        ]
    )
    # mock get user roles
    httpserver_auth.expect_request(
        "/v1/users/test-1/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})
    httpserver_auth.expect_request(
        "/v1/users/user-1/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1]})
    httpserver_auth.expect_request(
        "/v1/users/test-2/roles", method="GET"
    ).respond_with_json({"roles": [TEST_USER_ROLE_1, TEST_USER_ROLE_2]})

    httpserver_auth.expect_request(
        "/v1/users/test-1/roles",
        method="PUT",
        json={"roleIds": []},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/roles",
        method="PUT",
        json={"roleIds": []},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)
    httpserver_auth.expect_request(
        "/v1/users/test-2/roles",
        method="PUT",
        json={"roleIds": [TEST_USER_ROLE_2["roleId"]]},
    ).respond_with_json(TEST_USER_ROLE_UPDATE)

    p = tmp_path / "users.csv"
    p.write_text(
        "user,role\ntest-1,rolename-1\ntest-1,role-2\nfoo@bar.com,role-1\ntest-2,rolename-1"
    )
    result = runner.invoke(incydr, ["users", "bulk-update-roles", str(p), "--remove"])
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command,uri", [("bulk-activate", "activate"), ("bulk-deactivate", "deactivate")]
)
def test_cli_bulk_activate_and_deactivate_when_csv_makes_expected_call(
    httpserver_auth: HTTPServer, runner, tmp_path, command, uri, mock_user_lookup
):
    httpserver_auth.expect_request(
        f"/v1/users/test-user-id/{uri}", method="POST"
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/{uri}", method="POST"
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/test-user-id-1/{uri}", method="POST"
    ).respond_with_data()

    p = tmp_path / "users.csv"
    p.write_text("user\ntest-user-id\nfoo@bar.com\ntest-user-id-1")
    result = runner.invoke(incydr, ["users", command, str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command,uri", [("bulk-activate", "activate"), ("bulk-deactivate", "deactivate")]
)
def test_cli_bulk_activate_and_deactivate_when_json_makes_expected_call(
    httpserver_auth: HTTPServer, runner, tmp_path, command, uri, mock_user_lookup
):
    httpserver_auth.expect_request(
        f"/v1/users/test-user-id/{uri}", method="POST"
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/{uri}", method="POST"
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/test-user-id-1/{uri}", method="POST"
    ).respond_with_data()

    p = tmp_path / "users.csv"
    p.write_text(
        '{"userId": "test-user-id"}\n{"username": "foo@bar.com"}\n{"userId": "test-user-id-1"}'
    )
    result = runner.invoke(incydr, ["users", command, str(p), "-f", "json-lines"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_move_when_csv_makes_expected_call(
    httpserver_auth: HTTPServer, runner, tmp_path, mock_user_lookup
):
    httpserver_auth.expect_request(
        "/v1/users/test-user-id/move", method="POST", json={"orgGuid": "42"}
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/move", method="POST", json={"orgGuid": TEST_ORG_GUID}
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/users/test-user-id-1/move", method="POST", json={"orgGuid": "44"}
    ).respond_with_data()

    p = tmp_path / "users.csv"
    p.write_text(
        f"user,org_guid\ntest-user-id,42\nfoo@bar.com,{TEST_ORG_GUID}\ntest-user-id-1,44"
    )
    result = runner.invoke(incydr, ["users", "bulk-move", str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_move_when_json_makes_expected_call(
    httpserver_auth: HTTPServer, runner, tmp_path, mock_user_lookup
):
    httpserver_auth.expect_request(
        "/v1/users/test-user-id/move", method="POST", json={"orgGuid": "42"}
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/users/{TEST_USER_ID}/move", method="POST", json={"orgGuid": TEST_ORG_GUID}
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/users/test-user-id-1/move", method="POST", json={"orgGuid": "44"}
    ).respond_with_data()

    p = tmp_path / "users.csv"
    p.write_text(
        '{"userId": "test-user-id", "org_guid": "42"}\n{"username": "foo@bar.com", "org_guid": "orgGuid-1"}\n{"userId": "test-user-id-1", "org_guid": "44"}'
    )
    result = runner.invoke(
        incydr, ["users", "bulk-move", str(p), "--format", "json-lines"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize("role", ["test-role", "Test Role"])
def test_cli_roles_show_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_role, role, mock_list_roles
):
    result = runner.invoke(incydr, ["users", "roles", "show", role])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_roles_list_makes_expected_call(httpserver_auth, runner, mock_list_roles):
    result = runner.invoke(incydr, ["users", "roles", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0
