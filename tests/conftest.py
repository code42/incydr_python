import pytest
from pytest_httpserver import HTTPServer

TEST_SERVER_ADDRESS = "127.0.0.1:8042"
TEST_HOST = f"http://{TEST_SERVER_ADDRESS}"

# dummy token with only one claim {"tenantUid": "abcd-1234"}
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRVaWQiOiJhYmNkLTEyMzQifQ.QouLd4K4pEIphqMZNfY1RuchnltWeQvDOuDsUP69Zkc"


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return TEST_SERVER_ADDRESS.split(":")


@pytest.fixture
def httpserver_auth(httpserver: HTTPServer, monkeypatch):
    """Sets up environment variables and auth response from server."""
    monkeypatch.setenv("incydr_api_client_id", "env_id")
    monkeypatch.setenv("incydr_api_client_secret", "env_secret")
    monkeypatch.setenv("incydr_url", TEST_HOST)

    auth_response = dict(
        token_type="bearer",
        expires_in=900,
        access_token=TEST_TOKEN,
    )
    # ordered request will take precedent as first request
    httpserver.expect_ordered_request("/v1/oauth", method="POST").respond_with_json(
        auth_response
    )
    return httpserver
