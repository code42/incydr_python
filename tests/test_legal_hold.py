import json
from datetime import datetime
from typing import List
from urllib.parse import urlencode

from pytest_httpserver import HTTPServer

from incydr._core.client import Client
from incydr._legal_hold.models import Custodian
from incydr._legal_hold.models import CustodianMembership
from incydr._legal_hold.models import Matter
from incydr._legal_hold.models import MatterMembership
from incydr._legal_hold.models import Policy
from incydr._legal_hold.models import ReactivateMatterResponse

TEST_USER_ID = "test-user-1"
TEST_MATTER_ID = "test-matter-1"
TEST_POLICY_ID = "test-policy-1"

TEST_POLICY_1 = {
    "policyId": TEST_POLICY_ID,
    "name": "Policy 1",
    "creatorUser": {"userId": TEST_USER_ID, "username": "foo@bar.com"},
    "creatorPrincipal": {
        "type": "principal-type",
        "principalId": "12345",
        "displayName": "Principal Name",
    },
    "creationDate": "2022-07-01T16:39:51.356082Z",
    "modificationDate": "2022-07-01T17:04:16.454497Z",
}
TEST_POLICY_2 = {
    "policyId": "test-policy-2",
    "name": "Policy 2",
    "creatorUser": {"userId": "test-user-2", "username": "bar@foo.com"},
    "creatorPrincipal": {
        "type": "principal-test",
        "principalId": "12345678",
        "displayName": "Test Name",
    },
    "creationDate": "2022-08-01T16:39:51.356082Z",
    "modificationDate": "2022-08-01T17:04:16.454497Z",
}
TEST_MATTER_1 = {
    "matterId": TEST_MATTER_ID,
    "name": "Test Matter 1",
    "description": "test matter",
    "notes": None,
    "active": True,
    "creationDate": "2022-07-01T16:39:51.356082Z",
    "lastModifiedDate": "2022-07-01T17:04:16.454497Z",
    "creatorObject": None,
    "creatorPrincipal": {
        "type": "principal-test",
        "principalId": "12345",
        "displayName": "Test Name",
    },
    "policyId": TEST_POLICY_ID,
}
TEST_MATTER_2 = {
    "matterId": "test-matter-2",
    "name": "Test Matter 2",
    "description": "test matter 2",
    "notes": "additional notes.",
    "active": False,
    "creationDate": "2022-08-01T16:39:51.356082Z",
    "lastModifiedDate": "2022-08-01T17:04:16.454497Z",
    "creatorObject": None,
    "creatorPrincipal": {
        "type": "principal-test",
        "principalId": "12345678",
        "displayName": "Test Name",
    },
    "policyId": "test-policy-2",
}
TEST_CUSTODIAN_1 = {
    "membershipActive": True,
    "membershipCreationDate": "2022-07-01T16:39:51.356082Z",
    "userId": TEST_USER_ID,
    "username": "foo",
    "email": "foo@bar.com",
}
TEST_CUSTODIAN_2 = {
    "membershipActive": True,
    "membershipCreationDate": "2022-03-01T16:39:51.356082Z",
    "userId": "test-user-2",
    "username": "baz",
    "email": "baz@bar.com",
}


def test_list_policies_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"policies": [TEST_POLICY_1, TEST_POLICY_2]}
    httpserver_auth.expect_request(
        "/v1/legal-hold/policies", method="GET"
    ).respond_with_json(data)
    c = Client()
    page = c.legal_hold.v1.list_policies()
    assert isinstance(page, List)
    assert isinstance(page[0], Policy)
    assert isinstance(page[1], Policy)
    assert page[0].json() == json.dumps(TEST_POLICY_1)
    assert page[1].json() == json.dumps(TEST_POLICY_2)


def test_get_policy_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/policies/{TEST_POLICY_ID}", method="GET"
    ).respond_with_json(TEST_POLICY_1)
    c = Client()
    policy = c.legal_hold.v1.get_policy(TEST_POLICY_ID)

    assert isinstance(policy, Policy)
    assert policy.policy_id == TEST_POLICY_ID
    assert policy.json() == json.dumps(TEST_POLICY_1)

    # test timestamp datetime conversion
    assert policy.creation_date == datetime.fromisoformat(
        TEST_POLICY_1["creationDate"].replace("Z", "+00:00")
    )
    assert policy.modification_date == datetime.fromisoformat(
        TEST_POLICY_1["modificationDate"].replace("Z", "+00:00")
    )


def test_get_page_matters_when_custom_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"matters": [TEST_MATTER_1, TEST_MATTER_2]}
    query = {
        "creatorUserId": TEST_USER_ID,
        "active": True,
        "name": "Test",
        "page": 2,
        "pageSize": 2,
    }
    httpserver_auth.expect_request(
        "/v1/legal-hold/matters",
        method="GET",
        query_string=urlencode(query, doseq=True),
    ).respond_with_json(data)
    c = Client()
    page = c.legal_hold.v1.get_page_matters(
        user_id=TEST_USER_ID, active=True, name="Test", page_num=2, page_size=2
    )
    assert isinstance(page, List)
    assert isinstance(page[0], Matter)
    assert isinstance(page[1], Matter)
    assert page[0].json() == json.dumps(TEST_MATTER_1)
    assert page[1].json() == json.dumps(TEST_MATTER_2)


def test_get_page_matters_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    data = {"matters": [TEST_MATTER_1, TEST_MATTER_2]}
    query = {"page": 1, "pageSize": 100}
    httpserver_auth.expect_request(
        "/v1/legal-hold/matters",
        method="GET",
        query_string=urlencode(query, doseq=True),
    ).respond_with_json(data)
    c = Client()
    page = c.legal_hold.v1.get_page_matters()
    assert isinstance(page, List)
    assert isinstance(page[0], Matter)
    assert isinstance(page[1], Matter)
    assert page[0].json() == json.dumps(TEST_MATTER_1)
    assert page[1].json() == json.dumps(TEST_MATTER_2)


def test_iter_all_matters_returns_expected_data(httpserver_auth: HTTPServer):
    query_1 = {
        "creatorUserId": TEST_USER_ID,
        "active": True,
        "name": "test",
        "page": 1,
        "pageSize": 2,
    }
    query_2 = {
        "creatorUserId": TEST_USER_ID,
        "active": True,
        "name": "test",
        "page": 2,
        "pageSize": 2,
    }

    data_1 = {"matters": [TEST_MATTER_1, TEST_MATTER_2]}
    data_2 = {"matters": []}

    httpserver_auth.expect_ordered_request(
        "/v1/legal-hold/matters", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/legal-hold/matters", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(data_2)

    client = Client()
    iterator = client.legal_hold.v1.iter_all_matters(
        user_id=TEST_USER_ID, active=True, name="test", page_size=2
    )
    total = 0
    expected = [TEST_MATTER_1, TEST_MATTER_2]
    for item in iterator:
        total += 1
        assert isinstance(item, Matter)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 2


def test_create_matter_returns_expected_data(httpserver_auth: HTTPServer):
    data = {
        "policyId": TEST_POLICY_ID,
        "name": "Test Matter 1",
        "description": "test matter",
        "notes": "test",
    }
    httpserver_auth.expect_request(
        uri="/v1/legal-hold/matters", method="POST", json=data
    ).respond_with_json(TEST_MATTER_1)
    c = Client()
    matter = c.legal_hold.v1.create_matter(
        TEST_POLICY_ID, "Test Matter 1", description="test matter", notes="test"
    )
    assert isinstance(matter, Matter)
    assert matter.matter_id == TEST_MATTER_ID
    assert matter.json() == json.dumps(TEST_MATTER_1)

    # test timestamp datetime conversion
    assert matter.creation_date == datetime.fromisoformat(
        TEST_MATTER_1["creationDate"].replace("Z", "+00:00")
    )
    assert matter.last_modified_date == datetime.fromisoformat(
        TEST_MATTER_1["lastModifiedDate"].replace("Z", "+00:00")
    )


def test_get_matter_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}", method="GET"
    ).respond_with_json(TEST_MATTER_1)
    c = Client()
    matter = c.legal_hold.v1.get_matter(TEST_MATTER_ID)
    assert isinstance(matter, Matter)
    assert matter.matter_id == TEST_MATTER_ID
    assert matter.json() == json.dumps(TEST_MATTER_1)

    # test timestamp datetime conversion
    assert matter.creation_date == datetime.fromisoformat(
        TEST_MATTER_1["creationDate"].replace("Z", "+00:00")
    )
    assert matter.last_modified_date == datetime.fromisoformat(
        TEST_MATTER_1["lastModifiedDate"].replace("Z", "+00:00")
    )


def test_deactivate_matter_makes_expected_call(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/legal-hold/matters/{TEST_MATTER_ID}/deactivate", method="POST"
    ).respond_with_data()
    c = Client()
    assert c.legal_hold.v1.deactivate_matter(TEST_MATTER_ID).status_code == 200


def test_reactivate_matter_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/legal-hold/matters/{TEST_MATTER_ID}/reactivate", method="POST"
    ).respond_with_json({"membershipsChanged": True})
    c = Client()
    response = c.legal_hold.v1.reactivate_matter(TEST_MATTER_ID)
    assert isinstance(response, ReactivateMatterResponse)
    assert response.memberships_changed


def test_get_page_custodians_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"custodians": [TEST_CUSTODIAN_1, TEST_CUSTODIAN_2]}
    query = {"page": 1, "pageSize": 2}
    httpserver_auth.expect_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(data)
    c = Client()
    custodians = c.legal_hold.v1.get_page_custodians(
        TEST_MATTER_ID, page_num=1, page_size=2
    )
    assert isinstance(custodians, List)
    assert isinstance(custodians[0], Custodian)
    assert isinstance(custodians[1], Custodian)
    assert custodians[0].json() == json.dumps(TEST_CUSTODIAN_1)
    assert custodians[1].json() == json.dumps(TEST_CUSTODIAN_2)


def test_iter_all_custodians_returns_expected_data(httpserver_auth: HTTPServer):
    query_1 = {
        "page": 1,
        "pageSize": 2,
    }
    query_2 = {"page": 2, "pageSize": 2}

    data_1 = {"custodians": [TEST_CUSTODIAN_1, TEST_CUSTODIAN_2]}
    data_2 = {"custodians": []}

    httpserver_auth.expect_ordered_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians",
        method="GET",
        query_string=urlencode(query_1),
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians",
        method="GET",
        query_string=urlencode(query_2),
    ).respond_with_json(data_2)

    client = Client()
    iterator = client.legal_hold.v1.iter_all_custodians(
        matter_id=TEST_MATTER_ID, page_size=2
    )
    total = 0
    expected = [TEST_CUSTODIAN_1, TEST_CUSTODIAN_2]
    for item in iterator:
        total += 1
        assert isinstance(item, Custodian)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 2


def test_add_user_to_matter_returns_expected_data(httpserver_auth: HTTPServer):
    test_membership = {
        "membershipActive": True,
        "membershipCreationDate": "2022-05-01T16:39:51.356082Z",
        "matter": {"matterId": "string", "name": "string"},
        "custodian": {"userId": "string", "username": "string", "email": "string"},
    }

    httpserver_auth.expect_request(
        uri=f"/v1/legal-hold/matters/{TEST_MATTER_ID}/custodians",
        method="POST",
        json={"userId": TEST_USER_ID},
    ).respond_with_json(test_membership)
    c = Client()
    membership = c.legal_hold.v1.add_user_to_matter(TEST_MATTER_ID, TEST_USER_ID)
    assert isinstance(membership, MatterMembership)
    assert membership.json() == json.dumps(test_membership)

    # test timestamp datetime conversion
    assert membership.membership_creation_date == datetime.fromisoformat(
        test_membership["membershipCreationDate"].replace("Z", "+00:00")
    )


def test_list_matters_for_user_returns_expected_data(httpserver_auth: HTTPServer):
    membership = {
        "membershipActive": True,
        "membershipCreationDate": "2022-05-01T16:39:51.356082Z",
        "matterId": TEST_MATTER_ID,
        "name": "Test Matter 1",
    }
    data = {"matters": [membership]}
    query = {"page": 1, "pageSize": 2}
    httpserver_auth.expect_request(
        f"/v1/legal-hold/custodians/{TEST_USER_ID}",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(data)
    c = Client()
    matters = c.legal_hold.v1.list_matters_for_user(
        user_id=TEST_USER_ID, page_num=1, page_size=2
    )
    assert isinstance(matters, List)
    assert isinstance(matters[0], CustodianMembership)
    assert matters[0].json() == json.dumps(membership)
