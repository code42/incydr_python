import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from incydr import Client

TEST_ORG_NAME = "test org"
TEST_ORG_GUID = "orgguid"
TEST_DATA = {
    "orgGuid": "7ed19049-3266-42ff-a3c9-b79a7f8e2b30",
    "orgName": TEST_ORG_NAME,
    "orgExtRef": None,
    "notes": None,
    "parentOrgGuid": "a10400e3-e7f3-406e-85f4-d6aa59d94828",
    "active": True,
    "creationDate": "2025-06-02T18:11:32.198Z",
    "modificationDate": "2025-06-02T18:11:32.314Z",
    "deactivationDate": None,
    "registrationKey": "USRR-2C8M-CS28-C9WW",
    "userCount": 0,
    "computerCount": 0,
    "orgCount": 0,
}
TEST_CREATE_ORG_PAYLOAD = {
    "orgName": TEST_ORG_NAME,
    "orgExtRef": None,
    "notes": None,
    "parentOrgGuid": TEST_DATA["orgGuid"],
}
TEST_UPDATE_ORG_PAYLOAD = {"orgName": TEST_ORG_NAME, "orgExtRef": None, "notes": None}
TEST_ORG_LIST = {"totalCount": 1, "orgs": [TEST_DATA]}


@pytest.fixture
def mock_get_org(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/orgs/{TEST_ORG_GUID}", method="GET"
    ).respond_with_json(response_json=TEST_DATA, status=200)
    return httpserver_auth


@pytest.fixture
def mock_create_org(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/orgs", method="GET").respond_with_json(
        response_json=TEST_ORG_LIST, status=200
    )
    httpserver_auth.expect_request(
        "/v1/orgs", method="POST", json=TEST_CREATE_ORG_PAYLOAD
    ).respond_with_json(response_json=TEST_DATA, status=200)
    return httpserver_auth


@pytest.fixture
def mock_update_org(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/orgs/{TEST_ORG_GUID}", method="PUT", json=TEST_UPDATE_ORG_PAYLOAD
    ).respond_with_json(response_json=TEST_DATA, status=200)
    return httpserver_auth


@pytest.fixture
def mock_list_orgs(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/orgs", method="GET").respond_with_json(
        response_json=TEST_ORG_LIST, status=200
    )
    return httpserver_auth


@pytest.fixture
def mock_activate_org(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/orgs/{TEST_ORG_GUID}/activate", method="POST"
    ).respond_with_data(response_data="", status=200)
    return httpserver_auth


@pytest.fixture
def mock_deactivate_org(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/orgs/{TEST_ORG_GUID}/deactivate", method="POST"
    ).respond_with_data(response_data="", status=200)
    return httpserver_auth


def test_activate_org_makes_correct_call(mock_activate_org):
    c = Client()
    c.orgs.v1.activate(TEST_ORG_GUID)
    mock_activate_org.check()


def test_deactivate_org_makes_correct_call(mock_deactivate_org):
    c = Client()
    c.orgs.v1.deactivate(TEST_ORG_GUID)
    mock_deactivate_org.check()


def test_create_org_makes_correct_call(mock_create_org):
    c = Client()
    response = c.orgs.v1.create(org_name=TEST_ORG_NAME)
    assert response.org_name == TEST_ORG_NAME
    mock_create_org.check()


def test_update_org_makes_correct_call(mock_update_org):
    c = Client()
    response = c.orgs.v1.update(org_guid=TEST_ORG_GUID, org_name=TEST_ORG_NAME)
    assert response.org_name == TEST_ORG_NAME
    mock_update_org.check()


def test_list_orgs_makes_correct_call(mock_list_orgs):
    c = Client()
    response = c.orgs.v1.list()
    assert len(response.orgs) == 1
    mock_list_orgs.check()


# ************************************************ CLI ************************************************


def test_cli_activate_activates_org(runner, mock_activate_org):
    result = runner.invoke(incydr, ["orgs", "activate", TEST_ORG_GUID])
    assert result.exit_code == 0
    mock_activate_org.check()


def test_cli_list_lists_orgs(runner, mock_list_orgs):
    result = runner.invoke(incydr, ["orgs", "list"])
    assert result.exit_code == 0
    assert TEST_ORG_NAME in result.output
    mock_list_orgs.check()


def test_cli_create_creates_org(runner, mock_create_org):
    result = runner.invoke(incydr, ["orgs", "create", TEST_ORG_NAME])
    assert result.exit_code == 0
    assert TEST_ORG_NAME in result.output
    mock_create_org.check()


def test_cli_deactivate_deactivates_org(runner, mock_deactivate_org):
    result = runner.invoke(incydr, ["orgs", "deactivate", TEST_ORG_GUID])
    assert result.exit_code == 0
    mock_deactivate_org.check()


def test_cli_show_shows_org(runner, mock_get_org):
    result = runner.invoke(incydr, ["orgs", "show", TEST_ORG_GUID])
    assert result.exit_code == 0
    assert TEST_ORG_NAME in result.output
    mock_get_org.check()


def test_cli_update_updates_org(runner, mock_update_org):
    result = runner.invoke(
        incydr, ["orgs", "update", TEST_ORG_GUID, "--name", TEST_ORG_NAME]
    )
    assert result.exit_code == 0
    assert TEST_ORG_NAME in result.output
    mock_update_org.check()
