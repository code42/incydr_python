import datetime
import json
from copy import copy

import pytest
from pydantic import ValidationError
from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._cases.models import Case
from incydr._cases.models import CaseDetail
from incydr._cases.models import CasesPage
from incydr.cli.main import incydr

TEST_CASE_NUMBER = 42

TEST_CASE_1 = {
    "number": 1,
    "name": "test_1",
    "createdAt": "2022-07-18T16:39:51.356082Z",
    "updatedAt": "2022-07-18T16:40:53.335018Z",
    "subject": None,
    "subjectUsername": None,
    "status": "OPEN",
    "assignee": None,
    "assigneeUsername": None,
    "createdByUserUid": None,
    "createdByUsername": None,
    "lastModifiedByUserUid": None,
    "lastModifiedByUsername": None,
    "archivalTime": "2023-07-18T00:00:00Z",
    "description": "description_1",
    "findings": None,
}

TEST_CASE_2 = {
    "number": 2,
    "name": "test_2",
    "createdAt": "2022-07-01T16:39:51.356082Z",
    "updatedAt": "2022-07-01T17:04:16.454497Z",
    "subject": "945056771151950748",
    "subjectUsername": "subject@example.com",
    "status": "OPEN",
    "assignee": "942564422882759874",
    "assigneeUsername": "assignee@example.com",
    "createdByUserUid": None,
    "createdByUsername": None,
    "lastModifiedByUserUid": "942564422882759874",
    "lastModifiedByUsername": "admin@example.com",
    "archivalTime": "2023-07-18T00:00:00Z",
    "description": "description_2",
    "findings": "## Title\n\n- item a\n- item b\n\n**Bolded**\n_Italicized_",
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
    case = c.cases.v1.create(**test_data)
    assert isinstance(case, Case)
    assert case.name == test_data["name"]
    assert case.description == test_data["description"]


def test_create_raises_validation_error_when_param_constraint_exceeded(
    httpserver_auth: HTTPServer,
):
    c = Client()
    # `name` has max of 50 chars
    with pytest.raises(ValidationError):
        c.cases.v1.create(name="x" * 51)

    # `description` has max of 250 chars
    with pytest.raises(ValidationError):
        c.cases.v1.create(name="x", description="x" * 251)

    # `findings` has max of 30k chars
    with pytest.raises(ValidationError):
        c.cases.v1.create(name="x", findings="x" * 30_001)

def test_get_single_case(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/cases/2").respond_with_json(TEST_CASE_2)
    c = Client()
    case = c.cases.v1.get_case(2)
    assert isinstance(case, CaseDetail)
    assert case.number == 2
    assert case.created_at == datetime.datetime.fromisoformat(
        TEST_CASE_2["createdAt"].replace("Z", "+00:00")
    )
    assert case.json() == json.dumps(TEST_CASE_2)


def test_get_page(httpserver_auth: HTTPServer):
    slim_1 = copy(TEST_CASE_1)
    del slim_1["description"]
    del slim_1["findings"]
    slim_2 = copy(TEST_CASE_2)
    del slim_2["description"]
    del slim_2["findings"]
    cases_data = {
        "cases": [
            slim_1,
            slim_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request("/v1/cases").respond_with_json(cases_data)

    client = Client()
    page = client.cases.v1.get_page()
    assert isinstance(page, CasesPage)
    assert page.cases[0].json() == json.dumps(slim_1)
    assert page.cases[1].json() == json.dumps(slim_2)
    assert page.total_count == len(page.cases)

# ************************************************ CLI ************************************************


def test_create_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
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

    result = runner.invoke(
        incydr, ["cases", "create", "test_name", "--description", "test_description",
                 "--subject", "test_subject", "--assignee", "test_assignee", "--findings", "test_findings"]
    )
    assert result.exit_code == 0
    

def test_delete_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    result = runner.invoke(
        incydr, ["cases", "delete", TEST_CASE_NUMBER]
    )
    pass

def test_list_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    result = runner.invoke(incydr, ["cases", "list"])
    pass

def test_show_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    result = runner.invoke(
        incydr, ["cases", "show", TEST_CASE_NUMBER]
    )
    pass

def test_bulk_update_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_download_summary_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_download_cases_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_download_events_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_download_source_file_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_show_file_event_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_list_file_events_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_file_events_add_when_event_ids_list_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_file_events_add_when_csv_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_file_events_remove_when_event_ids_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass

def test_file_events_remove_when_csv_makes_expected_sdk_call(runner, httpserver_auth: HTTPServer):
    pass
