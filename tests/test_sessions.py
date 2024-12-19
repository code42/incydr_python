import json
from datetime import datetime
from datetime import timezone
from unittest import mock
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.cursor import CursorStore
from _incydr_cli.main import incydr
from _incydr_sdk.core.client import Client
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.sessions import ContentInspectionStatuses
from _incydr_sdk.enums.sessions import SessionStates
from _incydr_sdk.enums.sessions import SortKeys
from _incydr_sdk.file_events.models.response import FileEventsPage
from _incydr_sdk.sessions.models.response import Session
from _incydr_sdk.sessions.models.response import SessionsPage
from tests.test_file_events import TEST_EVENT_1
from tests.test_file_events import TEST_EVENT_2

TEST_SESSION_ID = "123-session-1"
DATETIME_INSTANT = datetime(2024, 1, 1, tzinfo=timezone.utc)
POSIX_TS = int(DATETIME_INSTANT.timestamp()) * 1000
START_DATE = "2024-12-19"
START_TIMESTAMP = 1734566400000  # in ms
END_DATE = "2024-12-20"
END_TIMESTAMP = 1734652800000  # in ms

TEST_SESSION = {
    "actorId": TEST_SESSION_ID,
    "beginTime": POSIX_TS,
    "contentInspectionResults": {
        "eventResults": [
            {"eventId": "event-id", "piiType": ["string"], "status": "PENDING"}
        ],
        "status": "PENDING",
    },
    "contextSummary": "string",
    "criticalEvents": 0,
    "endTime": POSIX_TS,
    "exfiltrationSummary": "string",
    "firstObserved": POSIX_TS,
    "highEvents": 0,
    "lastUpdated": 0,
    "lowEvents": 0,
    "moderateEvents": 0,
    "noRiskEvents": 0,
    "notes": [
        {
            "content": "string",
            "id": "string",
            "sourceTimestamp": POSIX_TS,
            "userId": "string",
        }
    ],
    "riskIndicators": [
        {"eventCount": 0, "id": "string", "name": "string", "weight": 0}
    ],
    "scores": [{"score": 0, "severity": 0, "sourceTimestamp": POSIX_TS}],
    "sessionId": TEST_SESSION_ID,
    "states": [
        {
            "sourceTimestamp": POSIX_TS,
            "state": "OPEN",
            "userId": "string",
        }
    ],
    "tenantId": "string",
    "triggeredAlerts": [
        {"alertId": "alert-id", "lessonId": "lesson-id", "ruleId": "rule-id"}
    ],
    "userId": "string",
}


@pytest.fixture
def mock_get_session(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/sessions/{TEST_SESSION_ID}", method="GET"
    ).respond_with_json(TEST_SESSION)


@pytest.fixture
def mock_get_events(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/sessions/{TEST_SESSION_ID}/events", method="GET"
    ).respond_with_json(
        {
            "queryResult": {
                "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
                "nextPgToken": "",
                "problems": None,
                "totalCount": 2,
            }
        }
    )


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "has_alerts": "true",
        "page_number": 0,
        "page_size": 50,
    }
    sessions_page = {"items": [TEST_SESSION], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query, doseq=True)
    ).respond_with_json(sessions_page)

    client = Client()
    page = client.sessions.v1.get_page()
    assert isinstance(page, SessionsPage)
    assert page.items[0].json() == json.dumps(TEST_SESSION)
    assert len(page.items) == 1 == page.total_count


def test_get_page_when_custom_params_returns_expected_data(httpserver_auth: HTTPServer):
    query = {
        "actor_id": "actor-id",
        "on_or_after": POSIX_TS,
        "before": POSIX_TS,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
        "order_by": "score",
        "sort_direction": "desc",
        "page_number": 2,
        "page_size": 10,
    }
    sessions_page = {"items": [TEST_SESSION], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query, doseq=True)
    ).respond_with_json(sessions_page)

    client = Client()
    page = client.sessions.v1.get_page(
        actor_id="actor-id",
        start_time=POSIX_TS,
        end_time=POSIX_TS,
        has_alerts=False,
        sort_key=SortKeys.SCORE,
        risk_indicators=["risk-indicator"],
        sort_dir=SortDirection.DESC,
        states=SessionStates.OPEN,
        severities=3,
        rule_ids="rule-id",
        watchlist_ids="watchlist-id",
        page_num=2,
        page_size=10,
        content_inspection_status=ContentInspectionStatuses.PENDING,
    )
    assert isinstance(page, SessionsPage)
    assert page.items[0].json() == json.dumps(TEST_SESSION)
    assert len(page.items) == 1 == page.total_count


def test_get_page_when_given_date_uses_correct_timestamp(httpserver_auth: HTTPServer):
    query = {
        "actor_id": "actor-id",
        "on_or_after": START_TIMESTAMP,
        "before": END_TIMESTAMP,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
        "order_by": "score",
        "sort_direction": "desc",
        "page_number": 2,
        "page_size": 10,
    }
    sessions_page = {"items": [TEST_SESSION], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query, doseq=True)
    ).respond_with_json(sessions_page)

    client = Client()
    page = client.sessions.v1.get_page(
        actor_id="actor-id",
        start_time=START_DATE,
        end_time=END_DATE,
        has_alerts=False,
        sort_key=SortKeys.SCORE,
        risk_indicators=["risk-indicator"],
        sort_dir=SortDirection.DESC,
        states=SessionStates.OPEN,
        severities=3,
        rule_ids="rule-id",
        watchlist_ids="watchlist-id",
        page_num=2,
        page_size=10,
        content_inspection_status=ContentInspectionStatuses.PENDING,
    )
    assert isinstance(page, SessionsPage)
    assert page.items[0].json() == json.dumps(TEST_SESSION)
    assert len(page.items) == 1 == page.total_count


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/sessions",
        method="GET",
        query_string=urlencode(
            {
                "has_alerts": "true",
                "page_number": 0,
                "page_size": 1,
            }
        ),
    ).respond_with_json({"items": [TEST_SESSION], "totalCount": 1})
    httpserver_auth.expect_request(
        "/v1/sessions",
        method="GET",
        query_string=urlencode(
            {
                "has_alerts": "true",
                "page_number": 1,
                "page_size": 1,
            }
        ),
    ).respond_with_json({"items": [], "totalCount": 1})

    client = Client()
    iterator = client.sessions.v1.iter_all(page_size=1)
    expected_sessions = [TEST_SESSION]
    total_count = 0
    for item in iterator:
        total_count += 1
        assert isinstance(item, Session)
        assert item.json() == json.dumps(expected_sessions.pop(0))
    assert total_count == 1


def test_iter_all_when_custom_params_returns_expected_data(httpserver_auth: HTTPServer):
    query_1 = {
        "actor_id": "actor-id",
        "on_or_after": POSIX_TS,
        "before": POSIX_TS,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
        "order_by": "score",
        "sort_direction": "desc",
        "page_number": 0,
        "page_size": 1,
    }
    query_2 = {
        "actor_id": "actor-id",
        "on_or_after": POSIX_TS,
        "before": POSIX_TS,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
        "order_by": "score",
        "sort_direction": "desc",
        "page_number": 1,
        "page_size": 1,
    }
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query_1, doseq=True)
    ).respond_with_json({"items": [TEST_SESSION], "totalCount": 1})
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query_2, doseq=True)
    ).respond_with_json({"items": [], "totalCount": 1})

    client = Client()
    iterator = client.sessions.v1.iter_all(
        actor_id="actor-id",
        start_time=DATETIME_INSTANT,
        end_time=DATETIME_INSTANT,
        has_alerts=False,
        sort_key=SortKeys.SCORE,
        risk_indicators=["risk-indicator"],
        sort_dir=SortDirection.DESC,
        states=SessionStates.OPEN,
        severities=3,
        rule_ids="rule-id",
        watchlist_ids="watchlist-id",
        page_size=1,
        content_inspection_status=ContentInspectionStatuses.PENDING,
    )
    expected_sessions = [TEST_SESSION]
    total_count = 0
    for item in iterator:
        total_count += 1
        assert isinstance(item, Session)
        assert item.json() == json.dumps(expected_sessions.pop(0))
    assert total_count == 1


def test_get_session_details_returns_expected_data(mock_get_session):
    client = Client()
    response = client.sessions.v1.get_session_details(TEST_SESSION_ID)
    assert isinstance(response, Session)
    assert response.json() == json.dumps(TEST_SESSION)


def test_get_session_events_returns_expected_data(
    httpserver_auth: HTTPServer, mock_get_events
):
    client = Client()
    response = client.sessions.v1.get_session_events(TEST_SESSION_ID)
    assert isinstance(response, FileEventsPage)
    assert len(response.file_events) == 2


def test_add_note_return_expected_data(httpserver_auth: HTTPServer):
    client = Client()
    note_content = "this is my note"
    httpserver_auth.expect_request(
        f"/v1/sessions/{TEST_SESSION_ID}/add-note",
        method="POST",
        json={"noteContent": note_content},
    ).respond_with_data()
    assert client.sessions.v1.add_note(TEST_SESSION_ID, note_content).status_code == 200


@pytest.mark.parametrize(
    "input_session_ids,expected_call",
    [
        (TEST_SESSION_ID, [TEST_SESSION_ID]),
        (
            [TEST_SESSION_ID, "my-session-id", "test"],
            [TEST_SESSION_ID, "my-session-id", "test"],
        ),
    ],
)
def test_update_state_by_id_makes_expected_call(
    httpserver_auth: HTTPServer, input_session_ids, expected_call
):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": expected_call, "newState": "CLOSED"},
    ).respond_with_data()
    client = Client()
    client.sessions.v1.update_state_by_id(input_session_ids, SessionStates.CLOSED)


def test_update_state_by_criteria_makes_expected_calls(httpserver_auth: HTTPServer):
    query = {
        "actor_id": "actor-id",
        "on_or_after": POSIX_TS,
        "before": POSIX_TS,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
    }

    token = "123-token"
    httpserver_auth.expect_request(
        "/v1/sessions/change-states",
        query_string=urlencode(query, doseq=True),
        method="POST",
        json={"continuationToken": None, "newState": "CLOSED"},
    ).respond_with_json({"continuationToken": token})
    httpserver_auth.expect_request(
        "/v1/sessions/change-states",
        query_string=urlencode(query, doseq=True),
        method="POST",
        json={"continuationToken": token, "newState": "CLOSED"},
    ).respond_with_json({"continuationToken": None})

    client = Client()
    responses = client.sessions.v1.update_state_by_criteria(
        new_state=SessionStates.CLOSED,
        actor_id="actor-id",
        start_time=DATETIME_INSTANT,
        end_time=DATETIME_INSTANT,
        has_alerts=False,
        risk_indicators=["risk-indicator"],
        states=SessionStates.OPEN,
        severities=3,
        rule_ids="rule-id",
        watchlist_ids="watchlist-id",
        content_inspection_status=ContentInspectionStatuses.PENDING,
    )
    assert responses[0].json()["continuationToken"] == token
    assert responses[1].json()["continuationToken"] is None
    for response in responses:
        assert response.status_code == 200


def test_update_state_by_criteria_when_given_date_uses_correct_timestamp(
    httpserver_auth: HTTPServer,
):
    query = {
        "actor_id": "actor-id",
        "on_or_after": START_TIMESTAMP,
        "before": END_TIMESTAMP,
        "has_alerts": "false",
        "risk_indicators": ["risk-indicator"],
        "state": ["OPEN"],
        "severity": [3],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
    }

    token = "123-token"
    httpserver_auth.expect_request(
        "/v1/sessions/change-states",
        query_string=urlencode(query, doseq=True),
        method="POST",
        json={"continuationToken": None, "newState": "CLOSED"},
    ).respond_with_json({"continuationToken": token})
    httpserver_auth.expect_request(
        "/v1/sessions/change-states",
        query_string=urlencode(query, doseq=True),
        method="POST",
        json={"continuationToken": token, "newState": "CLOSED"},
    ).respond_with_json({"continuationToken": None})

    client = Client()
    responses = client.sessions.v1.update_state_by_criteria(
        new_state=SessionStates.CLOSED,
        actor_id="actor-id",
        start_time=START_DATE,
        end_time=END_DATE,
        has_alerts=False,
        risk_indicators=["risk-indicator"],
        states=SessionStates.OPEN,
        severities=3,
        rule_ids="rule-id",
        watchlist_ids="watchlist-id",
        content_inspection_status=ContentInspectionStatuses.PENDING,
    )
    assert responses[0].json()["continuationToken"] == token
    assert responses[1].json()["continuationToken"] is None
    for response in responses:
        assert response.status_code == 200


# ************************************************ CLI ************************************************


def test_cli_search_with_checkpointing_stores_new_checkpoint(
    httpserver_auth, runner, mocker
):
    query = {"has_alerts": "true", "page_number": 0, "page_size": 50}

    # Only return one alert so `cursor.replace` is only called once.
    response = {"items": [TEST_SESSION], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query, doseq=True)
    ).respond_with_json(response)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = None
    with mock.patch(
        "_incydr_cli.cmds.sessions._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store, mock.patch.object(
        mock_cursor, "replace"
    ) as mock_replace, mock.patch.object(
        mock_cursor, "replace_items"
    ) as mock_replace_items:
        result = runner.invoke(
            incydr,
            [
                "sessions",
                "search",
                "--checkpoint",
                "test-chkpt",
            ],
        )
    httpserver_auth.check()

    mock_get_store.assert_called()
    mock_replace.assert_called_once_with(
        "test-chkpt",
        TEST_SESSION["endTime"],
    )
    mock_replace_items.assert_called_once_with(
        "test-chkpt", [TEST_SESSION["sessionId"]]
    )
    assert result.exit_code == 0


def test_cli_search_with_checkpointing_ignores_start_param_and_uses_existing_checkpoint(
    httpserver_auth, runner, mocker
):
    query = {
        "on_or_after": POSIX_TS,
        "has_alerts": "true",
        "page_number": 0,
        "page_size": 50,
    }

    # Only return one session so `cursor.replace` is only called once.
    response = {"items": [TEST_SESSION], "totalCount": 1}
    httpserver_auth.expect_request(
        "/v1/sessions", method="GET", query_string=urlencode(query, doseq=True)
    ).respond_with_json(response)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = TEST_SESSION["endTime"]
    with mock.patch(
        "_incydr_cli.cmds.sessions._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store:
        result = runner.invoke(
            incydr,
            [
                "sessions",
                "search",
                "--start",
                "2022-06-01",
                "--checkpoint",
                "test-chkpt",
            ],
        )
    httpserver_auth.check()
    mock_get_store.assert_called()
    assert result.exit_code == 0


def test_cli_search_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/sessions",
        method="GET",
        query_string=urlencode(
            {
                "has_alerts": "true",
                "page_number": 0,
                "page_size": 50,
            }
        ),
    ).respond_with_json({"items": [TEST_SESSION], "totalCount": 1})

    result = runner.invoke(
        incydr,
        ["sessions", "search"],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_search_when_custom_params_returns_expected_data(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "actor_id": "actor-id",
        "on_or_after": POSIX_TS,
        "before": POSIX_TS,
        "has_alerts": "false",
        "risk_indicators": ["value1", "value2"],
        "state": ["CLOSED"],
        "severity": [1, 2],
        "rule_id": ["rule-id"],
        "watchlist_id": ["watchlist-id"],
        "content_inspection_status": "PENDING",
        "page_number": 0,
        "page_size": 50,
    }
    httpserver_auth.expect_request(
        "/v1/sessions",
        method="GET",
        query_string=urlencode(query, doseq=True),
    ).respond_with_json({"items": [TEST_SESSION], "totalCount": 1})

    result = runner.invoke(
        incydr,
        [
            "sessions",
            "search",
            "--actor-id",
            "actor-id",
            "--start",
            "2024-1-1",
            "--end",
            "2024-1-1",
            "--no-alerts",
            "--risk-indicators",
            "value1,value2",
            "--state",
            "CLOSED",
            "--severity",
            "LOW",
            "--severity",
            "MODERATE",
            "--rule-id",
            "rule-id",
            "--watchlist-id",
            "watchlist-id",
            "--content-inspection-status",
            "PENDING",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_returns_expected_data(
    httpserver_auth: HTTPServer, runner, mock_get_session
):
    result = runner.invoke(incydr, ["sessions", "show", TEST_SESSION_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_events_returns_expected_data(
    httpserver_auth: HTTPServer, runner, mock_get_events
):
    result = runner.invoke(incydr, ["sessions", "show-events", TEST_SESSION_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_update_makes_expected_call(httpserver_auth: HTTPServer, runner):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": [TEST_SESSION_ID], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        f"/v1/sessions/{TEST_SESSION_ID}/add-note",
        method="POST",
        json={"noteContent": "note content"},
    ).respond_with_data()
    result = runner.invoke(
        incydr,
        [
            "sessions",
            "update",
            TEST_SESSION_ID,
            "--state",
            "CLOSED",
            "--note",
            "note content",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "file_text,options",
    [
        ("session_id,state\n1234,CLOSED,\nabcd,OPEN", None),
        (
            '{"session_id": "1234", "state": "CLOSED"}\n{"session_id": "abcd", "state": "OPEN"}',
            ["--format", "json-lines"],
        ),
    ],
)
def test_cli_bulk_update_state_when_state_column_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path, file_text, options
):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["1234"], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["abcd"], "newState": "OPEN"},
    ).respond_with_data()

    p = tmp_path / "update_sessions.csv"
    p.write_text(file_text)

    cmd = ["sessions", "bulk-update-state", str(p)]
    if options:
        cmd.extend(options)

    result = runner.invoke(incydr, cmd)
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "file_text,options",
    [
        ("session_id,state,note\n1234,CLOSED,\nabcd,OPEN,test note", None),
        (
            '{"session_id": "1234", "state": "CLOSED", "note": null}\n{"session_id": "abcd", "state": "OPEN", "note": "test note"}',
            ["--format", "json-lines"],
        ),
    ],
)
def test_cli_bulk_update_state_when_state_and_note_columns_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path, file_text, options
):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["1234"], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["abcd"], "newState": "OPEN"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/abcd/add-note",
        method="POST",
        json={"noteContent": "test note"},
    ).respond_with_data()

    p = tmp_path / "update_sessions.csv"
    p.write_text(file_text)

    cmd = ["sessions", "bulk-update-state", str(p)]
    if options:
        cmd.extend(options)

    result = runner.invoke(incydr, cmd)
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "file_text,options",
    [
        ("session_id\n1234\nabcd", ["--state", "CLOSED"]),
        (
            '{"session_id": "1234"}\n{"session_id": "abcd"}',
            ["--state", "CLOSED", "--format", "json-lines"],
        ),
    ],
)
def test_cli_bulk_update_state_when_state_option_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path, file_text, options
):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["1234"], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["abcd"], "newState": "CLOSED"},
    ).respond_with_data()

    p = tmp_path / "update_sessions.csv"
    p.write_text(file_text)

    cmd = ["sessions", "bulk-update-state", str(p)]
    cmd.extend(options)

    result = runner.invoke(incydr, cmd)
    httpserver_auth.check()
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "file_text,options",
    [
        ("session_id,note\n1234,\nabcd,test note", ["--state", "CLOSED"]),
        (
            '{"session_id": "1234", "note": null}\n{"session_id": "abcd", "note": "test note"}',
            ["--state", "CLOSED", "--format", "json-lines"],
        ),
    ],
)
def test_cli_bulk_update_state_when_state_option_and_note_column_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path, file_text, options
):
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["1234"], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/change-state",
        method="POST",
        json={"ids": ["abcd"], "newState": "CLOSED"},
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/sessions/abcd/add-note",
        method="POST",
        json={"noteContent": "test note"},
    ).respond_with_data()

    p = tmp_path / "update_sessions.csv"
    p.write_text(file_text)

    cmd = ["sessions", "bulk-update-state", str(p)]
    cmd.extend(options)

    result = runner.invoke(incydr, cmd)
    httpserver_auth.check()
    assert result.exit_code == 0
