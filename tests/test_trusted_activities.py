import json
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer
from requests import Response

from incydr import Client
from incydr._trusted_activities.models import TrustedActivitiesPage
from incydr._trusted_activities.models import TrustedActivity
from incydr.enums.trusted_activities import ActivityType

TEST_TRUSTED_ACTIVITY_1 = {
    "activityActionGroups": [
        {
            "name": "DEFAULT",
            "activityActions": [
                {"type": "CLOUD_SHARE", "providers": [{"name": "BOX"}]}
            ],
        }
    ],
    "activityId": "1234",
    "description": None,
    "principalType": None,
    "activityType": None,
    "updateTime": None,
    "updatedByPrincipalId": "123",
    "updatedByPrincipalName": "Indiscreet User",
    "value": "Onedrive",
    "type": "DOMAIN",
}

TEST_TRUSTED_ACTIVITY_2 = {
    "activityActionGroups": [
        {
            "name": "DEFAULT",
            "activityActions": [
                {"type": "CLOUD_SHARE", "providers": [{"name": "BOX"}]}
            ],
        }
    ],
    "activityId": "1324",
    "description": "This is a description",
    "principalType": "API_KEY",
    "activityType": "SLACK",
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
        "/v2/trusted-activities",
        query_string=urlencode({"page_num": 1, "page_size": 100}),
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


def test_add_domain_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    domain = "testDomain.com"
    activity_type = ActivityType.DOMAIN
    activity_action_groups = [
        {
            "name": "DEFAULT",
            "activityActions": [
                {"type": "FILE_UPLOAD", "providers": None},
                {"type": "GIT_PUSH", "providers": None},
                {
                    "type": "CLOUD_SYNC",
                    "providers": [
                        {"name": "BOX"},
                        {"name": "ICLOUD"},
                        {"name": "GOOGLE_DRIVE"},
                        {"name": "ONE_DRIVE"},
                    ],
                },
                {
                    "type": "CLOUD_SHARE",
                    "providers": [
                        {"name": "BOX"},
                        {"name": "GOOGLE_DRIVE"},
                        {"name": "ONE_DRIVE"},
                    ],
                },
                {
                    "type": "EMAIL",
                    "providers": [{"name": "GMAIL"}, {"name": "OFFICE_365"}],
                },
            ],
        }
    ]

    test_data = {
        "type": activity_type,
        "value": domain,
        "description": "Description",
        "activityActionGroups": activity_action_groups,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)

    test_response.update({"activityType": activity_type})

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.add_domain(
        domain=domain,
        description="Description",
        file_upload=True,
        cloud_sync_services=["BOX", "ICLOUD", "GOOGLE_DRIVE", "ONE_DRIVE"],
        cloud_share_services=["BOX", "GOOGLE_DRIVE", "ONE_DRIVE"],
        email_share_services=["GMAIL", "OFFICE_365"],
        git_push=True,
    )

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == activity_type
    assert trusted_activity.value == domain
    assert trusted_activity.description == test_data["description"]
    assert trusted_activity.activity_action_groups == activity_action_groups


def test_add_domain_when_invalid_trusted_provider_value_raises_error(
    httpserver_auth: HTTPServer,
):
    domain = "testDomain.com"
    client = Client()
    with pytest.raises(ValueError) as e:
        client.trusted_activities.v2.add_domain(
            domain=domain,
            cloud_sync_services=["invalid-value"],
        )
    assert (
        "'invalid-value' is not a valid incydr.enums.trusted_activities.CloudSyncApps. Expected one of ['BOX', 'GOOGLE_DRIVE', 'ICLOUD', 'ONE_DRIVE']"
        in str(e.value)
    )


def test_add_domain_when_no_trusted_actions_raises_error(httpserver_auth: HTTPServer):
    domain = "testDomain.com"
    client = Client()
    with pytest.raises(ValueError) as e:
        client.trusted_activities.v2.add_domain(domain=domain)
    assert "At least 1 action for the domain must be trusted." in str(e.value)


def test_add_url_path_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    url = "testDomain.com"
    activity_type = ActivityType.URL_PATH
    activity_action_groups = []

    test_data = {
        "type": activity_type,
        "value": url,
        "description": "Description",
        "activityActionGroups": activity_action_groups,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)

    test_response.update({"activityType": activity_type})

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.add_url_path(
        url=url, description="Description"
    )

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == activity_type
    assert trusted_activity.value == url
    assert trusted_activity.description == test_data["description"]
    assert trusted_activity.activity_action_groups == activity_action_groups


def test_create_trusted_activity_slack_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    workspace_name = "test workspace"
    activity_type = ActivityType.SLACK
    activity_action_groups = []

    test_data = {
        "type": activity_type,
        "value": workspace_name,
        "description": "Description",
        "activityActionGroups": activity_action_groups,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)

    test_response.update({"activityType": activity_type})

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.add_slack_workspace(
        workspace_name=workspace_name, description="Description"
    )

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == activity_type
    assert trusted_activity.value == workspace_name
    assert trusted_activity.description == test_data["description"]
    assert trusted_activity.activity_action_groups == activity_action_groups


def test_add_account_name_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    account_name = "test account"
    activity_type = ActivityType.ACCOUNT_NAME
    activity_action_groups = [
        {
            "name": "DEFAULT",
            "activityActions": [
                {
                    "type": "CLOUD_SYNC",
                    "providers": [{"name": "DROPBOX"}, {"name": "ONE_DRIVE"}],
                }
            ],
        }
    ]

    test_data = {
        "type": activity_type,
        "value": account_name,
        "description": "Description",
        "activityActionGroups": activity_action_groups,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)
    test_response.update({"activityType": activity_type})

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.add_account_name(
        account_name=account_name,
        description="Description",
        dropbox=True,
        one_drive=True,
    )

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == activity_type
    assert trusted_activity.value == account_name
    assert trusted_activity.description == test_data["description"]
    assert trusted_activity.activity_action_groups == activity_action_groups


def test_add_account_name_when_no_trusted_providers_raises_error(
    httpserver_auth: HTTPServer,
):
    client = Client()

    with pytest.raises(ValueError) as e:
        client.trusted_activities.v2.add_account_name(account_name="foo@bar.com")
    assert "At least 1 cloud sync service (dropbox, one_drive) must be trusted." in str(
        e.value
    )


def test_add_git_repository_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    git_uri = "test.com:example/myRepo"
    activity_type = ActivityType.GIT_REPOSITORY_URI
    activity_action_groups = [
        {
            "name": "DEFAULT",
            "activityActions": [
                {"type": "GIT_PUSH", "providers": []},
            ],
        }
    ]

    test_data = {
        "type": activity_type,
        "value": git_uri,
        "description": "Description",
        "activityActionGroups": activity_action_groups,
    }

    test_response = TEST_TRUSTED_ACTIVITY_1.copy()
    test_response.update(test_data)

    test_response.update({"activityType": activity_type})

    httpserver_auth.expect_request(
        uri="/v2/trusted-activities", method="POST", json=test_data
    ).respond_with_json(test_response)

    client = Client()
    trusted_activity = client.trusted_activities.v2.add_git_repository(
        git_uri=git_uri, description="Description"
    )

    assert isinstance(trusted_activity, TrustedActivity)
    assert trusted_activity.activity_type == activity_type
    assert trusted_activity.value == git_uri
    assert trusted_activity.description == test_data["description"]
    assert trusted_activity.activity_action_groups == activity_action_groups


def test_delete_trusted_activity_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v2/trusted-activities/1234").respond_with_data()

    client = Client()
    response = client.trusted_activities.v2.delete("1234")

    assert isinstance(response, Response)
    assert response.status_code == 200
