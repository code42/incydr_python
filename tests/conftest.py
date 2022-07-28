import pytest
from pytest_httpserver import HTTPServer

TEST_SERVER_ADDRESS = "127.0.0.1:8042"
TEST_HOST = f"http://{TEST_SERVER_ADDRESS}"


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return TEST_SERVER_ADDRESS.split(":")


@pytest.fixture
def httpserver_auth(httpserver: HTTPServer, monkeypatch):
    """Sets up environment variables and auth response from server."""
    monkeypatch.setenv("incydr_api_client_id", "env_id")
    monkeypatch.setenv("incydr_api_client_secret", "env_secret")
    monkeypatch.setenv("incydr_url", TEST_HOST)

    auth_response = dict(token_type="bearer", expires_in=900, access_token="test_token")
    httpserver.expect_request("/v1/oauth", method="POST").respond_with_json(
        auth_response
    )
    return httpserver
