import json
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer
from requests import Response

from incydr import Client
from incydr._trusted_activities.models import TrustedActivitiesPage
from incydr._trusted_activities.models import TrustedActivity

TEST_TRUSTED_ACTIVITY_1 = {
    "activityActionGroups": [
        {
            "activityActions": [
                {"providers": [{"name": "BOX"}], "activityType": "CLOUD_SHARE"}
            ],
            "name": "DEFAULT",
        }
    ],
    "activityId": "1234",
    "description": None,
    "principalType": None,
    "activityType": "DOMAIN",
    "updateTime": None,
    "updatedByPrincipalId": "123",
    "updatedByPrincipalName": "Indiscreet User",
    "value": "Onedrive",
}

TEST_TRUSTED_ACTIVITY_2 = {
    "activityActionGroups": [
        {
            "activityActions": [
                {"providers": [{"name": "BOX"}], "activityType": "CLOUD_SHARE"}
            ],
            "name": "DEFAULT",
        }
    ],
    "activityId": "1324",
    "description": "This is a description",
    "principalType": "API_KEY",
    "activityType": "DOMAIN",
    "updateTime": None,
    "updatedByPrincipalId": "999",
    "updatedByPrincipalName": "John Debuyer",
    "value": "Onedrive",
}


def test_get_single_trusted_activity_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v2/trusted-activities/1234").respond_with_json(
        TEST_TRUSTED_ACTIVITY_1
    )
    client = Client()
    trusted_activity = client.trusted_activities.v2.get_trusted_activity("1234")
    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_id == "1234"
    assert trusted_activity.json() == json.dumps(TEST_TRUSTED_ACTIVITY_1)


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    trusted_activities_data = {
        "trustedActivities": [
            TEST_TRUSTED_ACTIVITY_1,
            TEST_TRUSTED_ACTIVITY_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/trusted-activities", query_string=urlencode({"page": 1, "page_size": 100})
    ).respond_with_json(trusted_activities_data)

    client = Client()
    page = client.trusted_activities.v2.get_page()
    assert isinstance(page, TrustedActivitiesPage)
    assert page.trusted_activities[0].json() == json.dumps(TEST_TRUSTED_ACTIVITY_1)
    assert page.trusted_activities[1].json() == json.dumps(TEST_TRUSTED_ACTIVITY_2)
    assert page.total_count == len(page.trusted_activities) == 2


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "page_num": 1,
        "page_size": 2,
    }
    query_2 = {"page_num": 2, "page_size": 2}

    trusted_activities_data_1 = {
        "trustedActivities": [TEST_TRUSTED_ACTIVITY_1, TEST_TRUSTED_ACTIVITY_2],
        "totalCount": 2,
    }
    trusted_activities_data_2 = {
        "trustedActivities": [],
        "totalCount": 2,
    }

    httpserver_auth.expect_request(
        "/v2/trusted-activities", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(trusted_activities_data_1)

    httpserver_auth.expect_request(
        "/v2/trusted-activities", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(trusted_activities_data_2)

    client = Client()
    iterator = client.trusted_activities.v2.iter_all(page_size=2)
    total_trusted_activities = 0
    expected_trusted_activities = [TEST_TRUSTED_ACTIVITY_1, TEST_TRUSTED_ACTIVITY_2]

    for item in iterator:
        total_trusted_activities += 1
        assert isinstance(item, TrustedActivity)
        assert item.json() == json.dumps(expected_trusted_activities.pop(0))
    assert total_trusted_activities == 2


def test_create_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    test_data = {
        "activity_type": "ACCOUNT_NAME",
        "value": "New value",
        "description": "New description",
        "activity_action_groups": None,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.create(**test_data)

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == test_data["activity_type"]
    assert trusted_activity.value == test_data["value"]
    assert trusted_activity.description == test_data["description"]


def test_delete_user_risk_profile_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v2/trusted-activities/1234").respond_with_data()

    client = Client()
    response = client.trusted_activities.v2.delete("1234")

    assert isinstance(response, Response)
    assert response.status_code == 200
