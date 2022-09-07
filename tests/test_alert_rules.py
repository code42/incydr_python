import json
from unittest import mock
from unittest.mock import PropertyMock

import pytest
from pytest_httpserver import HTTPServer

from incydr._alert_rules.models.response import AssignedUsersList
from incydr._core.client import Client

TEST_TENANT_ID = "test-tenant-id"
TEST_RULE_ID = "test-rule-id"

list_input_param = pytest.mark.parametrize(
    "_input,expected",
    [(["test-1", "test-2"], ["test-1", "test-2"]), ("test-1", ["test-1"])],
)

TEST_RULE_USER_1 = {
    "userIdFromAuthority": "test-user-1",
    "userAliasList": ["test-alias-1"],
}
TEST_RULE_USER_2 = {
    "userIdFromAuthority": "test-user-2",
    "userAliasList": ["test-user-2", "test-alias-2"],
}

TEST_CLOUD_SHARE_PERMS_RULE = {
    "tenantId": "MyExampleTenant",
    "name": "Removable Media Exfiltration Rule",
    "description": "Alert me on all removable media exfiltration.",
    "severity": "LOW",
    "isEnabled": "TRUE",
    "fileBelongsTo": {"usersToAlertOn": "ALL_USERS", "userList": ["user1", "user2"]},
    "notificationConfig": {
        "enabled": "TRUE",
        "notificationInfo": [
            {
                "notificationType": "EMAIL",
                "notificationAddress": "myUsername@company.com",
            }
        ],
    },
    "fileCategoryWatch": {"watchAllFiles": "FALSE", "fileCategoryList": ["ARCHIVE"]},
    "ruleSource": "Departing Employee",
    "watchGoogleDrive": {
        "publicOnTheWeb": "TRUE",
        "publicViaLink": "FALSE",
        "outsideTrustedDomains": "TRUE",
    },
    "watchMicrosoftOneDrive": {
        "publicViaLink": "FALSE",
        "outsideTrustedDomains": "TRUE",
    },
    "watchBox": {"publicViaLink": "FALSE", "outsideTrustedDomains": "TRUE"},
    "id": "RuleId",
    "createdAt": "2020-02-18T01:00:45.006683Z",
    "createdBy": "UserWhoCreatedTheRule",
    "modifiedAt": "2020-02-19T01:57:45.006683Z",
    "modifiedBy": "UserWhoMostRecentlyModifiedTheRule",
    "isSystem": "FALSE",
}

TEST_ENDPOINT_EXFIL_RULE = {
    "tenantId": "MyExampleTenant",
    "name": "Removable Media Exfiltration Rule",
    "description": "Alert me on all removable media exfiltration.",
    "severity": "LOW",
    "isEnabled": "TRUE",
    "fileBelongsTo": {"usersToAlertOn": "ALL_USERS", "userList": ["user1", "user2"]},
    "notificationConfig": {
        "enabled": "TRUE",
        "notificationInfo": [
            {
                "notificationType": "EMAIL",
                "notificationAddress": "myUsername@company.com",
            }
        ],
    },
    "fileCategoryWatch": {"watchAllFiles": "FALSE", "fileCategoryList": ["ARCHIVE"]},
    "ruleSource": "Departing Employee",
    "fileSizeAndCount": {
        "fileCountGreaterThan": "15",
        "totalSizeGreaterThanInBytes": "5000",
        "operator": "AND",
    },
    "fileActivityIs": {
        "syncedToCloudService": {
            "watchBox": "TRUE",
            "watchBoxDrive": "FALSE",
            "watchDropBox": "TRUE",
            "watchGoogleBackupAndSync": "FALSE",
            "watchAppleIcLoud": "TRUE",
            "watchMicrosoftOneDrive": "TRUE",
        },
        "uploadedOnRemovableMedia": "TRUE",
        "readByBrowserOrOther": "FALSE",
    },
    "timeWindow": "60",
    "id": "RuleId",
    "createdAt": "2020-02-18T01:00:45.006683Z",
    "createdBy": "UserWhoCreatedTheRule",
    "modifiedAt": "2020-02-19T01:57:45.006683Z",
    "modifiedBy": "UserWhoMostRecentlyModifiedTheRule",
    "isSystem": "FALSE",
}

TEST_FILE_TYPE_MISMATCH_RULE = {
    "tenantId": "MyExampleTenant",
    "name": "Removable Media Exfiltration Rule",
    "description": "Alert me on all removable media exfiltration.",
    "severity": "LOW",
    "isEnabled": "TRUE",
    "fileBelongsTo": {"usersToAlertOn": "ALL_USERS", "userList": ["user1", "user2"]},
    "notificationConfig": {
        "enabled": "TRUE",
        "notificationInfo": [
            {
                "notificationType": "EMAIL",
                "notificationAddress": "myUsername@company.com",
            }
        ],
    },
    "fileCategoryWatch": {"watchAllFiles": "FALSE", "fileCategoryList": ["ARCHIVE"]},
    "ruleSource": "Departing Employee",
    "id": "RuleId",
    "createdAt": "2020-02-18T01:00:45.006683Z",
    "createdBy": "UserWhoCreatedTheRule",
    "modifiedAt": "2020-02-19T01:57:45.006683Z",
    "modifiedBy": "UserWhoMostRecentlyModifiedTheRule",
    "isSystem": "FALSE",
}

TEST_FILE_NAME_RULE = {
    "tenantId": "MyExampleTenant",
    "name": "Removable Media Exfiltration Rule",
    "description": "Alert me on all removable media exfiltration.",
    "severity": "LOW",
    "isEnabled": "TRUE",
    "fileBelongsTo": {"usersToAlertOn": "ALL_USERS", "userList": ["user1", "user2"]},
    "notificationConfig": {
        "enabled": "TRUE",
        "notificationInfo": [
            {
                "notificationType": "EMAIL",
                "notificationAddress": "myUsername@company.com",
            }
        ],
    },
    "fileCategoryWatch": {"watchAllFiles": "FALSE", "fileCategoryList": ["ARCHIVE"]},
    "ruleSource": "Departing Employee",
    "fileNamePatterns": ["Q?ProductPlan.*", "*.cs"],
    "id": "RuleId",
    "createdAt": "2020-02-18T01:00:45.006683Z",
    "createdBy": "UserWhoCreatedTheRule",
    "modifiedAt": "2020-02-19T01:57:45.006683Z",
    "modifiedBy": "UserWhoMostRecentlyModifiedTheRule",
    "isSystem": "FALSE",
}


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    # TODO
    pass


def test_get_page_when_custom_params_returns_expected_data(httpserver_auth: HTTPServer):
    # TODO
    pass


# TODO
def test_get_rule_returns_expected_data(httpserver_auth: HTTPServer):
    pass


@list_input_param
def test_update_rules_returns_expected_data(
    httpserver_auth: HTTPServer, _input, expected
):
    data = {"tenantId": TEST_TENANT_ID, "ruleIds": expected, "isEnabled": True}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/update-is-enabled", method="POST", json=data
    ).respond_with_data()

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        assert (
            c.alert_rules.v1.update_rules(rule_ids=_input, enabled=True).status_code
            == 200
        )


def test_add_users_returns_expected_data(httpserver_auth: HTTPServer):
    data = {
        "tenantId": TEST_TENANT_ID,
        "ruleId": TEST_RULE_ID,
        "userList": [
            {"userIdFromAuthority": "user-1", "userAliasList": ["alias-1", "alias-2"]},
            {"userIdFromAuthority": "user-2", "userAliasList": []},
            {"userIdFromAuthority": "user-3", "userAliasList": ["alias-3"]},
        ],
    }
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/add-users", method="POST", json=data
    ).respond_with_data()

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        assert (
            c.alert_rules.v1.add_users(
                TEST_RULE_ID,
                users=[
                    ["user-1", "alias-1", "alias-2"],
                    "user-2",
                    ["user-3", "alias-3"],
                ],
            ).status_code
            == 200
        )


@list_input_param
def test_remove_users_returns_expected_data(
    httpserver_auth: HTTPServer, _input, expected
):
    data = {"tenantId": TEST_TENANT_ID, "ruleId": TEST_RULE_ID, "userIdList": expected}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/remove-users", method="POST", json=data
    ).respond_with_data()

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        assert (
            c.alert_rules.v1.remove_users(
                rule_id=TEST_RULE_ID, users=_input
            ).status_code
            == 200
        )


def test_remove_user_aliases_returns_expected_data(httpserver_auth: HTTPServer):
    data = {
        "tenantId": TEST_TENANT_ID,
        "ruleId": TEST_RULE_ID,
        "userList": [
            {"userIdFromAuthority": "user-1", "userAliasList": ["alias-0", "alias-1"]},
            {"userIdFromAuthority": "user-2", "userAliasList": ["alias-2"]},
            {"userIdFromAuthority": "user-3", "userAliasList": ["alias-3"]},
        ],
    }
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/remove-user-aliases", method="POST", json=data
    ).respond_with_data()

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        assert (
            c.alert_rules.v1.remove_user_aliases(
                TEST_RULE_ID,
                user_aliases=[
                    ["user-1", "alias-0", "alias-1"],
                    ["user-2", "alias-2"],
                    ["user-3", "alias-3"],
                ],
            ).status_code
            == 200
        )


def test_remove_all_users_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"tenantId": TEST_TENANT_ID, "ruleId": TEST_RULE_ID}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/remove-all-users", method="POST", json=data
    ).respond_with_data()

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        assert c.alert_rules.v1.remove_all_users(TEST_RULE_ID).status_code == 200


def test_get_users_returns_expected_data(httpserver_auth: HTTPServer):
    data = {
        "users": [TEST_RULE_USER_1, TEST_RULE_USER_2],
        "usersToAlertOn": "ALL_USERS",
    }

    request = {"tenantId": TEST_TENANT_ID, "ruleId": TEST_RULE_ID}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/query-users", method="POST", json=request
    ).respond_with_json(data)

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        response = c.alert_rules.v1.get_users(TEST_RULE_ID)
        assert isinstance(response, AssignedUsersList)
        assert response.users_to_alert_on == "ALL_USERS"
        assert response.users[0].json() == json.dumps(TEST_RULE_USER_1)
        assert response.users[1].json() == json.dumps(TEST_RULE_USER_2)


# TODO
def test_get_details_cloud_share_permissions_rules_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"rules": [TEST_CLOUD_SHARE_PERMS_RULE]}
    request = {"tenantId": TEST_TENANT_ID, "ruleIds": []}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/query-cloud-share-permissions-rule",
        method="POST",
        json=request,
    ).respond_with_json(data)

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        c.alert_rules.v1.get_details_cloud_share_permissions_rules(rule_ids=[])


# TODO
def test_get_details_endpoint_exfiltration_rules_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"rules": [TEST_ENDPOINT_EXFIL_RULE]}
    request = {"tenantId": TEST_TENANT_ID, "ruleIds": []}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/query-endpoint-exfiltration-rule",
        method="POST",
        json=request,
    ).respond_with_json(data)

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        c.alert_rules.v1.get_details_endpoint_exfiltration_rules(rule_ids=[])


# TODO
def test_get_details_file_type_mismatch_rules_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"rules": [TEST_FILE_TYPE_MISMATCH_RULE]}
    request = {"tenantId": TEST_TENANT_ID, "ruleIds": []}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/query-file-rule-type-mismatch-rule",
        method="POST",
        json=request,
    ).respond_with_json(data)

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        c.alert_rules.v1.get_details_file_type_mismatch_rules(rule_ids=[])


# TODO
def test_get_details_file_name_rules_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"rules": [TEST_FILE_NAME_RULE]}
    request = {"tenantId": TEST_TENANT_ID, "ruleIds": []}
    httpserver_auth.expect_request(
        uri="/v1/alert-rules/query-file-name-rule", method="POST", json=request
    ).respond_with_json(data)

    with mock.patch(
        "incydr._core.client.Client.tenant_id", new_callable=PropertyMock
    ) as mock_tenant_id:
        mock_tenant_id.return_value = TEST_TENANT_ID
        c = Client()
        c.alert_rules.v1.get_details_file_name_rules(rule_ids=[])
