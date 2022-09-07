import datetime
import json
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer
from requests import Response

from incydr import Client
from incydr._user_risk_profiles.models import UpdatedUserRiskProfile
from incydr._user_risk_profiles.models import UserRiskProfile
from incydr._user_risk_profiles.models import UserRiskProfilesPage

TEST_USER_RISK_PROFILE_1 = {
    "active": "true",
    "cloudAliases": [],
    "country": "France",
    "deleted": "false",
    "department": "Finance",
    "displayName": "Phill",
    "division": "22-19",
    "employmentType": "Part-Time",
    "endDate": "2022-07-18T16:40:53.335018Z",
    "locality": None,
    "managerDisplayName": None,
    "managerId": None,
    "managerUsername": None,
    "notes": None,
    "region": None,
    "startDate": "2022-07-18T16:39:51.356082Z",
    "supportUser": None,
    "tenantId": None,
    "title": None,
    "userId": "1",
    "username": None,
}

TEST_USER_RISK_PROFILE_2 = {
    "active": "true",
    "cloudAliases": [],
    "country": "France",
    "deleted": "false",
    "department": "Finance",
    "displayName": "Phill",
    "division": "22-19",
    "employmentType": "Part-Time",
    "endDate": "2022-07-18T16:40:53.335018Z",
    "locality": "Paris",
    "managerDisplayName": "Phill #2",
    "managerId": "22-20",
    "managerUsername": "Bob-1234",
    "notes": "These are notes",
    "region": "Region of Paris",
    "startDate": "2022-07-18T16:39:51.356082Z",
    "supportUser": "true",
    "tenantId": "124",
    "title": "Exist",
    "userId": "2",
    "username": "C424",
}


def test_get_single_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v1/user_risk_profile/2").respond_with_json(
        TEST_USER_RISK_PROFILE_2
    )
    client = Client()
    user_risk_profile = client.user_risk_profiles.v1.get_user_risk_profile(2)
    assert isinstance(user_risk_profile, UserRiskProfile)
    assert user_risk_profile.userId == 2
    assert user_risk_profile.startDate == datetime.datetime.fromisoformat(
        TEST_USER_RISK_PROFILE_2["startDate"].replace("Z", "+00:00")
    )
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
    httpserver_auth.expect_request("/v1/user_risk_profile").respond_with_json(
        user_risk_profiles_data
    )

    client = Client()
    page = client.user_risk_profiles.v1.get_list_user_risk_profile()
    assert isinstance(page, UserRiskProfilesPage)
    assert page.userRiskProfiles[0].json() == json.dumps(TEST_USER_RISK_PROFILE_1)
    assert page.userRiskProfiles[1].json() == json.dumps(TEST_USER_RISK_PROFILE_2)
    assert page.totalCount == len(page.userRiskProfiles)


def test_update_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v1/user_risk_profile/2").respond_with_json(
        TEST_USER_RISK_PROFILE_2
    )

    client = Client()
    user_risk_profile = client.user_risk_profiles.v1.get_user_risk_profile(2)
    assert isinstance(user_risk_profile, UserRiskProfile)
    assert user_risk_profile.userId == 2
    assert user_risk_profile.startDate == datetime.datetime.fromisoformat(
        TEST_USER_RISK_PROFILE_2["startDate"].replace("Z", "+00:00")
    )
    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_2)


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page": 1,
        "pageSize": 1,
    }
    query_2 = {"page": 2, "pageSize": 2}

    user_risk_profile_data_1 = {
        "userRiskProfiles": [TEST_USER_RISK_PROFILE_1],
        "totalCount": 1,
    }
    user_risk_profile_data_2 = {
        "userRiskProfiles": [TEST_USER_RISK_PROFILE_2],
        "totalCount": 1,
    }

    httpserver_auth.expect_ordered_request(
        "/v1/user_risk_profile", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(user_risk_profile_data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/user_risk_profile", method="GET", query_string=urlencode(query_2)
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
    httpserver_auth.expect_request(
        "/v1/user_risk_profile/2", method="PUT"
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    user_risk_profile = client.user_risk_profiles.v1.update(
        "2",
        "These are new notes",
        "2022-07-18T16:40:53.335019Z",
        "2022-07-18T16:40:53.335678Z",
    )

    assert isinstance(user_risk_profile, UpdatedUserRiskProfile)
    assert user_risk_profile.notes == TEST_USER_RISK_PROFILE_2["notes"]
    assert user_risk_profile.startDate == TEST_USER_RISK_PROFILE_2["startDate"].replace(
        "Z", "+00:00"
    )
    assert user_risk_profile.endDate == TEST_USER_RISK_PROFILE_2["startDate"].replace(
        "Z", "+00:00"
    )

    assert user_risk_profile.json() == json.dumps(TEST_USER_RISK_PROFILE_2)


def test_add_cloud_aliases_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/user_risk_profile/2/add-cloud-aliases"
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    response = client.user_risk_profiles.v1.add_cloud_aliases("2", ["alias_one", "two"])

    assert isinstance(response, Response)
    assert response.status_code == 200

    assert response.json() == json.dumps({})


def test_delete_cloud_aliases_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/user_risk_profile/2/delete-cloud-aliases"
    ).respond_with_json(TEST_USER_RISK_PROFILE_2)

    client = Client()
    response = client.user_risk_profiles.v1.delete_cloud_aliases(
        "2", ["alias_one", "two"]
    )

    assert isinstance(response, Response)
    assert response.status_code == 200

    assert response.json() == json.dumps({})
