import datetime
import json
from urllib.parse import urlencode

import pytest
from pydantic import ValidationError
from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._cases.models import Case
from incydr._cases.models import CaseFileEvents
from incydr._cases.models import CasesPage
from incydr._cases.models import FileEvent
from incydr._file_events.models.event import FileEventV2
from tests.test_file_events import TEST_EVENT_1

TEST_CASE_NUMBER = 42

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
    "archivalTime": None,
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
    "archivalTime": None,
}
TEST_EVENT_ID = "0_147e9445-2f30"
TEST_FILE_EVENT = {
    "eventId": TEST_EVENT_ID,
    "eventTimestamp": "2020-12-23T14:24:44.593Z",
    "exposure": ["OutsideTrustedDomains", "IsPublic"],
    "fileAvailability": "EXACT_FILE_AVAILABLE",
    "fileName": "example.txt",
    "filePath": "/Users/test/",
    "riskIndicators": [],
    "riskScore": 8,
    "riskSeverity": "CRITICAL",
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
    assert isinstance(case, Case)
    assert case.number == 2
    assert case.created_at == datetime.datetime.fromisoformat(
        TEST_CASE_2["createdAt"].replace("Z", "+00:00")
    )
    assert case.json() == json.dumps(TEST_CASE_2)


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {"pgNum": 1, "pgSize": 15, "srtDir": "asc", "srtKey": "number"}
    cases_data = {
        "cases": [
            TEST_CASE_1,
            TEST_CASE_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v1/cases",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(cases_data)

    client = Client()
    client.settings.page_size = 15
    page = client.cases.v1.get_page()
    assert isinstance(page, CasesPage)
    assert page.cases[0].json() == json.dumps(TEST_CASE_1)
    assert page.cases[1].json() == json.dumps(TEST_CASE_2)
    assert page.total_count == len(page.cases)


def test_get_page_when_all_params_makes_expected_call(httpserver_auth: HTTPServer):
    query = {
        "assignee": "test-assignee",
        "createdAt": "2022-08-09T00:00:00.000000Z/2022-08-11T00:00:00.000000Z",
        "isAssigned": True,
        "lastModifiedBy": "test-user",
        "name": "test-name",
        "pgNum": 2,
        "pgSize": 10,
        "srtDir": "desc",
        "srtKey": "status",
        "status": "OPEN",
    }
    cases_data = {
        "cases": [
            TEST_CASE_1,
            TEST_CASE_2,
        ],
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v1/cases",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(cases_data)

    client = Client()
    page = client.cases.v1.get_page(
        assignee="test-assignee",
        created_at=(datetime.datetime(2022, 8, 9), datetime.datetime(2022, 8, 11)),
        is_assigned=True,
        last_modified_by="test-user",
        name="test-name",
        page_num=2,
        page_size=10,
        sort_dir="desc",
        sort_key="status",
        status="OPEN",
    )
    assert isinstance(page, CasesPage)


def test_delete_makes_expected_api_call(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}", method="DELETE"
    ).respond_with_data()
    c = Client()
    assert c.cases.v1.delete(TEST_CASE_NUMBER).status_code == 200


def test_iter_all_returns_expected_data(httpserver_auth: HTTPServer):
    query_1 = {"pgNum": 1, "pgSize": 2, "srtDir": "asc", "srtKey": "number"}
    query_2 = {"pgNum": 2, "pgSize": 2, "srtDir": "asc", "srtKey": "number"}

    test_case_3 = TEST_CASE_2.copy()
    test_case_3["number"] = 3
    test_case_3["name"] = "test_3"

    data_1 = {"cases": [TEST_CASE_1, TEST_CASE_2], "totalCount": 2}
    data_2 = {"cases": [test_case_3], "totalCount": 1}

    httpserver_auth.expect_ordered_request(
        "/v1/cases", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/cases", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(data_2)

    client = Client()
    iterator = client.cases.v1.iter_all(page_size=2)
    total = 0
    expected = [TEST_CASE_1, TEST_CASE_2, test_case_3]
    for item in iterator:
        total += 1
        assert isinstance(item, Case)
        assert item.json() == json.dumps(expected.pop(0))
    assert total == 3


def test_update_returns_expected_data(httpserver_auth: HTTPServer):

    test_case = TEST_CASE_1.copy()
    test_case["name"] = "my_renamed_case"
    test_case["number"] = TEST_CASE_NUMBER
    case = Case.parse_obj(test_case)

    data = {
        "name": "my_renamed_case",
        "assignee": None,
        "description": "description_1",
        "findings": None,
        "subject": None,
        "status": "OPEN",
    }

    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}", method="PUT", json=data
    ).respond_with_json(test_case)

    c = Client()
    new_case = c.cases.v1.update(case)
    assert isinstance(new_case, Case)
    assert new_case.name == "my_renamed_case"


def test_download_summary_pdf_returns_expected_data(
    httpserver_auth: HTTPServer, tmp_path
):
    data = "test-case-summary"
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/export", method="GET"
    ).respond_with_json(data)
    c = Client()
    c.cases.v1.download_summary_pdf(TEST_CASE_NUMBER, tmp_path)
    f1 = tmp_path / f"Case-{TEST_CASE_NUMBER}.pdf"
    f = open(f1)
    content = f.read()
    assert content == f'"{data}"'


def test_download_file_event_csv_returns_expected_data(
    httpserver_auth: HTTPServer, tmp_path
):
    data = "test-case-file-events"
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/export", method="GET"
    ).respond_with_json(data)
    c = Client()
    c.cases.v1.download_file_event_csv(TEST_CASE_NUMBER, tmp_path)
    f1 = tmp_path / f"Case-{TEST_CASE_NUMBER}-file-events.csv"
    f = open(f1)
    content = f.read()
    assert content == f'"{data}"'


def test_download_full_case_zip_returns_expected_data(
    httpserver_auth: HTTPServer, tmp_path
):
    # TODO params
    data = "test-full-case-zip"
    params = {
        "files": True,
        "summary": True,
        "fileEvents": True,
    }
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/export/full",
        method="GET",
        query_string=urlencode(params),
    ).respond_with_json(data)
    c = Client()
    c.cases.v1.download_full_case_zip(TEST_CASE_NUMBER, tmp_path)
    f1 = tmp_path / f"Case-{TEST_CASE_NUMBER}.zip"
    f = open(f1)
    content = f.read()
    assert content == f'"{data}"'


def test_download_file_for_event_returns_expected_data(
    httpserver_auth: HTTPServer, tmp_path
):
    data = "test-download-source-file"
    event_id = "TEST-EVENT-ID"
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{event_id}/file", method="GET"
    ).respond_with_json(data)
    c = Client()
    c.cases.v1.download_file_for_event(TEST_CASE_NUMBER, event_id, tmp_path)
    f1 = tmp_path / f"Case-{TEST_CASE_NUMBER}-{event_id}-unknown-filename"
    f = open(f1)
    content = f.read()
    assert content == f'"{data}"'


def test_get_file_events_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"events": [TEST_FILE_EVENT], "totalCount": 1}
    query = {"pgNum": 1, "pgSize": 100}
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(data)
    c = Client()
    events = c.cases.v1.get_file_events(TEST_CASE_NUMBER)
    assert isinstance(events, CaseFileEvents)
    assert isinstance(events.events[0], FileEvent)
    assert events.events[0].event_id == TEST_EVENT_ID
    assert 1 == events.total_count == len(events.events)


def test_add_file_events_to_case_returns_expected_data(httpserver_auth: HTTPServer):
    data = {"events": [TEST_EVENT_ID]}
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent", method="POST", json=data
    ).respond_with_data()
    c = Client()
    assert (
        c.cases.v1.add_file_events_to_case(TEST_CASE_NUMBER, TEST_EVENT_ID).status_code
        == 200
    )


def test_delete_file_events_from_case_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{TEST_EVENT_ID}", method="DELETE"
    ).respond_with_data()
    c = Client()
    assert (
        c.cases.v1.delete_file_event_from_case(
            TEST_CASE_NUMBER, TEST_EVENT_ID
        ).status_code
        == 200
    )


def test_get_file_event_detail_returns_expected_data(httpserver_auth: HTTPServer):
    data = TEST_EVENT_1
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{TEST_EVENT_ID}", method="GET"
    ).respond_with_json(data)
    c = Client()
    event = c.cases.v1.get_file_event_detail(TEST_CASE_NUMBER, TEST_EVENT_ID)
    assert isinstance(event, FileEventV2)
