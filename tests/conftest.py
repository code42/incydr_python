import os
from urllib.parse import urlencode

import pytest
from click.testing import CliRunner
from pytest_httpserver import HTTPServer

TEST_SERVER_ADDRESS = "127.0.0.1:8042"
TEST_HOST = f"http://{TEST_SERVER_ADDRESS}"

# dummy token with only one claim {"tenantUid": "abcd-1234"}
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRVaWQiOiJhYmNkLTEyMzQifQ.QouLd4K4pEIphqMZNfY1RuchnltWeQvDOuDsUP69Zkc"

TEST_USER = {
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


@pytest.fixture(autouse=True)
def clean_environment(mocker):
    mocker.patch.dict(os.environ, clear=True)


@pytest.fixture(scope="session")
def runner():
    cli_runner = CliRunner()
    # prevent local .env files from interfering with tests
    with cli_runner.isolated_filesystem():
        yield cli_runner


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


@pytest.fixture
def mock_user_lookup(httpserver_auth):
    query_1 = {
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }

    data_1 = {"users": [TEST_USER], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    httpserver_auth.expect_request("/v1/oauth", method="POST").respond_with_json(
        dict(
            token_type="bearer",
            expires_in=900,
            access_token="abcd-1234",
        )
    )
