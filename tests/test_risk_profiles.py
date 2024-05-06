import datetime
import json
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.risk_profiles.models import RiskProfile
from _incydr_sdk.risk_profiles.models import RiskProfilesPage
from incydr import Client
from tests.test_users import TEST_USER_1

TEST_USER_ID = "user-1"

TEST_USER_RISK_PROFILE_1 = {
    "active": True,
    "cloudAliases": [],
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
    "userId": TEST_USER_ID,
    "username": None,
}

TEST_USER_RISK_PROFILE_2 = {
    "active": True,
    "cloudAliases": [],
    "country": "France",
    "deleted": False,
    "department": "Finance",
    "displayName": "Phill",
    "division": "22-19",
    "employmentType": "Part-Time",
    "endDate": {"year": 2022, "month": 7, "day": 18},
    "locality": "Paris",
    "managerDisplayName": "Phill #2",
    "managerId": "22-20",
    "managerUsername": "Bob-1234",
    "notes": "These are notes",
    "region": "Region of Paris",
    "startDate": {"year": 2020, "month": 2, "day": 1},
    "supportUser": True,
    "tenantId": "124",
    "title": "Exist",
    "userId": "2",
    "username": "C424",
}

user_input = pytest.mark.parametrize("user", [TEST_USER_ID, "foo@bar.com"])


@pytest.fixture
def mock_user_lookup(httpserver_auth):
    query_1 = {
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }

    data_1 = {"users": [TEST_USER_1], "totalCount": 1}
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


@pytest.fixture
def mock_get_profile(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/user-risk-profiles/{TEST_USER_ID}"
    ).respond_with_json(TEST_USER_RISK_PROFILE_1)


@pytest.fixture
def mock_update_profile(httpserver_auth: HTTPServer):
    query = {"paths": ["startDate", "endDate", "notes"]}
    data = {
        "endDate": {
            "year": 2022,
            "month": 8,
            "day": 2,
        },
        "notes": "These are new notes",
        "startDate": {
            "year": 2020,
            "month": 9,
            "day": 1,
        },
    }
    httpserver_auth.expect_request(
        f"/v1/user-risk-profiles/{TEST_USER_ID}",
        method="PATCH",
        query_string=urlencode(query, doseq=True),
        json=data,
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)


def test_get_single_user_risk_profile_when_default_params_returns_expected_data(
    mock_get_profile,
):
    client = Client()
    user_risk_profile = client.risk_profiles.v1.get_risk_profile(TEST_USER_ID)
    assert isinstance(user_risk_profile, RiskProfile)
    assert user_risk_profile.user_id == TEST_USER_ID
    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_1)


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    user_risk_profiles_data = {
        "userRiskProfiles": [
            TEST_USER_RISK_PROFILE_1,
            TEST_USER_RISK_PROFILE_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request("/v1/user-risk-profiles").respond_with_json(
        user_risk_profiles_data
    )

    client = Client()
    page = client.risk_profiles.v1.get_page()
    assert isinstance(page, RiskProfilesPage)
    assert page.user_risk_profiles[0].json() == json.dumps(TEST_USER_RISK_PROFILE_1)
    assert page.user_risk_profiles[1].json() == json.dumps(TEST_USER_RISK_PROFILE_2)
    assert page.total_count == len(page.user_risk_profiles) == 2


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page": 1,
        "page_size": 2,
    }
    query_2 = {"page": 2, "page_size": 2}

    user_risk_profile_data_1 = {
        "userRiskProfiles": [TEST_USER_RISK_PROFILE_1, TEST_USER_RISK_PROFILE_2],
        "totalCount": 2,
    }
    user_risk_profile_data_2 = {
        "userRiskProfiles": [],
        "totalCount": 2,
    }

    httpserver_auth.expect_request(
        "/v1/user-risk-profiles", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(user_risk_profile_data_1)

    httpserver_auth.expect_request(
        "/v1/user-risk-profiles", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(user_risk_profile_data_2)
    client = Client()
    iterator = client.risk_profiles.v1.iter_all(page_size=2)
    total_user_risk_profiles = 0
    expected_user_risk_profiles = [TEST_USER_RISK_PROFILE_1, TEST_USER_RISK_PROFILE_2]

    for item in iterator:
        total_user_risk_profiles += 1
        assert isinstance(item, RiskProfile)
        assert item.json() == json.dumps(expected_user_risk_profiles.pop(0))
    assert total_user_risk_profiles == 2


def test_update_when_default_params_returns_expected_data(mock_update_profile):
    client = Client()
    user_risk_profile = client.risk_profiles.v1.update(
        TEST_USER_ID,
        notes="These are new notes",
        start_date=datetime.datetime(2020, 9, 1, tzinfo=datetime.timezone.utc),
        end_date=datetime.datetime(2022, 8, 2, tzinfo=datetime.timezone.utc),
    )

    assert isinstance(user_risk_profile, RiskProfile)
    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_2)


# ************************************************ CLI ************************************************


def test_cli_list_makes_expected_call(httpserver_auth: HTTPServer, runner):
    query_1 = {
        "page": 1,
        "page_size": 100,
    }
    user_risk_profile_data_1 = {
        "userRiskProfiles": [TEST_USER_RISK_PROFILE_1, TEST_USER_RISK_PROFILE_2],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v1/user-risk-profiles", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(user_risk_profile_data_1)

    result = runner.invoke(incydr, ["risk-profiles", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_show_makes_expected_call(
    httpserver_auth: HTTPServer, runner, user, mock_get_profile, mock_user_lookup
):
    result = runner.invoke(incydr, ["risk-profiles", "show", user])
    httpserver_auth.check()
    assert result.exit_code == 0


@user_input
def test_cli_update_when_all_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, user, mock_user_lookup, mock_update_profile
):
    result = runner.invoke(
        incydr,
        [
            "risk-profiles",
            "update",
            user,
            "--start-date",
            "2020-09-01",
            "--end-date",
            "2022-08-02",
            "--notes",
            "These are new notes",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "date_option,date_input", [("--start-date", "2022-02-30"), ("--end-date", "1-1")]
)
def test_cli_update_when_incorrect_date_format_raises_date_parse_exception(
    httpserver_auth: HTTPServer, runner, date_option, date_input
):
    result = runner.invoke(
        incydr,
        ["risk-profiles", "update", TEST_USER_ID, date_option, date_input],
    )
    assert result.exit_code == 1
    assert "DateParseError: Error parsing time data." in result.output


def test_cli_update_when_no_options_raises_usage_error(
    httpserver_auth: HTTPServer, runner
):
    result = runner.invoke(incydr, ["risk-profiles", "update", TEST_USER_ID])
    assert result.exit_code == 2
    assert (
        "At least one of --start-date, --end-date, or --notes, or one of their corresponding clear flags, is required to update a risk profile."
        in str(result.output)
    )
