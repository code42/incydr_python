import datetime
from pathlib import Path
from unittest import mock

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.cmds.audit_log import _hash_event
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cursor import CursorStore
from _incydr_cli.main import incydr
from _incydr_sdk.audit_log.models import AuditEventsPage
from _incydr_sdk.queries.utils import parse_ts_to_posix_ts
from incydr import Client

TEST_AL_ENTRY_1 = {
    "type$": "audit_log::logged_in/1",
    "actorId": "898209175991065670",
    "actorName": "whiteoak_ffs_user2@code42.com",
    "actorAgent": "py42 0.2.0 python 2.7.14 Code42ForSplunk.v3.0.12.b250",
    "actorIpAddress": "50.93.255.223, 64.252.71.111",
    "timestamp": "2022-10-03T13:14:46.962Z",
    "actorType": "UNKNOWN",
}

TEST_AL_ENTRY_2 = {
    "type$": "audit_log::federation_metadata_updated/1",
    "actorId": "thwlhuOyiq2svbdcqfmm2demndi",
    "actorName": "SYSTEM",
    "actorAgent": None,
    "actorIpAddress": None,
    "timestamp": "2022-09-28T19:57:10.072Z",
    "actorType": "SYSTEM",
    "federationId": "1034183599256332463",
    "metadataUrl": "https://md.incommon.org/InCommon/InCommon-metadata.xml",
    "displayName": "Auth Provider Federation",
    "metadataMd5sum": "4df933958e17eea24f51f3bf0d375327",
}


@pytest.fixture
def mock_search(httpserver_auth: HTTPServer):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
            TEST_AL_ENTRY_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    data = {
        "actorIds": None,
        "actorIpAddresses": None,
        "actorNames": None,
        "dateRange": {"endTime": None, "startTime": None},
        "eventTypes": None,
        "page": 0,
        "pageSize": 100,
        "resourceIds": None,
        "userTypes": None,
    }
    httpserver_auth.expect_request(
        "/v1/audit/search-audit-log", method="POST", json=data
    ).respond_with_json(audit_events_data)


@pytest.fixture
def mock_export(httpserver_auth: HTTPServer):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
            TEST_AL_ENTRY_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    data = {
        "actorIds": None,
        "actorIpAddresses": None,
        "actorNames": None,
        "dateRange": {"endTime": None, "startTime": None},
        "eventTypes": None,
        "page": 0,
        "pageSize": 0,
        "resourceIds": None,
        "userTypes": None,
    }
    httpserver_auth.expect_request(
        "/v1/audit/search-results-export", method="POST", json=data
    ).respond_with_json(audit_events_data)


def test_get_page_when_default_params_returns_expected_data(mock_search):
    client = Client()
    page = client.audit_log.v1.get_page()
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == TEST_AL_ENTRY_1
    assert page.events[1] == TEST_AL_ENTRY_2
    assert page.pagination_range_end_index == len(page.events) == 2


def test_get_page_when_all_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
            TEST_AL_ENTRY_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }

    httpserver_auth.expect_request(
        "/v1/audit/search-audit-log",
    ).respond_with_json(audit_events_data)

    client = Client()
    page = client.audit_log.v1.get_page(
        page_num=1,
        page_size=100,
        actor_ids=["898209175991065670", "thwlhuOyiq2svbdcqfmm2demndi"],
        actor_ip_addresses=["50.93.255.223, 64.252.71.111", "None"],
        actor_names=["whiteoak_ffs_user2@code42.com", "SYSTEM"],
        start_time=datetime.datetime.strptime("09/19/18 13:55:26", "%m/%d/%y %H:%M:%S"),
        end_time=datetime.datetime.strptime("10/03/23 13:14:46", "%m/%d/%y %H:%M:%S"),
        event_types=["logged_in", "federation_metadata_updated"],
        resource_ids=["1"],
        user_types=["UNKNOWN", "SYSTEM"],
    )
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == TEST_AL_ENTRY_1
    assert page.events[1] == TEST_AL_ENTRY_2
    assert page.pagination_range_end_index == len(page.events) == 2


def test_get_events_count_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_count_data = {"totalResultCount": 2}
    httpserver_auth.expect_request("/v1/audit/search-results-count").respond_with_json(
        audit_events_count_data
    )

    client = Client()
    results_count = client.audit_log.v1.get_event_count()
    assert isinstance(results_count, int)
    assert results_count == 2


def test_download_events_when_default_params_makes_expected_calls(
    httpserver_auth: HTTPServer,
):
    export_event_data = {
        "downloadToken": "r_MltMkE_hFAUJA0EKsGe2F9GefX1NuIo3GtjRxSLVI="
    }

    httpserver_auth.expect_request("/v1/audit/export").respond_with_json(
        export_event_data
    )

    redeem_events_data = {
        "events": [],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 0,
    }

    httpserver_auth.expect_request(
        "/v1/audit/redeemDownloadToken", query_string=export_event_data
    ).respond_with_json(redeem_events_data)

    client = Client()
    response = client.audit_log.v1.download_events(Path.cwd())

    assert isinstance(response, Path)


# ************************************************ CLI ************************************************
format_arg = pytest.mark.parametrize(
    "format_", [TableFormat.json_pretty, TableFormat.json_lines, TableFormat.csv]
)


@format_arg
def test_cli_search_with_checkpointing_stores_new_checkpoint(
    httpserver_auth, runner, mocker, format_
):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 1,
    }
    data = {
        "actorIds": None,
        "actorIpAddresses": None,
        "actorNames": None,
        "dateRange": {"endTime": None, "startTime": None},
        "eventTypes": None,
        "page": 0,
        "pageSize": 100,
        "resourceIds": None,
        "userTypes": None,
    }
    httpserver_auth.expect_request(
        "/v1/audit/search-audit-log", method="POST", json=data
    ).respond_with_json(audit_events_data)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = None
    with mock.patch(
        "_incydr_cli.cmds.audit_log._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store, mock.patch.object(
        mock_cursor, "replace"
    ) as mock_replace, mock.patch.object(
        mock_cursor, "replace_items"
    ) as mock_replace_items:
        result = runner.invoke(
            incydr,
            ["audit-log", "search", "--checkpoint", "test-chkpt", "-f", format_],
        )
    httpserver_auth.check()
    mock_get_store.assert_called()
    mock_replace.assert_called_once_with(
        "test-chkpt", parse_ts_to_posix_ts(TEST_AL_ENTRY_1["timestamp"])
    )
    mock_replace_items.assert_called_once_with(
        "test-chkpt", [_hash_event(TEST_AL_ENTRY_1)]
    )
    assert result.exit_code == 0


@format_arg
def test_cli_search_with_checkpointing_ignores_start_param_and_uses_existing_checkpoint(
    httpserver_auth, runner, mocker, format_
):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
            TEST_AL_ENTRY_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    ts = parse_ts_to_posix_ts(TEST_AL_ENTRY_1["timestamp"])
    data = {
        "actorIds": None,
        "actorIpAddresses": None,
        "actorNames": None,
        "dateRange": {"endTime": None, "startTime": ts},
        "eventTypes": None,
        "page": 0,
        "pageSize": 100,
        "resourceIds": None,
        "userTypes": None,
    }
    httpserver_auth.expect_request(
        "/v1/audit/search-audit-log", method="POST", json=data
    ).respond_with_json(audit_events_data)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = ts
    with mock.patch(
        "_incydr_cli.cmds.audit_log._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store:
        result = runner.invoke(
            incydr,
            [
                "audit-log",
                "search",
                "--start",
                "2022-06-01",
                "--checkpoint",
                "test-chkpt",
                "-f",
                format_,
            ],
        )
    httpserver_auth.check()
    mock_get_store.assert_called()
    assert result.exit_code == 0


def test_cli_search_when_default_params_makes_expected_call(runner, mock_search):
    result = runner.invoke(incydr, ["audit-log", "search"])
    assert result.exit_code == 0


def test_cli_search_when_custom_params_makes_expected_call(
    runner, httpserver_auth: HTTPServer
):
    audit_events_data = {
        "events": [
            TEST_AL_ENTRY_1,
            TEST_AL_ENTRY_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    data = {
        "actorIds": ["foo", "bar"],
        "actorIpAddresses": ["foo1", "bar1"],
        "actorNames": ["foo2", "bar2"],
        "dateRange": {"endTime": 1666296001.0, "startTime": 1662768000.0},
        "eventTypes": ["foo3", "bar3"],
        "page": 0,
        "pageSize": 100,
        "resourceIds": ["foo4", "bar4"],
        "userTypes": ["USER"],
    }
    httpserver_auth.expect_request(
        "/v1/audit/search-audit-log", method="POST", json=data
    ).respond_with_json(audit_events_data)

    result = runner.invoke(
        incydr,
        [
            "audit-log",
            "search",
            "--start",
            "2022-09-10",
            "--end",
            "2022-10-20 20:00:01",
            "--actor-ids",
            "foo,bar",
            "--actor-ip-addresses",
            "foo1,bar1",
            "--actor-names",
            "foo2,bar2",
            "--event-types",
            "foo3,bar3",
            "--resource-ids",
            "foo4,bar4",
            "--user-types",
            "USER",
        ],
    )
    assert result.exit_code == 0


def test_cli_download_makes_expected_call(
    runner, httpserver_auth: HTTPServer, tmp_path
):
    export_event_data = {
        "downloadToken": "r_MltMkE_hFAUJA0EKsGe2F9GefX1NuIo3GtjRxSLVI="
    }
    data = {
        "actorIds": None,
        "actorIpAddresses": None,
        "actorNames": None,
        "dateRange": {"endTime": None, "startTime": None},
        "eventTypes": None,
        "resourceIds": None,
        "userTypes": None,
    }
    httpserver_auth.expect_request(
        "/v1/audit/export", method="POST", json=data
    ).respond_with_json(export_event_data)

    redeem_events_data = {
        "events": [],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 0,
    }

    httpserver_auth.expect_request(
        "/v1/audit/redeemDownloadToken", query_string=export_event_data
    ).respond_with_json(redeem_events_data)

    result = runner.invoke(incydr, ["audit-log", "download", "--path", str(tmp_path)])
    httpserver_auth.check()
    assert result.exit_code == 0
