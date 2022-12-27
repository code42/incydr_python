import datetime
import json
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer
from pytest_lazyfixture import (
    lazy_fixture,
)  # lazy_fixture allows us to pass a fixture as a value in @pytest.mark.parametrize

from incydr._core.client import Client
from incydr._watchlists.models.responses import ExcludedUsersList
from incydr._watchlists.models.responses import IncludedDepartment
from incydr._watchlists.models.responses import IncludedDepartmentsList
from incydr._watchlists.models.responses import IncludedDirectoryGroup
from incydr._watchlists.models.responses import IncludedDirectoryGroupsList
from incydr._watchlists.models.responses import IncludedUsersList
from incydr._watchlists.models.responses import Watchlist
from incydr._watchlists.models.responses import WatchlistMembersList
from incydr._watchlists.models.responses import WatchlistsPage
from incydr._watchlists.models.responses import WatchlistUser
from incydr.cli.main import incydr
from incydr.enums.watchlists import WatchlistType
from incydr.exceptions import WatchlistNotFoundError
from tests.conftest import TEST_TOKEN

TEST_WATCHLIST_ID = "1c7dd799-1aa0-4f3a-bae8-1d3242fc2af6"
TEST_ID = "b799bf9c-8838-480f-85dc-438d74e3ca0d"

TEST_WATCHLIST_1 = {
    "description": None,
    "listType": "DEPARTING_EMPLOYEE",
    "stats": {
        "excludedUsersCount": 4,
        "includedDepartmentsCount": 2,
        "includedDirectoryGroupsCount": 1,
        "includedUsersCount": 42,
    },
    "tenantId": "code-42",
    "title": "departing employee",
    "watchlistId": TEST_WATCHLIST_ID,
}
TEST_WATCHLIST_2 = {
    "description": "custom watchlist",
    "listType": "CUSTOM",
    "stats": {
        "excludedUsersCount": 13,
        "includedDepartmentsCount": 0,
        "includedDirectoryGroupsCount": 10,
        "includedUsersCount": 43,
    },
    "tenantId": "code-42",
    "title": "test",
    "watchlistId": "1-watchlist-43",
}

TEST_WATCHLIST_3 = {
    "description": None,
    "listType": "NEW_EMPLOYEE",
    "stats": {
        "excludedUsersCount": 1,
        "includedDepartmentsCount": 0,
        "includedDirectoryGroupsCount": 1,
        "includedUsersCount": 10,
    },
    "tenantId": "code-42",
    "title": None,
    "watchlistId": "1-watchlist-44",
}

TEST_USER_1 = {
    "addedTime": "2022-07-18T16:39:51.356082Z",
    "userId": TEST_ID,
    "username": "foo@bar.com",
}
TEST_USER_2 = {
    "addedTime": "2022-08-18T16:39:51.356082Z",
    "userId": "user-43",
    "username": "baz@bar.com",
}

TEST_DEPARTMENT_1 = {"addedTime": "2022-07-18T16:39:51.356082Z", "name": "Engineering"}
TEST_DEPARTMENT_2 = {"addedTime": "2022-08-18T16:39:51.356082Z", "name": "Marketing"}

TEST_GROUP_1 = {
    "addedTime": "2022-07-18T16:39:51.356082Z",
    "groupId": TEST_ID,
    "isDeleted": False,
    "name": "Sales",
}
TEST_GROUP_2 = {
    "addedTime": "2022-08-18T16:39:51.356082Z",
    "groupId": "group-43",
    "isDeleted": False,
    "name": "Research and development",
}


valid_ids_param = pytest.mark.parametrize(
    "input,expected",
    [("user-42", ["user-42"]), (["user-42", "user-43"], ["user-42", "user-43"])],
)


@pytest.fixture
def mock_create_custom(httpserver_auth: HTTPServer):
    data = {
        "description": "custom watchlist",
        "title": "test",
        "watchlistType": "CUSTOM",
    }
    httpserver_auth.expect_request(
        "/v1/watchlists", method="POST", json=data
    ).respond_with_json(TEST_WATCHLIST_2)


@pytest.fixture
def mock_create_departing_employee(httpserver_auth: HTTPServer):
    data = {"description": None, "title": None, "watchlistType": "DEPARTING_EMPLOYEE"}
    httpserver_auth.expect_request(
        "/v1/watchlists", method="POST", json=data
    ).respond_with_json(TEST_WATCHLIST_1)


@pytest.fixture
def mock_delete(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}", method="DELETE"
    ).respond_with_data()


@pytest.fixture
def mock_get_all(httpserver_auth: HTTPServer):
    data = {"watchlists": [TEST_WATCHLIST_1, TEST_WATCHLIST_2], "totalCount": 2}

    query = {"page": 1, "pageSize": 100}

    httpserver_auth.expect_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)


@pytest.fixture
def mock_get_all_members(httpserver_auth: HTTPServer):
    data = {"watchlistMembers": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/members"
    ).respond_with_json(data)


@pytest.fixture
def mock_get_all_included_users(httpserver_auth: HTTPServer):
    data = {"includedUsers": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-users"
    ).respond_with_json(data)


@pytest.fixture
def mock_get_all_excluded_users(httpserver_auth: HTTPServer):
    data = {"excludedUsers": [TEST_USER_1, TEST_USER_2], "totalCount": 2}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/excluded-users"
    ).respond_with_json(data)


@pytest.fixture
def mock_get_all_departments(httpserver_auth: HTTPServer):
    data = {
        "includedDepartments": [TEST_DEPARTMENT_1, TEST_DEPARTMENT_2],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-departments"
    ).respond_with_json(data)


@pytest.fixture
def mock_get_all_directory_groups(httpserver_auth: HTTPServer):
    data = {"includedDirectoryGroups": [TEST_GROUP_1, TEST_GROUP_2], "totalCount": 2}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-directory-groups"
    ).respond_with_json(data)


@pytest.fixture
def mock_get_member(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/members/{TEST_ID}", method="GET"
    ).respond_with_json(TEST_USER_1)


@pytest.fixture
def mock_get_included_user(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-users/{TEST_ID}"
    ).respond_with_json(TEST_USER_1)


@pytest.fixture
def mock_get_excluded_user(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/excluded-users/{TEST_ID}"
    ).respond_with_json(TEST_USER_1)


@pytest.fixture
def mock_get_department(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-departments/{TEST_ID}"
    ).respond_with_json(TEST_DEPARTMENT_1)


@pytest.fixture
def mock_get_directory_group(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-directory-groups/{TEST_ID}"
    ).respond_with_json(TEST_GROUP_1)


def test_get_page_when_default_params_returns_expected_data(mock_get_all):
    c = Client()
    page = c.watchlists.v1.get_page()
    assert isinstance(page, WatchlistsPage)
    assert page.watchlists[0].json() == json.dumps(TEST_WATCHLIST_1)
    assert page.watchlists[1].json() == json.dumps(TEST_WATCHLIST_2)
    assert page.total_count == len(page.watchlists) == 2


def test_get_page_when_custom_params_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"watchlists": [TEST_WATCHLIST_1, TEST_WATCHLIST_2], "totalCount": 2}

    query = {"page": 2, "pageSize": 42, "userId": "user-42"}

    httpserver_auth.expect_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    page = c.watchlists.v1.get_page(page_num=2, page_size=42, user_id="user-42")
    assert isinstance(page, WatchlistsPage)
    assert page.watchlists[0].json() == json.dumps(TEST_WATCHLIST_1)
    assert page.watchlists[1].json() == json.dumps(TEST_WATCHLIST_2)
    assert page.total_count == len(page.watchlists) == 2


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page": 1,
        "pageSize": 2,
    }
    query_2 = {
        "page": 2,
        "pageSize": 2,
    }

    data_1 = {"watchlists": [TEST_WATCHLIST_1, TEST_WATCHLIST_2], "totalCount": 2}
    data_2 = {"watchlists": [TEST_WATCHLIST_3], "totalCount": 1}

    httpserver_auth.expect_ordered_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(data_2)

    client = Client()
    iterator = client.watchlists.v1.iter_all(page_size=2)
    total = 0
    expected = [TEST_WATCHLIST_1, TEST_WATCHLIST_2, TEST_WATCHLIST_3]
    for item in iterator:
        total += 1
        assert isinstance(item, Watchlist)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 3


def test_get_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}", method="GET"
    ).respond_with_json(TEST_WATCHLIST_1)

    c = Client()
    watchlist = c.watchlists.v1.get(TEST_WATCHLIST_ID)
    assert isinstance(watchlist, Watchlist)
    assert watchlist.watchlist_id == TEST_WATCHLIST_ID
    assert watchlist.json() == json.dumps(TEST_WATCHLIST_1)


def test_create_when_required_params_returns_expected_data(
    mock_create_departing_employee,
):
    c = Client()
    watchlist = c.watchlists.v1.create(WatchlistType.DEPARTING_EMPLOYEE)
    assert isinstance(watchlist, Watchlist)
    assert watchlist.json() == json.dumps(TEST_WATCHLIST_1)


def test_create_when_all_params_returns_expected_data(mock_create_custom):
    c = Client()
    watchlist = c.watchlists.v1.create(
        "CUSTOM", title="test", description="custom watchlist"
    )
    assert isinstance(watchlist, Watchlist)
    assert watchlist.json() == json.dumps(TEST_WATCHLIST_2)


def test_create_when_custom_and_no_title_raises_error(httpserver_auth: HTTPServer):
    c = Client()
    with pytest.raises(ValueError) as err:
        c.watchlists.v1.create("CUSTOM")
    assert err.value.args[0] == "`title` value is required for custom watchlists."


def test_delete_returns_expected_data(mock_delete):
    c = Client()
    assert c.watchlists.v1.delete(TEST_WATCHLIST_ID).status_code == 200


def test_update_when_all_params_returns_expected_data(httpserver_auth: HTTPServer):
    query = {"paths": ["title", "description"]}
    data = {"description": "updated description", "title": "updated title"}
    watchlist = TEST_WATCHLIST_2.copy()
    watchlist["title"] = "updated title"
    watchlist["description"] = "updated description"
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}",
        method="PATCH",
        query_string=urlencode(query, doseq=True),
        json=data,
    ).respond_with_json(watchlist)

    c = Client()
    response = c.watchlists.v1.update(
        TEST_WATCHLIST_ID, title="updated title", description="updated description"
    )
    assert isinstance(response, Watchlist)
    assert response.json() == json.dumps(watchlist)


def test_update_when_one_param_returns_expected_data(httpserver_auth: HTTPServer):
    query = {"paths": ["title"]}
    data = {"title": "updated title", "description": None}
    watchlist = TEST_WATCHLIST_2.copy()
    watchlist["title"] = "updated title"
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}",
        method="PATCH",
        query_string=urlencode(query, doseq=True),
        json=data,
    ).respond_with_json(watchlist)

    c = Client()
    response = c.watchlists.v1.update(TEST_WATCHLIST_ID, title="updated title")
    assert isinstance(response, Watchlist)
    assert response.json() == json.dumps(watchlist)


def test_get_member_returns_expected_data(mock_get_member):
    c = Client()
    member = c.watchlists.v1.get_member(TEST_WATCHLIST_ID, TEST_ID)
    assert isinstance(member, WatchlistUser)
    assert member.user_id == TEST_ID
    assert member.username == "foo@bar.com"
    assert member.added_time == datetime.datetime.fromisoformat(
        TEST_USER_1["addedTime"].replace("Z", "+00:00")
    )
    assert member.json() == json.dumps(TEST_USER_1)


def test_list_members_returns_expected_data(mock_get_all_members):
    c = Client()
    members = c.watchlists.v1.list_members(TEST_WATCHLIST_ID)
    assert isinstance(members, WatchlistMembersList)
    assert members.watchlist_members[0].json() == json.dumps(TEST_USER_1)
    assert members.watchlist_members[1].json() == json.dumps(TEST_USER_2)
    assert members.total_count == len(members.watchlist_members) == 2


@valid_ids_param
def test_add_included_users_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"userIds": expected, "watchlistId": TEST_WATCHLIST_ID}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-users/add", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.add_included_users(TEST_WATCHLIST_ID, input).status_code == 200
    )


@valid_ids_param
def test_remove_included_users_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"userIds": expected, "watchlistId": TEST_WATCHLIST_ID}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-users/delete", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.remove_included_users(TEST_WATCHLIST_ID, input).status_code
        == 200
    )


def test_get_included_user_returns_expected_data(mock_get_included_user):
    c = Client()
    user = c.watchlists.v1.get_included_user(TEST_WATCHLIST_ID, TEST_ID)
    assert isinstance(user, WatchlistUser)
    assert user.user_id == TEST_ID
    assert user.username == "foo@bar.com"
    assert user.added_time == datetime.datetime.fromisoformat(
        TEST_USER_1["addedTime"].replace("Z", "+00:00")
    )
    assert user.json() == json.dumps(TEST_USER_1)


def test_list_included_users_returns_expected_data(mock_get_all_included_users):
    c = Client()
    users = c.watchlists.v1.list_included_users(TEST_WATCHLIST_ID)
    assert isinstance(users, IncludedUsersList)
    assert users.included_users[0].json() == json.dumps(TEST_USER_1)
    assert users.included_users[1].json() == json.dumps(TEST_USER_2)
    assert users.total_count == len(users.included_users) == 2


@valid_ids_param
def test_add_excluded_users_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"userIds": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/excluded-users/add", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.add_excluded_users(TEST_WATCHLIST_ID, input).status_code == 200
    )


@valid_ids_param
def test_remove_excluded_users_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"userIds": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/excluded-users/delete", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.remove_excluded_users(TEST_WATCHLIST_ID, input).status_code
        == 200
    )


def test_get_excluded_user_returns_expected_data(mock_get_excluded_user):
    c = Client()
    user = c.watchlists.v1.get_excluded_user(TEST_WATCHLIST_ID, TEST_ID)
    assert isinstance(user, WatchlistUser)
    assert user.user_id == TEST_ID
    assert user.username == "foo@bar.com"
    assert user.added_time == datetime.datetime.fromisoformat(
        TEST_USER_1["addedTime"].replace("Z", "+00:00")
    )
    assert user.json() == json.dumps(TEST_USER_1)


def test_list_excluded_users_returns_expected_data(mock_get_all_excluded_users):
    c = Client()
    users = c.watchlists.v1.list_excluded_users(TEST_WATCHLIST_ID)
    assert isinstance(users, ExcludedUsersList)
    assert users.excluded_users[0].json() == json.dumps(TEST_USER_1)
    assert users.excluded_users[1].json() == json.dumps(TEST_USER_2)
    assert users.total_count == len(users.excluded_users) == 2


@valid_ids_param
def test_add_directory_groups_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"groupIds": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-directory-groups/add", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.add_directory_groups(TEST_WATCHLIST_ID, input).status_code
        == 200
    )


@valid_ids_param
def test_remove_directory_groups_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"groupIds": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-directory-groups/add", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.add_directory_groups(TEST_WATCHLIST_ID, input).status_code
        == 200
    )


def test_list_included_directory_groups_returns_expected_data(
    mock_get_all_directory_groups,
):
    c = Client()
    groups = c.watchlists.v1.list_directory_groups(TEST_WATCHLIST_ID)
    assert isinstance(groups, IncludedDirectoryGroupsList)
    assert groups.included_directory_groups[0].json() == json.dumps(TEST_GROUP_1)
    assert groups.included_directory_groups[1].json() == json.dumps(TEST_GROUP_2)
    assert groups.total_count == len(groups.included_directory_groups) == 2


def test_get_directory_group_returns_expected_data(mock_get_directory_group):
    c = Client()
    group = c.watchlists.v1.get_directory_group(TEST_WATCHLIST_ID, TEST_ID)
    assert isinstance(group, IncludedDirectoryGroup)
    assert group.group_id == TEST_ID
    assert group.name == "Sales"
    assert group.added_time == datetime.datetime.fromisoformat(
        TEST_GROUP_1["addedTime"].replace("Z", "+00:00")
    )
    assert group.json() == json.dumps(TEST_GROUP_1)


@valid_ids_param
def test_add_departments_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"departments": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-departments/add", json=data
    ).respond_with_data()
    c = Client()
    assert c.watchlists.v1.add_departments(TEST_WATCHLIST_ID, input).status_code == 200


@valid_ids_param
def test_remove_departments_returns_expected_data(
    httpserver_auth: HTTPServer, input, expected
):
    data = {"departments": expected}
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-departments/delete", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.watchlists.v1.remove_departments(TEST_WATCHLIST_ID, input).status_code == 200
    )


def test_list_included_departments_returns_expected_data(mock_get_all_departments):
    c = Client()
    departments = c.watchlists.v1.list_departments(TEST_WATCHLIST_ID)
    assert isinstance(departments, IncludedDepartmentsList)
    assert departments.included_departments[0].json() == json.dumps(TEST_DEPARTMENT_1)
    assert departments.included_departments[1].json() == json.dumps(TEST_DEPARTMENT_2)
    assert departments.total_count == len(departments.included_departments) == 2


def test_get_department_returns_expected_data(mock_get_department):
    c = Client()
    department = c.watchlists.v1.get_department(TEST_WATCHLIST_ID, TEST_ID)
    assert isinstance(department, IncludedDepartment)
    assert department.name == "Engineering"
    assert department.added_time == datetime.datetime.fromisoformat(
        TEST_DEPARTMENT_1["addedTime"].replace("Z", "+00:00")
    )
    assert department.json() == json.dumps(TEST_DEPARTMENT_1)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("DEPARTING_EMPLOYEE", TEST_WATCHLIST_ID),
        (WatchlistType.DEPARTING_EMPLOYEE, TEST_WATCHLIST_ID),
        ("test", "1-watchlist-43"),
    ],
)
def test_get_id_by_name_returns_id(httpserver_auth: HTTPServer, name, expected):
    data = {"watchlists": [TEST_WATCHLIST_1, TEST_WATCHLIST_2], "totalCount": 2}
    query = {"page": 1, "pageSize": 100}
    httpserver_auth.expect_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    actual = c.watchlists.v1.get_id_by_name(name)
    assert expected == actual


def test_get_id_by_name_when_no_id_raises_error(httpserver_auth: HTTPServer):
    data = {"watchlists": [], "totalCount": 0}
    query = {"page": 1, "pageSize": 100}
    httpserver_auth.expect_request(
        "/v1/watchlists", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    with pytest.raises(WatchlistNotFoundError) as err:
        c.watchlists.v1.get_id_by_name("name")
    assert (
        err.value.args[0] == "No watchlist matching the type or title 'name' was found."
    )


# ************************************************ CLI ************************************************


def test_cli_list_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_all
):
    result = runner.invoke(incydr, ["watchlists", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "watchlist_input,watchlist_expected",
    [
        (TEST_WATCHLIST_ID, TEST_WATCHLIST_ID),
        ("DEPARTING_EMPLOYEE", TEST_WATCHLIST_ID),
    ],
)
def test_cli_show_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    mock_get_all,
    watchlist_input,
    watchlist_expected,
    mock_get_all_included_users,
    mock_get_all_excluded_users,
    mock_get_all_departments,
    mock_get_all_directory_groups,
):
    # mock unordered token request to follow watchlist arg callback
    auth_response = dict(
        token_type="bearer",
        expires_in=900,
        access_token=TEST_TOKEN,
    )
    httpserver_auth.expect_request("/v1/oauth", method="POST").respond_with_json(
        auth_response
    )

    httpserver_auth.expect_request(
        f"/v1/watchlists/{watchlist_expected}", method="GET"
    ).respond_with_json(TEST_WATCHLIST_1)

    result = runner.invoke(incydr, ["watchlists", "show", watchlist_input])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_create_default_watchlist_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_create_departing_employee
):
    result = runner.invoke(incydr, ["watchlists", "create", "DEPARTING_EMPLOYEE"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_create_custom_watchlist_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_create_custom
):
    result = runner.invoke(
        incydr,
        [
            "watchlists",
            "create",
            "CUSTOM",
            "--title",
            "test",
            "--description",
            "custom watchlist",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_delete_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_delete
):
    result = runner.invoke(incydr, ["watchlists", "delete", TEST_WATCHLIST_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_update_makes_expected_call(httpserver_auth: HTTPServer, runner):
    query = {"paths": ["title", "description"]}
    data = {"description": "updated description", "title": "updated title"}
    watchlist = TEST_WATCHLIST_2.copy()
    watchlist["title"] = "updated title"
    watchlist["description"] = "updated description"
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}",
        method="PATCH",
        query_string=urlencode(query, doseq=True),
        json=data,
    ).respond_with_json(watchlist)

    result = runner.invoke(
        incydr,
        [
            "watchlists",
            "update",
            TEST_WATCHLIST_ID,
            "--title",
            "updated title",
            "--description",
            "updated description",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command,mock_server_call",
    [
        ("list-members", lazy_fixture("mock_get_all_members")),
        ("list-included-users", lazy_fixture("mock_get_all_included_users")),
        ("list-excluded-users", lazy_fixture("mock_get_all_excluded_users")),
        ("list-directory-groups", lazy_fixture("mock_get_all_directory_groups")),
        ("list-departments", lazy_fixture("mock_get_all_departments")),
    ],
)
def test_cli_list_members_makes_expected_call(
    httpserver_auth: HTTPServer, runner, command, mock_server_call
):
    result = runner.invoke(incydr, ["watchlists", command, TEST_WATCHLIST_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


USER_IDS = ["user-1", "user-2", "user-3"]
user_params = pytest.mark.parametrize(
    "option, command, path_group, url_path, expected_request",
    [
        (
            "users",
            "add",
            "included-users",
            "add",
            {"userIds": USER_IDS, "watchlistId": TEST_WATCHLIST_ID},
        ),
        (
            "users",
            "remove",
            "included-users",
            "delete",
            {"userIds": USER_IDS, "watchlistId": TEST_WATCHLIST_ID},
        ),
        ("excluded-users", "add", "excluded-users", "add", {"userIds": USER_IDS}),
        ("excluded-users", "remove", "excluded-users", "delete", {"userIds": USER_IDS}),
    ],
)


@user_params
def test_cli_update_users_when_list_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    option,
    command,
    path_group,
    url_path,
    expected_request,
):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/{path_group}/{url_path}",
        method="POST",
        json=expected_request,
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        ["watchlists", command, TEST_WATCHLIST_ID, "--" + option, ",".join(USER_IDS)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@user_params
def test_cli_update_users_when_csv_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    option,
    command,
    url_path,
    path_group,
    expected_request,
    tmp_path,
):
    p = tmp_path / "users.csv"
    p.write_text("user\n" + "\n".join(USER_IDS))

    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/{path_group}/{url_path}",
        method="POST",
        json=expected_request,
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        ["watchlists", command, TEST_WATCHLIST_ID, "--" + option, "@" + str(p)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@user_params
def test_cli_update_users_when_json_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    option,
    command,
    url_path,
    path_group,
    expected_request,
    tmp_path,
):
    p = tmp_path / "users.json"
    p.write_text("\n".join([f'{{ "user": "{u}" }}' for u in USER_IDS]))

    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/{path_group}/{url_path}",
        method="POST",
        json=expected_request,
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "watchlists",
            command,
            TEST_WATCHLIST_ID,
            "--" + option,
            "@" + str(p),
            "--format",
            "json-lines",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


GROUPS = ["scim-group-1", "scim-group-2"]


@pytest.mark.parametrize(
    "option, command, url_path, expected_request",
    [
        ("directory-groups", "add", "add", {"groupIds": GROUPS}),
        ("directory-groups", "remove", "delete", {"groupIds": GROUPS}),
        ("departments", "add", "add", {"departments": GROUPS}),
        ("departments", "remove", "delete", {"departments": GROUPS}),
    ],
)
def test_cli_update_departments_and_directory_groups_makes_expected_call(
    httpserver_auth: HTTPServer,
    runner,
    option,
    command,
    url_path,
    expected_request,
):
    httpserver_auth.expect_request(
        f"/v1/watchlists/{TEST_WATCHLIST_ID}/included-{option}/{url_path}",
        method="POST",
        json=expected_request,
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        ["watchlists", command, TEST_WATCHLIST_ID, "--" + option, ",".join(GROUPS)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0
