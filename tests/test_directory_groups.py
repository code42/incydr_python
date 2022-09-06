import json
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer

from incydr._core.client import Client
from incydr._directory_groups.models import DirectoryGroupsPage


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
