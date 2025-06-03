import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.legal_hold.models import CustodianMattersPage
from _incydr_sdk.legal_hold.models import CustodiansPage
from _incydr_sdk.legal_hold.models import LegalHoldPolicy
from _incydr_sdk.legal_hold.models import LegalHoldPolicyPage
from _incydr_sdk.legal_hold.models import Matter
from _incydr_sdk.legal_hold.models import MattersPage
from incydr import Client


TEST_MATTER_ID = "matter id"
TEST_USER_ID = "user id"
TEST_POLICY_ID = "policy id"

TEST_MATTER = {
    "matter_id": "1221742823190440525",
    "name": "sdk test matter",
    "description": "",
    "notes": None,
    "active": True,
    "creation_date": "2025-06-03T15:04:29.965+00:00",
    "policy_id": "1221742699257145933",
    "creator": None,
    "creator_principal": {
        "type": "API_KEY",
        "principal_id": "api key",
        "display_name": "cecilia saved",
    },
}

TEST_MATTERS_PAGE = {"matters": [TEST_MATTER]}

TEST_CUSTODIAN_MATTERS_PAGE = {
    "matters": [
        {
            "membershipActive": True,
            "membershipCreationDate": "2025-06-03T15:10:37.713000Z",
            "matterId": "matter one",
            "name": "sdk test matter",
        },
        {
            "membershipActive": True,
            "membershipCreationDate": "2024-10-11T14:29:33.829000Z",
            "matterId": "matter two",
            "name": "sdk test matter 2",
        },
    ]
}

TEST_CUSTODIANS_PAGE = {
    "custodians": [
        {
            "membershipActive": True,
            "membershipCreationDate": "2025-06-03T15:10:37.713000Z",
            "userId": "id one",
            "name": None,
            "email": "email@code42.com",
            "username": "email@code42.com",
        },
        {
            "membershipActive": True,
            "membershipCreationDate": "2025-06-03T15:10:37.713000Z",
            "userId": "id two",
            "name": None,
            "email": "email@code42.com",
            "username": "email@code42.com",
        },
    ]
}

TEST_ADD_CUSTODIAN_RESPONSE = {
    "membershipActive": True,
    "membershipCreationDate": "2025-06-03T15:10:37.713000Z",
    "matter": {"matterId": "1221742823190440525", "name": "sdk test matter"},
    "custodian": {
        "userId": "938960273869958201",
        "username": "cecilia.stevens+test@code42.com",
        "email": "cecilia.stevens+test@code42.com",
    },
}

TEST_POLICY = {
    "policyId": "policy id",
    "name": "sdk test",
    "creationDate": "2025-06-03T15:03:16.093000Z",
    "modificationDate": "2025-06-03T15:03:16.093000Z",
    "creatorUser": None,
    "creatorPrincipal": {
        "type": "API_KEY",
        "principalId": "api key",
        "displayName": "cecilia saved",
    },
}

TEST_POLICIES_PAGE = {"policies": [TEST_POLICY]}


@pytest.fixture
def mock_memberships_page(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/custodians/{TEST_USER_ID}", method="GET"
    ).respond_with_json(response_json=TEST_CUSTODIAN_MATTERS_PAGE, status=200)
    return httpserver_auth


@pytest.fixture
def mock_custodians_page(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians", method="GET"
    ).respond_with_json(response_json=TEST_CUSTODIANS_PAGE, status=200)
    return httpserver_auth


@pytest.fixture
def mock_add_custodian(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians",
        method="POST",
        json={"userId": TEST_USER_ID},
    ).respond_with_json(response_json=TEST_ADD_CUSTODIAN_RESPONSE, status=200)
    return httpserver_auth


@pytest.fixture
def mock_remove_custodian(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians/remove",
        method="POST",
        json={"userId": TEST_USER_ID},
    ).respond_with_data(response_data="", status=200)
    return httpserver_auth


@pytest.fixture
def mock_matters_page(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        "/v1/legal-hold/matters", method="GET"
    ).respond_with_json(response_json=TEST_MATTERS_PAGE, status=200)
    return httpserver_auth


@pytest.fixture
def mock_create_matter(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        "/v1/legal-hold/matters",
        method="POST",
        json={
            "policyId": TEST_MATTER["policy_id"],
            "name": TEST_MATTER["name"],
            "description": None,
            "notes": None,
        },
    ).respond_with_json(response_json=TEST_MATTER, status=200)
    return httpserver_auth


@pytest.fixture
def mock_deactivate_matter(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/deactivate", method="POST"
    ).respond_with_data(response_data="", status=200)
    return httpserver_auth


@pytest.fixture
def mock_reactivate_matter(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/reactivate", method="POST"
    ).respond_with_data(response_data="", status=200)
    return httpserver_auth


@pytest.fixture
def mock_get_matter(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}", method="GET"
    ).respond_with_json(response_json=TEST_MATTER, status=200)
    return httpserver_auth


@pytest.fixture
def mock_policies_page(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        "/v1/legal-hold/policies", method="GET"
    ).respond_with_json(response_json=TEST_POLICIES_PAGE, status=200)
    return httpserver_auth


@pytest.fixture
def mock_get_policy(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/policies/{TEST_POLICY_ID}", method="GET"
    ).respond_with_json(response_json=TEST_POLICY, status=200)
    return httpserver_auth


def test_get_memberships_page_for_user_makes_correct_call(mock_memberships_page):
    c = Client()
    response = c.legal_hold.v1.get_memberships_page_for_user(user_id=TEST_USER_ID)
    assert isinstance(response, CustodianMattersPage)
    mock_memberships_page.check()


def test_iter_all_memberships_for_user_iterates_memberships(mock_memberships_page):
    c = Client()
    response = list(c.legal_hold.v1.iter_all_memberships_for_user(user_id=TEST_USER_ID))
    assert len(response) == 2
    mock_memberships_page.check()


def test_get_custodians_page_makes_correct_call(mock_custodians_page):
    c = Client()
    response = c.legal_hold.v1.get_custodians_page(matter_id=TEST_MATTER_ID)
    assert isinstance(response, CustodiansPage)
    mock_custodians_page.check()


def test_iter_all_custodians_iterates_custodians(mock_custodians_page):
    c = Client()
    response = list(c.legal_hold.v1.iter_all_custodians(matter_id=TEST_MATTER_ID))
    assert len(response) == 2
    mock_custodians_page.check()


def test_add_custodian_adds_custodian(mock_add_custodian):
    c = Client()
    c.legal_hold.v1.add_custodian(matter_id=TEST_MATTER_ID, user_id=TEST_USER_ID)
    mock_add_custodian.check()


def test_get_matters_page_makes_correct_call(mock_matters_page):
    c = Client()
    response = c.legal_hold.v1.get_matters_page()
    assert isinstance(response, MattersPage)
    mock_matters_page.check()


def test_iter_all_matters_iterates_matters(mock_matters_page):
    c = Client()
    response = list(c.legal_hold.v1.iter_all_matters())
    assert len(response) == 1
    mock_matters_page.check()


def test_create_matter_makes_correct_call(mock_create_matter):
    c = Client()
    response = c.legal_hold.v1.create_matter(
        name=TEST_MATTER["name"], policy_id=TEST_MATTER["policy_id"]
    )
    assert isinstance(response, Matter)
    mock_create_matter.check()


def test_deactivate_matter_makes_correct_call(mock_deactivate_matter):
    c = Client()
    c.legal_hold.v1.deactivate_matter(matter_id=TEST_MATTER_ID)
    mock_deactivate_matter.check()


def test_reactivate_matter_makes_correct_call(mock_reactivate_matter):
    c = Client()
    c.legal_hold.v1.reactivate_matter(matter_id=TEST_MATTER_ID)
    mock_reactivate_matter.check()


def test_remove_custodian_makes_correct_call(mock_remove_custodian):
    c = Client()
    c.legal_hold.v1.remove_custodian(matter_id=TEST_MATTER_ID, user_id=TEST_USER_ID)
    mock_remove_custodian.check()


def test_get_matter_makes_correct_call(mock_get_matter):
    c = Client()
    result = c.legal_hold.v1.get_matter(matter_id=TEST_MATTER_ID)
    assert isinstance(result, Matter)
    mock_get_matter.check()


def test_get_policies_page_makes_correct_call(mock_policies_page):
    c = Client()
    result = c.legal_hold.v1.get_policies_page()
    assert isinstance(result, LegalHoldPolicyPage)
    mock_policies_page.check()


def test_iter_all_policies_iterates_policies(mock_policies_page):
    c = Client()
    result = list(c.legal_hold.v1.iter_all_policies())
    assert len(result) == 1
    mock_policies_page.check()


def test_get_policy_makes_correct_call(mock_get_policy):
    c = Client()
    result = c.legal_hold.v1.get_policy(policy_id=TEST_POLICY_ID)
    assert isinstance(result, LegalHoldPolicy)
    mock_get_policy.check()


# ************************************************ CLI ************************************************


def test_cli_list_matters_for_user_lists_memberships(runner, mock_memberships_page):
    result = runner.invoke(
        incydr, ["legal-hold", "list-matters-for-user", TEST_USER_ID]
    )
    assert "sdk test matter" in result.output
    assert "sdk test matter 2" in result.output
    assert result.exit_code == 0
    mock_memberships_page.check()


def test_cli_list_custodians_lists_custodians(runner, mock_custodians_page):
    result = runner.invoke(incydr, ["legal-hold", "list-custodians", TEST_MATTER_ID])
    assert "id one" in result.output
    assert "id two" in result.output
    assert result.exit_code == 0
    mock_custodians_page.check()


def test_cli_add_custodian_adds_custodian(runner, mock_add_custodian):
    result = runner.invoke(
        incydr,
        [
            "legal-hold",
            "add-custodian",
            "--user-id",
            TEST_USER_ID,
            "--matter-id",
            TEST_MATTER_ID,
        ],
    )
    assert result.exit_code == 0
    mock_add_custodian.check()


def test_cli_remove_custodian_removes_custodian(runner, mock_remove_custodian):
    result = runner.invoke(
        incydr,
        [
            "legal-hold",
            "remove-custodian",
            "--user-id",
            TEST_USER_ID,
            "--matter-id",
            TEST_MATTER_ID,
        ],
    )
    assert result.exit_code == 0
    mock_remove_custodian.check()


def test_cli_list_matters_lists_matters(runner, mock_matters_page):
    result = runner.invoke(incydr, ["legal-hold", "list-matters"])
    assert "sdk test matter" in result.output
    assert result.exit_code == 0
    mock_matters_page.check()


def test_cli_create_matter_creates_matter(runner, mock_create_matter):
    result = runner.invoke(
        incydr,
        [
            "legal-hold",
            "create-matter",
            "--policy-id",
            TEST_MATTER["policy_id"],
            "--name",
            TEST_MATTER["name"],
        ],
    )
    assert "sdk test matter" in result.output
    assert result.exit_code == 0
    mock_create_matter.check()


def test_cli_deactivate_matter_deactivates_matter(runner, mock_deactivate_matter):
    result = runner.invoke(incydr, ["legal-hold", "deactivate-matter", TEST_MATTER_ID])
    assert result.exit_code == 0
    mock_deactivate_matter.check()


def test_cli_reactivate_matter_reactivates_matter(runner, mock_reactivate_matter):
    result = runner.invoke(incydr, ["legal-hold", "reactivate-matter", TEST_MATTER_ID])
    assert result.exit_code == 0
    mock_reactivate_matter.check()


def test_cli_show_matter_shows_matter(runner, mock_get_matter):
    result = runner.invoke(incydr, ["legal-hold", "show-matter", TEST_MATTER_ID])
    assert "sdk test matter" in result.output
    assert result.exit_code == 0
    mock_get_matter.check()


def test_cli_list_policies_lists_policies(runner, mock_policies_page):
    result = runner.invoke(incydr, ["legal-hold", "list-policies"])
    assert "policy id" in result.output
    assert result.exit_code == 0
    mock_policies_page.check()


def test_cli_show_policy_shows_policy(runner, mock_get_policy):
    result = runner.invoke(incydr, ["legal-hold", "show-policy", TEST_POLICY_ID])
    assert "policy id" in result.output
    assert result.exit_code == 0
    mock_get_policy.check()
