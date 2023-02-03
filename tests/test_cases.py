import datetime
import json
from copy import copy
from urllib.parse import urlencode

import pytest
from pydantic import ValidationError
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.cases.models import Case
from _incydr_sdk.cases.models import CaseDetail
from _incydr_sdk.cases.models import CaseFileEvents
from _incydr_sdk.cases.models import CasesPage
from _incydr_sdk.cases.models import FileEvent
from _incydr_sdk.file_events.models.event import FileEventV2
from incydr import Client
from tests.test_file_events import TEST_EVENT_1
from tests.test_users import TEST_USER_1
from tests.test_users import TEST_USER_2

TEST_CASE_NUMBER = "42"

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
    "number": 42,
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


@pytest.fixture
def mock_case_delete(httpserver_auth):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}", method="DELETE"
    ).respond_with_data()


@pytest.fixture
def mock_case_get(httpserver_auth):
    httpserver_auth.expect_request(f"/v1/cases/{TEST_CASE_NUMBER}").respond_with_json(
        TEST_CASE_2
    )


@pytest.fixture
def mock_file_event_get(httpserver_auth):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{TEST_EVENT_ID}", method="GET"
    ).respond_with_json(TEST_EVENT_1)


@pytest.fixture
def mock_user_lookup(httpserver_auth):
    query_1 = {
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }
    query_2 = {
        "username": "baz@bar.com",
        "page": 1,
        "pageSize": 100,
    }
    data_1 = {"users": [TEST_USER_1], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    data_2 = {"users": [TEST_USER_2], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/users", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(data_2)
    httpserver_auth.expect_request("/v1/oauth", method="POST").respond_with_json(
        dict(
            token_type="bearer",
            expires_in=900,
            access_token="abcd-1234",
        )
    )


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
    assert isinstance(case, CaseDetail)
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


def test_get_single_case(mock_case_get):
    c = Client()
    case = c.cases.v1.get_case(TEST_CASE_NUMBER)
    assert isinstance(case, CaseDetail)
    assert case.number == 42
    assert case.created_at == datetime.datetime.fromisoformat(
        TEST_CASE_2["createdAt"].replace("Z", "+00:00")
    )
    assert case.json() == json.dumps(TEST_CASE_2)


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    slim_1 = copy(TEST_CASE_1)
    del slim_1["description"]
    del slim_1["findings"]
    slim_2 = copy(TEST_CASE_2)
    del slim_2["description"]
    del slim_2["findings"]

    query = {"pgNum": 1, "pgSize": 15, "srtDir": "asc", "srtKey": "number"}
    cases_data = {
        "cases": [
            slim_1,
            slim_2,
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
    assert page.cases[0].json() == json.dumps(slim_1)
    assert page.cases[1].json() == json.dumps(slim_2)
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


def test_delete_makes_expected_api_call(mock_case_delete):
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
        assert json.loads(item.json()) == expected.pop(0)
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
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{TEST_EVENT_ID}/file", method="GET"
    ).respond_with_json(data)
    c = Client()
    c.cases.v1.download_file_for_event(TEST_CASE_NUMBER, TEST_EVENT_ID, tmp_path)
    f1 = tmp_path / f"Case-{TEST_CASE_NUMBER}-{TEST_EVENT_ID}-unknown-filename"
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


def test_get_file_event_detail_returns_expected_data(mock_file_event_get):
    c = Client()
    event = c.cases.v1.get_file_event_detail(TEST_CASE_NUMBER, TEST_EVENT_ID)
    assert isinstance(event, FileEventV2)


# ************************************************ CLI ************************************************


def test_cli_create_makes_expected_call(runner, httpserver_auth: HTTPServer):
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
        incydr,
        [
            "cases",
            "create",
            "test_name",
            "--description",
            "test_description",
            "--subject",
            "test_subject",
            "--assignee",
            "test_assignee",
            "--findings",
            "test_findings",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_create_when_usernames_specified_performs_additional_lookup_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_user_lookup
):
    test_data = {
        "name": "test_name",
        "description": "test_description",
        "subject": "user-1",
        "assignee": "user-2",
        "findings": "test_findings",
    }
    test_response = TEST_CASE_1.copy()
    test_response.update(test_data)
    httpserver_auth.expect_request(
        uri="/v1/cases", method="POST", json=test_data
    ).respond_with_json(test_response)

    result = runner.invoke(
        incydr,
        [
            "cases",
            "create",
            "test_name",
            "--description",
            "test_description",
            "--subject",
            "foo@bar.com",
            "--assignee",
            "baz@bar.com",
            "--findings",
            "test_findings",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_delete_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_case_delete
):
    result = runner.invoke(incydr, ["cases", "delete", TEST_CASE_NUMBER])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_makes_expected_call(runner, httpserver_auth: HTTPServer):
    query_1 = {"pgNum": 1, "pgSize": 100, "srtDir": "asc", "srtKey": "number"}
    data_1 = {"cases": [TEST_CASE_1, TEST_CASE_2], "totalCount": 3}
    httpserver_auth.expect_ordered_request(
        "/v1/cases", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    result = runner.invoke(incydr, ["cases", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_case_get
):
    result = runner.invoke(incydr, ["cases", "show", TEST_CASE_NUMBER])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_update_when_no_params_raises_error(runner, httpserver_auth: HTTPServer):
    result = runner.invoke(incydr, ["cases", "update", TEST_CASE_NUMBER])
    assert result.exit_code == 2
    assert (
        "At least one command option must be provided to update a case."
        in result.output
    )


def test_cli_update_when_all_params_makes_expected_call(
    runner, httpserver_auth: HTTPServer
):
    test_case = {
        "number": TEST_CASE_NUMBER,
        "name": "orig-name",
        "assignee": "orig-assignee",
        "description": "orig-description",
        "findings": "orig-finding",
        "subject": "orig-subject",
        "status": "OPEN",
    }
    data = {
        "name": "TestCase",
        "assignee": "test-assignee",
        "description": "test-desc",
        "findings": "test-finding",
        "subject": "test-subject",
        "status": "CLOSED",
    }
    updated_case = test_case.copy()
    updated_case["status"] = "CLOSED"
    updated_case["assignee"] = "test-assignee"
    updated_case["subject"] = "test-subject"
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}", method="GET"
    ).respond_with_json(test_case)
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}", method="PUT", json=data
    ).respond_with_json(updated_case)
    result = runner.invoke(
        incydr,
        [
            "cases",
            "update",
            TEST_CASE_NUMBER,
            "--assignee",
            "test-assignee",
            "--description",
            "test-desc",
            "--findings",
            "test-finding",
            "--name",
            "TestCase",
            "--status",
            "CLOSED",
            "--subject",
            "test-subject",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_update_when_usernames_specified_performs_additional_lookup_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_user_lookup
):
    test_case = {
        "number": 42,
        "name": "test",
        "description": None,
        "assignee": "user-a",
        "subject": "user-b",
        "findings": None,
        "status": "OPEN",
    }
    test_data = {
        "name": "test",
        "assignee": "user-2",
        "description": None,
        "findings": None,
        "subject": "user-1",
        "status": "OPEN",
    }
    test_updated_case = test_case.copy()
    test_updated_case["assignee"] = "user-2"
    test_updated_case["subject"] = "user-1"

    httpserver_auth.expect_request(
        uri=f"/v1/cases/{TEST_CASE_NUMBER}", method="GET"
    ).respond_with_json(test_case)
    httpserver_auth.expect_request(
        uri=f"/v1/cases/{TEST_CASE_NUMBER}", method="PUT", json=test_data
    ).respond_with_json(test_updated_case)

    result = runner.invoke(
        incydr,
        [
            "cases",
            "update",
            TEST_CASE_NUMBER,
            "--subject",
            "foo@bar.com",
            "--assignee",
            "baz@bar.com",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_update_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    update_1 = {
        "name": "Test Case 1",
        "assignee": "new-user",
        "description": "updated-1",
        "findings": "updated-findings",
        "subject": "user-2",
        "status": "OPEN",
    }
    update_2 = {
        "name": "Test Case 2",
        "assignee": "user-3",
        "description": "updated-2",
        "findings": "updated-findings",
        "subject": "user-4",
        "status": "CLOSED",
    }
    httpserver_auth.expect_request("/v1/cases/1", method="GET").respond_with_json(
        TEST_CASE_1
    )
    httpserver_auth.expect_request("/v1/cases/42", method="GET").respond_with_json(
        TEST_CASE_2
    )
    httpserver_auth.expect_request(
        "/v1/cases/1", method="PUT", json=update_1
    ).respond_with_json(TEST_CASE_1)
    httpserver_auth.expect_request(
        "/v1/cases/42", method="PUT", json=update_2
    ).respond_with_json(TEST_CASE_2)

    p = tmp_path / "@cases.csv"
    p.write_text(
        "number,assignee,description,findings,name,status,subject\n"
        f"1,{update_1['assignee']},{update_1['description']},{update_1['findings']},{update_1['name']},{update_1['status']},{update_1['subject']}\n"
        f"42,{update_2['assignee']},{update_2['description']},{update_2['findings']},{update_2['name']},{update_2['status']},{update_2['subject']}"
    )

    result = runner.invoke(incydr, ["cases", "bulk-update", str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_update_when_usernames_makes_user_lookup(
    httpserver_auth: HTTPServer, mock_user_lookup, runner, tmp_path
):
    data_1 = {
        "name": "Test Case 1",
        "assignee": "user-1",
        "description": "test case 1",
        "findings": "no findings",
        "subject": "user-2",
        "status": "OPEN",
    }
    httpserver_auth.expect_request("/v1/cases/1", method="GET").respond_with_json(
        TEST_CASE_1
    )
    httpserver_auth.expect_request(
        "/v1/cases/1", method="PUT", json=data_1
    ).respond_with_json(TEST_CASE_1)

    p = tmp_path / "cases.csv"
    p.write_text(
        "number,assignee,description,findings,name,status,subject\n"
        "1,foo@bar.com,test case 1,no findings,Test Case 1,OPEN,baz@bar.com\n"
    )

    result = runner.invoke(incydr, ["cases", "bulk-update", str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_update_when_multiple_same_usernames_makes_single_user_lookup_and_caches_id(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    query_1 = {
        "username": "foo@bar.com",
        "page": 1,
        "pageSize": 100,
    }
    data_1 = {"users": [TEST_USER_1], "totalCount": 1}
    httpserver_auth.expect_request("/v1/cases/1", method="GET").respond_with_json(
        TEST_CASE_1
    )
    httpserver_auth.expect_oneshot_request(
        "/v1/users", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(data_1)

    httpserver_auth.expect_request("/v1/oauth", method="POST").respond_with_json(
        dict(
            token_type="bearer",
            expires_in=900,
            access_token="abcd-1234",
        )
    )

    data_1 = {
        "name": "Test Case 1",
        "assignee": "user-1",
        "description": "test case 1",
        "findings": "no findings",
        "subject": "user-1",
        "status": "OPEN",
    }

    httpserver_auth.expect_request(
        "/v1/cases/1", method="PUT", json=data_1
    ).respond_with_json(TEST_CASE_1)

    p = tmp_path / "cases.csv"
    p.write_text(
        "number,assignee,description,findings,name,status,subject\n"
        "1,foo@bar.com,test case 1,no findings,Test Case 1,OPEN,foo@bar.com\n"
    )

    result = runner.invoke(incydr, ["cases", "bulk-update", str(p)])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_download_summary_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/export", method="GET"
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        ["cases", "download", TEST_CASE_NUMBER, "--path", str(tmp_path), "--summary"],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_download_case_when_default_params_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    params = {
        "files": True,
        "summary": True,
        "fileEvents": True,
    }
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/export/full",
        method="GET",
        query_string=urlencode(params),
    ).respond_with_data()
    result = runner.invoke(
        incydr, ["cases", "download", TEST_CASE_NUMBER, "--path", str(tmp_path)]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_download_case_when_custom_params_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    params = {
        "files": True,
        "summary": True,
        "fileEvents": False,
    }
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/export/full",
        method="GET",
        query_string=urlencode(params),
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "cases",
            "download",
            TEST_CASE_NUMBER,
            "--path",
            str(tmp_path),
            "--source-files",
            "--summary",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_download_events_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/export", method="GET"
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "cases",
            "download",
            TEST_CASE_NUMBER,
            "--path",
            str(tmp_path),
            "--file-events",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_download_source_file_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/{TEST_EVENT_ID}/file", method="GET"
    ).respond_with_data()

    result = runner.invoke(
        incydr,
        [
            "cases",
            "download",
            TEST_CASE_NUMBER,
            "--source-file",
            TEST_EVENT_ID,
            "--path",
            str(tmp_path),
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_file_event_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_file_event_get
):
    result = runner.invoke(
        incydr, ["cases", "file-events", "show", TEST_CASE_NUMBER, TEST_EVENT_ID]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_file_events_makes_expected_call(runner, httpserver_auth: HTTPServer):
    data = {"events": [TEST_FILE_EVENT], "totalCount": 1}
    query = {"pgNum": 1, "pgSize": 100}
    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent",
        method="GET",
        query_string=urlencode(query),
    ).respond_with_json(data)
    result = runner.invoke(incydr, ["cases", "file-events", "list", TEST_CASE_NUMBER])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_add_when_event_ids_list_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    event_ids = ["event-1", "event-2", "event-3"]

    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent",
        method="POST",
        json={"events": event_ids},
    ).respond_with_data()
    result = runner.invoke(
        incydr, ["cases", "file-events", "add", TEST_CASE_NUMBER, ",".join(event_ids)]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_add_when_csv_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    event_ids = ["event-1", "event-2", "event-3"]
    p = tmp_path / "event_ids.csv"
    p.write_text("event_id\n" + "\n".join(event_ids))

    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent",
        method="POST",
        json={"events": event_ids},
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        ["cases", "file-events", "add", TEST_CASE_NUMBER, f"@{p}", "--format", "csv"],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_add_when_jsonlines_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    event_ids = ["event-1", "event-2", "event-3"]
    p = tmp_path / "event_ids.json"
    p.write_text(
        """{"event_id": "event-1"}\n{"eventId": "event-2"}\n{"event": {"id": "event-3"}}"""
    )

    httpserver_auth.expect_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent",
        method="POST",
        json={"events": event_ids},
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "cases",
            "file-events",
            "add",
            TEST_CASE_NUMBER,
            f"@{p}",
            "--format",
            "json-lines",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_remove_when_event_ids_makes_expected_call(
    runner, httpserver_auth: HTTPServer
):
    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-1",
        method="DELETE",
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-2",
        method="DELETE",
    ).respond_with_data()
    result = runner.invoke(
        incydr, ["cases", "file-events", "remove", TEST_CASE_NUMBER, "event-1,event-2"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_remove_when_csv_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    p = tmp_path / "event_ids.csv"
    p.write_text("event_id\nevent-1\nevent-2")

    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-1",
        method="DELETE",
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-2",
        method="DELETE",
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "cases",
            "file-events",
            "remove",
            TEST_CASE_NUMBER,
            f"@{p}",
            "--format",
            "csv",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_file_events_remove_when_jsonlines_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    p = tmp_path / "event_ids.json"
    p.write_text(
        """{"event_id": "event-1"}\n{"eventId": "event-2"}\n{"event": {"id": "event-3"}}"""
    )

    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-1",
        method="DELETE",
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-2",
        method="DELETE",
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        f"/v1/cases/{TEST_CASE_NUMBER}/fileevent/event-3",
        method="DELETE",
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "cases",
            "file-events",
            "remove",
            TEST_CASE_NUMBER,
            f"@{p}",
            "--format",
            "json-lines",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0
