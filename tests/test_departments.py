from urllib.parse import urlencode

from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._departments.models import DepartmentsPage


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"departments": ["Engineering", "Marketing"], "totalCount": 2}
    httpserver_auth.expect_request(
        "/v1/departments", query_string=urlencode({"page": 1, "page_size": 100})
    ).respond_with_json(data)

    c = Client()
    page = c.departments.v1.get_page()
    assert isinstance(page, DepartmentsPage)
    assert page.departments[0] == "Engineering"
    assert page.departments[1] == "Marketing"
    assert page.total_count == len(page.departments) == 2


def test_get_page_when_custom_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"departments": ["Marketing"], "totalCount": 1}
    query = {"page": 1, "page_size": 2, "name": "Marketing"}
    httpserver_auth.expect_request(
        "/v1/departments", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    page = c.departments.v1.get_page(page_num=1, page_size=2, name="Marketing")
    assert isinstance(page, DepartmentsPage)
    assert page.departments[0] == "Marketing"
    assert page.total_count == len(page.departments) == 1
