import datetime
import json

import pytest
from pydantic import ValidationError
from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._cases.models import Case, CasesPage

TEST_CASE_1 = {
    "number": 1,
    "name": "test_1",
    "createdAt": "2022-07-18T16:39:51.356082Z",
    "updatedAt": "2022-07-18T16:40:53.335018Z",
    "description": "description_1",
    "findings": None,
    "subject": None,
    "subjectUsername": None,
    "status": "OPEN",
    "assignee": None,
    "assigneeUsername": None,
    "createdByUserUid": None,
    "createdByUsername": None,
    "lastModifiedByUserUid": None,
    "lastModifiedByUsername": None,
}

TEST_CASE_2 = {
    "number": 2,
    "name": "test_2",
    "createdAt": "2022-07-01T16:39:51.356082Z",
    "updatedAt": "2022-07-01T17:04:16.454497Z",
    "description": "description_2",
    "findings": "## Title\n\n- item a\n- item b\n\n**Bolded**\n_Italicized_",
    "subject": "945056771151950748",
    "subjectUsername": "subject@example.com",
    "status": "OPEN",
    "assignee": "942564422882759874",
    "assigneeUsername": "assignee@example.com",
    "createdByUserUid": None,
    "createdByUsername": None,
    "lastModifiedByUserUid": "942564422882759874",
    "lastModifiedByUsername": "admin@example.com",
}


def test_create(httpserver_auth: HTTPServer):
    test_data = {
        "name": "test_name",
        "description": "test_description",
        "subject": "test_subject",
        "assignee": "test_assignee",
        "findings": "test_findings",
    }
    test_response = TEST_CASE_1.copy()
    test_response.update(test_data)
    httpserver_auth.expect_request(
        uri="/v1/cases", method="POST", json=test_data
    ).respond_with_json(test_response)
    c = Client()
    case = c.cases.create(**test_data)
    assert isinstance(case, Case)
    assert case.name == test_data["name"]
    assert case.description == test_data["description"]


def test_create_raises_validation_error_when_param_constraint_exceeded(
    httpserver_auth: HTTPServer,
):
    c = Client()
    # `name` has max of 50 chars
    with pytest.raises(ValidationError):
        c.cases.create(name="x" * 51)

    # `description` has max of 250 chars
    with pytest.raises(ValidationError):
        c.cases.create(name="x", description="x" * 251)

    # `findings` has max of 30k chars
    with pytest.raises(ValidationError):
        c.cases.create(name="x", findings="x" * 30_001)


def test_get_by_id(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/cases/2").respond_with_json(TEST_CASE_2)
    c = Client()
    case = c.cases.get_by_id(2)
    assert isinstance(case, Case)
    assert case.number == 2
    assert case.created_at == datetime.datetime.fromisoformat(
        TEST_CASE_2["createdAt"].replace("Z", "+00:00")
    )
    assert case.json() == json.dumps(TEST_CASE_2)


def test_get_page(httpserver_auth: HTTPServer):
    cases_data = {
        "cases": [
            TEST_CASE_1,
            TEST_CASE_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request("/v1/cases").respond_with_json(cases_data)

    client = Client()
    page = client.cases.get_page()
    assert isinstance(page, CasesPage)
    assert page.cases[0].json() == json.dumps(TEST_CASE_1)
    assert page.cases[1].json() == json.dumps(TEST_CASE_2)
    assert page.total_count == len(page.cases)
