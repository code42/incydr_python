import datetime
import json
from typing import List
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.alert_rules.client import MissingUsernameCriterionError
from _incydr_sdk.alert_rules.models.response import RuleDetails
from _incydr_sdk.alert_rules.models.response import RuleUser
from _incydr_sdk.alert_rules.models.response import RuleUsersList
from _incydr_sdk.core.client import Client

TEST_RULE_ID = "test-rule-id"

list_input_param = pytest.mark.parametrize(
    "_input,expected",
    [(["test-1", "test-2"], ["test-1", "test-2"]), ("test-1", ["test-1"])],
)

TEST_RULE_USER_1 = {
    "userIdFromAuthority": "test-user-1",
    "aliases": ["test-alias-1"],
}
TEST_RULE_USER_2 = {
    "userIdFromAuthority": "test-user-2",
    "aliases": ["test-user-2", "test-alias-2"],
}

TEST_RULE_1 = {
    "name": "Suspicious File Mismatch Rule",
    "description": "A rule created to trigger alerts on suspicious file mismatch exfiltration",
    "severity": "",
    "isEnabled": True,
    "source": "",
    "notifications": {
        "isEnabled": True,
        "contacts": [
            {"isEnabled": True, "type": "EMAIL", "address": "myUsername@company.com"}
        ],
    },
    "education": None,
    "vectors": {
        "cloudSharing": {
            "observeAll": False,
            "box": {"observeAll": True, "publicLinkShare": True, "directShare": True},
            "googleDrive": {
                "observeAll": True,
                "publicLinkShare": True,
                "directShare": True,
            },
            "oneDrive": {
                "observeAll": True,
                "publicLinkShare": True,
                "directShare": True,
            },
            "criteriaOrder": 3,
        },
        "download": {
            "observeAll": True,
            "salesforce": True,
            "box": True,
            "googleDrive": True,
            "microsoftOneDrive": True,
            "criteriaOrder": 0,
        },
        "email": {
            "observeAll": True,
            "gmail": True,
            "microsoft365": True,
            "criteriaOrder": 0,
        },
        "fileUpload": {
            "cloudStorage": {"observeAll": True, "destinations": []},
            "email": {"observeAll": True, "destinations": []},
            "fileConversionTool": {"observeAll": True, "destinations": []},
            "messaging": {"observeAll": True, "destinations": []},
            "pdfManager": {"observeAll": True, "destinations": []},
            "productivityTool": {"observeAll": True, "destinations": []},
            "socialMedia": {"observeAll": True, "destinations": []},
            "sourceCodeRepository": {"observeAll": True, "destinations": []},
            "webHosting": {"observeAll": True, "destinations": []},
            "advancedSettings": {"observeUncategorized": True},
            "criteriaOrder": 3,
        },
        "removableMedia": {"isEnabled": True, "criteriaOrder": 3},
    },
    "filters": {
        "fileCategory": {
            "categories": ["Archive", "Pdf", "SourceCode"],
            "criteriaOrder": 3,
        },
        "fileName": {"patterns": ["*.cs", "*.sh"], "criteriaOrder": 3},
        "fileTypeMismatch": {"isEnabled": True, "criteriaOrder": 3},
        "fileVolume": {
            "countGreaterThan": 125,
            "operator": "AND",
            "sizeGreaterThanInBytes": 1024,
            "criteriaOrder": 3,
        },
        "riskIndicator": {
            "categories": ["string"],
            "indicators": ["string"],
            "criteriaOrder": 0,
        },
        "riskSeverity": {
            "low": True,
            "moderate": True,
            "high": True,
            "critical": True,
            "criteriaOrder": 0,
        },
        "username": {
            "mode": "INCLUDE",
            "usernames": ["myUsername@company.com", "anotherUsername@company.com"],
            "criteriaOrder": 3,
        },
        "watchlist": {"watchlists": [{"id": "string"}], "criteriaOrder": 0},
    },
    "id": TEST_RULE_ID,
    "createdAt": "2022-10-05T15:38:53.385501Z",
    "createdBy": "my-username@company.com",
    "modifiedAt": "2022-10-05T15:38:53.385521Z",
    "modifiedBy": "my-username@company.com",
    "isSystemRule": True,
}


TEST_RULE_2 = {
    "name": "An Alert Rule",
    "description": "An alert rule.",
    "severity": "",
    "isEnabled": True,
    "source": "",
    "notifications": {
        "isEnabled": True,
        "contacts": [
            {"isEnabled": True, "type": "EMAIL", "address": "myUsername@company.com"}
        ],
    },
    "education": None,
    "vectors": {
        "cloudSharing": {
            "observeAll": False,
            "box": {"observeAll": True, "publicLinkShare": True, "directShare": True},
            "googleDrive": {
                "observeAll": True,
                "publicLinkShare": True,
                "directShare": True,
            },
            "oneDrive": {
                "observeAll": True,
                "publicLinkShare": True,
                "directShare": True,
            },
            "criteriaOrder": 3,
        },
        "download": {
            "observeAll": True,
            "salesforce": True,
            "box": True,
            "googleDrive": True,
            "microsoftOneDrive": True,
            "criteriaOrder": 0,
        },
        "email": {
            "observeAll": True,
            "gmail": True,
            "microsoft365": True,
            "criteriaOrder": 0,
        },
        "fileUpload": {
            "cloudStorage": {"observeAll": True, "destinations": []},
            "email": {"observeAll": True, "destinations": []},
            "fileConversionTool": {"observeAll": True, "destinations": []},
            "messaging": {"observeAll": True, "destinations": []},
            "pdfManager": {"observeAll": True, "destinations": []},
            "productivityTool": {"observeAll": True, "destinations": []},
            "socialMedia": {"observeAll": True, "destinations": []},
            "sourceCodeRepository": {"observeAll": True, "destinations": []},
            "webHosting": {"observeAll": True, "destinations": []},
            "advancedSettings": {"observeUncategorized": True},
            "criteriaOrder": 3,
        },
        "removableMedia": {"isEnabled": True, "criteriaOrder": 3},
    },
    "filters": {
        "fileCategory": {
            "categories": ["Archive", "Pdf", "SourceCode"],
            "criteriaOrder": 3,
        },
        "fileName": {"patterns": ["*.cs", "*.sh"], "criteriaOrder": 3},
        "fileTypeMismatch": {"isEnabled": True, "criteriaOrder": 3},
        "fileVolume": {
            "countGreaterThan": 125,
            "operator": "AND",
            "sizeGreaterThanInBytes": 1024,
            "criteriaOrder": 3,
        },
        "riskIndicator": {
            "categories": ["string"],
            "indicators": ["string"],
            "criteriaOrder": 0,
        },
        "riskSeverity": {
            "low": True,
            "moderate": True,
            "high": True,
            "critical": True,
            "criteriaOrder": 0,
        },
        "username": {
            "mode": "INCLUDE",
            "usernames": ["myUsername@company.com", "anotherUsername@company.com"],
            "criteriaOrder": 3,
        },
        "watchlist": {"watchlists": [{"id": "string"}], "criteriaOrder": 0},
    },
    "id": "test-rule-id-2",
    "createdAt": "2022-10-05T15:38:53.385501Z",
    "createdBy": "my-username@company.com",
    "modifiedAt": "2022-10-05T15:38:53.385521Z",
    "modifiedBy": "my-username@company.com",
    "isSystemRule": True,
}

TEST_USER_RISK_PROFILE = {
    "active": True,
    "cloudAliases": ["cloud-user-1@email.com", "foo@bar.com", "bazAccount"],
    "country": "France",
    "deleted": False,
    "department": "Finance",
    "displayName": "Phill",
    "division": "22-19",
    "employmentType": "Part-Time",
    "endDate": {
        "year": 2021,
        "month": 2,
        "day": 1,
    },
    "locality": None,
    "managerDisplayName": None,
    "managerId": None,
    "managerUsername": None,
    "notes": None,
    "region": None,
    "startDate": {"year": 2019, "month": 3, "day": 2},
    "supportUser": None,
    "tenantId": None,
    "title": None,
    "userId": "1",
    "username": None,
}


@pytest.fixture
def mock_get_page(httpserver_auth):
    data = [TEST_RULE_1, TEST_RULE_2]
    query = {
        "PageNumber": 0,
        "PageSize": 100,
    }
    httpserver_auth.expect_request(
        uri="/v2/alert-rules", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)


@pytest.fixture
def mock_get(httpserver_auth):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}", method="GET"
    ).respond_with_json(TEST_RULE_1)


@pytest.fixture
def mock_remove_users(httpserver_auth):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/users", method="DELETE"
    ).respond_with_data()


@pytest.fixture
def mock_get_users(httpserver_auth):
    data = {
        "id": TEST_RULE_ID,
        "users": [TEST_RULE_USER_1, TEST_RULE_USER_2],
        "mode": "INCLUDE",
    }
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/users",
        method="GET",
    ).respond_with_json(data)


def test_get_page_when_default_params_returns_expected_data(
    mock_get_page,
):
    c = Client()
    response = c.alert_rules.v2.get_page()
    assert isinstance(response, List)
    for rule in response:
        assert isinstance(rule, RuleDetails)
    assert response[0].json() == json.dumps(TEST_RULE_1)
    assert response[1].json() == json.dumps(TEST_RULE_2)


def test_get_page_when_custom_params_makes_expected_call(httpserver_auth: HTTPServer):
    data = [TEST_RULE_1, TEST_RULE_2]

    query = {"PageNumber": 3, "PageSize": 10, "WatchlistId": "42-watchlist"}
    httpserver_auth.expect_request(
        uri="/v2/alert-rules", method="GET", query_string=urlencode(query)
    ).respond_with_json(data)

    c = Client()
    response = c.alert_rules.v2.get_page(
        page_num=3, page_size=10, watchlist_id="42-watchlist"
    )
    assert isinstance(response, List)
    for rule in response:
        assert isinstance(rule, RuleDetails)
    assert response[0].json() == json.dumps(TEST_RULE_1)
    assert response[1].json() == json.dumps(TEST_RULE_2)
    assert len(response) == 2


def test_iter_all_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    test_rule_3 = TEST_RULE_1.copy()
    test_rule_3["id"] = "test-rule-3"

    query_1 = {
        "PageNumber": 0,
        "PageSize": 2,
    }
    query_2 = {
        "PageNumber": 1,
        "PageSize": 2,
    }

    data_1 = [TEST_RULE_1, TEST_RULE_2]
    date_2 = [test_rule_3]

    httpserver_auth.expect_ordered_request(
        "/v2/alert-rules", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        "/v2/alert-rules", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(date_2)

    client = Client()
    iterator = client.alert_rules.v2.iter_all(page_size=2)
    total = 0
    expected = [TEST_RULE_1, TEST_RULE_2, test_rule_3]
    for item in iterator:
        total += 1
        assert isinstance(item, RuleDetails)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 3


def test_get_rule_returns_expected_data(mock_get):
    c = Client()
    response = c.alert_rules.v2.get_rule(TEST_RULE_ID)
    assert isinstance(response, RuleDetails)
    assert response.id == TEST_RULE_ID
    assert response.created_at == datetime.datetime.fromisoformat(
        TEST_RULE_1["createdAt"].replace("Z", "+00:00")
    )
    assert response.modified_at == datetime.datetime.fromisoformat(
        TEST_RULE_1["modifiedAt"].replace("Z", "+00:00")
    )
    assert response.json() == json.dumps(TEST_RULE_1)


def test_enable_rules_when_single_rule_id_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/enable", method="POST"
    ).respond_with_data()

    c = Client()
    assert c.alert_rules.v2.enable_rules(rule_ids=TEST_RULE_ID).status_code == 200


def test_enable_rules_when_multiple_rule_ids_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        uri="/v2/alert-rules/enable", method="POST", json=["test-1", "test-2"]
    ).respond_with_data()

    c = Client()
    assert (
        c.alert_rules.v2.enable_rules(rule_ids=["test-1", "test-2"]).status_code == 200
    )


def test_disable_rules_when_single_rule_id_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/disable", method="POST"
    ).respond_with_data()

    c = Client()
    assert c.alert_rules.v2.disable_rules(rule_ids=TEST_RULE_ID).status_code == 200


def test_disable_rules_when_multiple_rule_ids_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        uri="/v2/alert-rules/disable",
        method="POST",
        json=["test-1", "test-2"],
    ).respond_with_data()

    c = Client()
    assert (
        c.alert_rules.v2.disable_rules(rule_ids=["test-1", "test-2"]).status_code == 200
    )


def test_remove_all_users_returns_expected_data(mock_remove_users):
    c = Client()
    assert c.alert_rules.v2.remove_all_users(TEST_RULE_ID).status_code == 200


def test_get_users_when_default_params_returns_expected_data(mock_get_users):
    c = Client()
    response = c.alert_rules.v2.get_users(TEST_RULE_ID)
    assert isinstance(response, RuleUsersList)
    assert response.id == TEST_RULE_ID
    assert response.mode == "INCLUDE"
    for user in response.users:
        assert isinstance(user, RuleUser)
    assert response.users[0].json() == json.dumps(TEST_RULE_USER_1)
    assert response.users[1].json() == json.dumps(TEST_RULE_USER_2)


def test_get_users_when_400_raises_missing_username_criterion_error(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/users",
        method="GET",
    ).respond_with_data(status=400)

    c = Client()
    with pytest.raises(MissingUsernameCriterionError) as e:
        c.alert_rules.v2.get_users(TEST_RULE_ID)
    assert f"Rule '{TEST_RULE_ID}' has no username filter." in str(e.value)


# ************************************************ CLI ************************************************


def test_cli_list_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_page
):
    result = runner.invoke(incydr, ["alert-rules", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get, mock_get_users
):
    result = runner.invoke(incydr, ["alert-rules", "show", TEST_RULE_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize("command", ["enable", "disable"])
def test_cli_enable_and_disable_make_expected_call(
    httpserver_auth: HTTPServer, runner, command
):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{command}",
        method="POST",
        json=["test-1", "test-2"],
    ).respond_with_data()
    result = runner.invoke(incydr, ["alert-rules", command, "test-1,test-2"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_remove_all_users_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_remove_users
):
    result = runner.invoke(incydr, ["alert-rules", "remove-all-users", TEST_RULE_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_users_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_users
):
    result = runner.invoke(incydr, ["alert-rules", "list-users", TEST_RULE_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_users_when_400_raises_returns_no_results_found_message(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        uri=f"/v2/alert-rules/{TEST_RULE_ID}/users",
        method="GET",
    ).respond_with_data(status=400)

    result = runner.invoke(incydr, ["alert-rules", "list-users", TEST_RULE_ID])
    assert result.exit_code == 0
    assert f"No results found for rule {TEST_RULE_ID}" in result.output
