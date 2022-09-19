import datetime
import json
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer
from requests import Response

from incydr import Client
from incydr._user_risk_profiles.models import UserRiskProfile
from incydr._user_risk_profiles.models import UserRiskProfilesPage

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
    "userId": "1",
    "username": None,
}

TEST_USER_RISK_PROFILE_1_UPDATED = {
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
    "notes": "New Notes",
    "region": None,
    "startDate": {"year": 2019, "month": 3, "day": 2},
    "supportUser": None,
    "tenantId": None,
    "title": None,
    "userId": "1",
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


def test_get_single_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v1/user-risk-profiles/2").respond_with_json(
        TEST_USER_RISK_PROFILE_2
    )
    client = Client()
    user_risk_profile = client.user_risk_profiles.v1.get_user_risk_profile("2")
    assert isinstance(user_risk_profile, UserRiskProfile)
    assert user_risk_profile.user_id == "2"
    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_2)


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
    page = client.user_risk_profiles.v1.get_page()
    assert isinstance(page, UserRiskProfilesPage)
    assert page.user_risk_profiles[0].json() == json.dumps(TEST_USER_RISK_PROFILE_1)
    assert page.user_risk_profiles[1].json() == json.dumps(TEST_USER_RISK_PROFILE_2)
    assert page.total_count == len(page.user_risk_profiles) == 2


def test_update_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    roles_data = TEST_USER_RISK_PROFILE_1_UPDATED

    httpserver_auth.expect_request(
        "/v1/user-risk-profiles/1", method="PATCH"
    ).respond_with_json(roles_data)

    client = Client()
    response = client.user_risk_profiles.v1.update(
        user_id="1",
        notes="New Notes"
    )
    assert isinstance(response, UserRiskProfile)
    assert response.json() == json.dumps(TEST_USER_RISK_PROFILE_1_UPDATED)


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
    iterator = client.user_risk_profiles.v1.iter_all(page_size=2)
    total_user_risk_profiles = 0
    expected_user_risk_profiles = [TEST_USER_RISK_PROFILE_1, TEST_USER_RISK_PROFILE_2]

    for item in iterator:
        total_user_risk_profiles += 1
        assert isinstance(item, UserRiskProfile)
        assert item.json() == json.dumps(expected_user_risk_profiles.pop(0))
    assert total_user_risk_profiles == 2


def test_update_when_default_params_returns_expected_data(httpserver_auth: HTTPServer):
    query = {"paths": ["startDate", "endDate", "notes"]}
    data = {
        "endDate": {
            "year": 2020,
            "month": 9,
            "day": 1,
        },
        "notes": "These are new notes",
        "startDate": {
            "year": 2022,
            "month": 8,
            "day": 2,
        },
    }
    httpserver_auth.expect_request(
        "/v1/user-risk-profiles/2",
        method="PATCH",
        query_string=urlencode(query, doseq=True),
        json=data,
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    user_risk_profile = client.user_risk_profiles.v1.update(
        "2",
        notes="These are new notes",
        start_date=datetime.datetime(
            2022, 8, 2, 13, 11, 7, 803762, tzinfo=datetime.timezone.utc
        ),
        end_date=datetime.datetime(
            2020, 9, 1, 13, 11, 7, 803762, tzinfo=datetime.timezone.utc
        ),
    )

    assert isinstance(user_risk_profile, UserRiskProfile)
    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_2)


def test_add_cloud_aliases_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/user-risk-profiles/2/add-cloud-aliases"
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    response = client.user_risk_profiles.v1.add_cloud_aliases("2", ["alias_one", "two"])

    assert isinstance(response, Response)
    assert response.status_code == 200


def test_delete_cloud_aliases_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/user-risk-profiles/2/delete-cloud-aliases"
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    response = client.user_risk_profiles.v1.delete_cloud_aliases(
        "2", ["alias_one", "two"]
    )

    assert isinstance(response, Response)
    assert response.status_code == 200
