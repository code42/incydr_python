import json
from urllib.parse import urlencode

from _incydr_cli.main import incydr
from _incydr_sdk.core.client import Client
from _incydr_sdk.directory_groups.models import DirectoryGroup
from _incydr_sdk.directory_groups.models import DirectoryGroupsPage
from pytest_httpserver import HTTPServer


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {
        "directory_groups": [
            {"groupId": "group-42", "name": "Sales"},
            {"groupId": "group-43", "name": "Research and Development"},
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v1/directory-groups", query_string=urlencode({"page": 1, "page_size": 100})
    ).respond_with_json(data)

    c = Client()
    page = c.directory_groups.v1.get_page()
    assert isinstance(page, DirectoryGroupsPage)
    assert page.directory_groups[0].json() == json.dumps(
        {"groupId": "group-42", "name": "Sales"}
    )
    assert page.directory_groups[1].json() == json.dumps(
        {"groupId": "group-43", "name": "Research and Development"}
    )
    assert page.total_count == len(page.directory_groups) == 2


def test_get_page_when_custom_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {
        "directory_groups": [
            {"groupId": "group-42", "name": "Sales"},
        ],
        "totalCount": 1,
    }

    query = {"page": 1, "page_size": 2, "name": "Sales"}

    httpserver_auth.expect_request(
        "/v1/directory-groups", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    page = c.directory_groups.v1.get_page(page_num=1, page_size=2, name="Sales")
    assert isinstance(page, DirectoryGroupsPage)
    assert page.directory_groups[0].json() == json.dumps(
        {"groupId": "group-42", "name": "Sales"}
    )
    assert page.total_count == len(page.directory_groups) == 1


def test_iter_all_returns_expected_data(httpserver_auth: HTTPServer):
    query_1 = {
        "page": 1,
        "page_size": 2,
    }
    query_2 = {
        "page": 2,
        "page_size": 2,
    }

    data_1 = {
        "directory_groups": [
            {"groupId": "group-42", "name": "Sales"},
            {"groupId": "group-43", "name": "Research and Development"},
        ],
        "totalCount": 2,
    }
    data_2 = {
        "directory_groups": [
            {"groupId": "group-44", "name": "Engineering"},
        ],
        "totalCount": 1,
    }

    httpserver_auth.expect_ordered_request(
        "/v1/directory-groups", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/directory-groups", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(data_2)

    client = Client()
    iterator = client.directory_groups.v1.iter_all(page_size=2)
    total = 0
    expected = [
        {"groupId": "group-42", "name": "Sales"},
        {"groupId": "group-43", "name": "Research and Development"},
        {"groupId": "group-44", "name": "Engineering"},
    ]
    for item in iterator:
        total += 1
        assert isinstance(item, DirectoryGroup)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 3


# ************************************************ CLI ************************************************


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    query_1 = {
        "page": 1,
        "page_size": 100,
    }

    data_1 = {
        "directory_groups": [
            {"groupId": "group-42", "name": "Sales"},
            {"groupId": "group-43", "name": "Marketing"},
            {"groupId": "group-44", "name": "Research and Development"},
        ],
        "totalCount": 2,
    }

    httpserver_auth.expect_ordered_request(
        "/v1/directory-groups", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    result = runner.invoke(incydr, ["directory-groups", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    query_1 = {"page": 1, "page_size": 100, "name": "test"}

    data_1 = {
        "directory_groups": [
            {"groupId": "group-42", "name": "Sales"},
            {"groupId": "group-43", "name": "Research and Development"},
        ],
        "totalCount": 2,
    }

    httpserver_auth.expect_ordered_request(
        "/v1/directory-groups", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    result = runner.invoke(incydr, ["directory-groups", "list", "--name", "test"])
    httpserver_auth.check()
    assert result.exit_code == 0
