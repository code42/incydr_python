from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._cases.models import CasesPage

from .conftest import TEST_HOST


def test_client(httpserver: HTTPServer):
    oauth_data = {"access_token": "bar", "token_type": "test", "expires_in": 100}
    httpserver.expect_request("/v1/oauth").respond_with_json(oauth_data)

    cases_data = {"cases": [], "totalCount": 0}
    httpserver.expect_request("/v1/cases").respond_with_json(cases_data)

    client = Client(url=TEST_HOST, api_client_id="abc", api_client_secret="123")
    client.cases.get_page()
    assert client.session.auth.token_response.access_token.get_secret_value() == "bar"


def test_client2(httpserver_auth: HTTPServer):
    cases_data = {"cases": [], "totalCount": 0}
    httpserver_auth.expect_request("/v1/cases").respond_with_json(cases_data)

    client = Client(url=TEST_HOST, api_client_id="abc", api_client_secret="123")
    cases = client.cases.get_page()
    assert isinstance(cases, CasesPage)
    assert client.session.auth.token_response.access_token.get_secret_value() == "test_token"