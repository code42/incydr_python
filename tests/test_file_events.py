import json
from datetime import datetime
from datetime import timezone
from typing import List
from unittest import mock

import pytest
from _cli.cmds.options.output_options import TableFormat
from _cli.cursor import CursorStore
from _client.core.client import Client
from _client.file_events.models.event import FileEventV2
from _client.file_events.models.response import FileEventsPage
from _client.file_events.models.response import SavedSearch
from _client.file_events.models.response import SearchFilter
from _client.file_events.models.response import SearchFilterGroup
from _client.queries.file_events import EventQuery
from incydr.cli import incydr
from pytest_httpserver import HTTPServer

MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
TEST_EVENT_1 = {
    "@timestamp": "2022-07-14T16:53:06.112Z",
    "event": {
        "id": "2-event-id-100",
        "inserted": "2022-07-14T16:57:00.913917Z",
        "action": "application-read",
        "observer": "Endpoint",
        "shareType": [],
        "ingested": "2022-07-14T16:55:04.723Z",
        "relatedEvents": [],
    },
    "user": {
        "email": "engineer@example.com",
        "id": "1068824450489230065",
        "deviceUid": "1068825680073059134",
    },
    "file": {
        "name": "cat.jpg",
        "directory": "C:/Users/John Doe/Downloads/",
        "category": "Spreadsheet",
        "mimeTypeByBytes": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "categoryByBytes": "Spreadsheet",
        "mimeTypeByExtension": "image/jpeg",
        "categoryByExtension": "Image",
        "sizeInBytes": 4748,
        "owner": "John Doe",
        "created": "2022-07-14T16:51:06.186Z",
        "modified": "2022-07-14T16:51:07.419Z",
        "hash": {
            "md5": "8872dfa1c181b823d2c00675ae5926fd",
            "sha256": "14d749cce008711b4ad1381d84374539560340622f0e8b9eb2fe3bba77ddbd64",
            "md5Error": None,
            "sha256Error": None,
        },
        "id": None,
        "url": None,
        "directoryId": [],
        "cloudDriveId": None,
        "classifications": [],
    },
    "report": {
        "id": None,
        "name": None,
        "description": None,
        "headers": [],
        "count": None,
        "type": None,
    },
    "source": {
        "category": "Device",
        "name": "DESKTOP-1",
        "domain": "192.168.00.000",
        "ip": "50.237.00.00",
        "privateIp": ["192.168.00.000", "127.0.0.1"],
        "operatingSystem": "Windows 10",
        "email": {"sender": None, "from": None},
        "removableMedia": {
            "vendor": None,
            "name": None,
            "serialNumber": None,
            "capacity": None,
            "busType": None,
            "mediaName": None,
            "volumeName": [],
            "partitionId": [],
        },
        "tabs": [],
        "domains": [],
        "user": {"email": ["test@example.com"]},
    },
    "destination": {
        "category": "Cloud Storage",
        "name": "Dropbox",
        "user": {"email": []},
        "ip": None,
        "privateIp": [],
        "operatingSystem": None,
        "printJobName": None,
        "printerName": None,
        "printedFilesBackupPath": None,
        "removableMedia": {
            "vendor": None,
            "name": None,
            "serialNumber": None,
            "capacity": None,
            "busType": None,
            "mediaName": None,
            "volumeName": [],
            "partitionId": [],
        },
        "email": {"recipients": None, "subject": None},
        "tabs": [
            {
                "title": "Files - Dropbox and 1 more page - Profile 1 - Microsoft​ Edge",
                "url": "https://www.dropbox.com/home",
                "titleError": None,
                "urlError": None,
            }
        ],
        "accountName": None,
        "accountType": None,
        "domains": ["dropbox.com"],
    },
    "process": {
        "executable": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "owner": "John doe",
    },
    "risk": {
        "score": 17,
        "severity": "CRITICAL",
        "indicators": [
            {"name": "First use of destination", "weight": 3},
            {"name": "File mismatch", "weight": 9},
            {"name": "Spreadsheet", "weight": 0},
            {"name": "Remote", "weight": 0},
            {"name": "Dropbox upload", "weight": 5},
        ],
        "trusted": False,
        "trustReason": None,
    },
    "git": {
        "event_id": "1234",
        "last_commit_hash": "abcd-1234",
        "repository_email": "gituser@example.com",
        "repository_endpoint_path": "/test/repo",
        "repository_uri": "git@example.com",
        "repository_user": "Git User",
    },
}

TEST_EVENT_2 = {
    "@timestamp": "2022-05-31T17:44:59.699Z",
    "event": {
        "action": "application-read",
        "id": "1-event-id-100",
        "ingested": datetime(
            2022, 5, 31, 17, 46, 16, 859000, tzinfo=timezone.utc
        ).strftime(MICROSECOND_FORMAT)[:-4]
        + "Z",
        "inserted": datetime(
            2022, 5, 31, 17, 49, 15, 395939, tzinfo=timezone.utc
        ).strftime(MICROSECOND_FORMAT)[:-4]
        + "Z",
        "observer": "Endpoint",
        "related_events": None,
        "share_type": [],
    },
    "user": {
        "device_uid": "1062452691487811640",
        "email": "partner@code42.com",
        "id": "1046079859310944097",
    },
    "file": {
        "category": "Archive",
        "category_by_bytes": "Uncategorized",
        "category_by_extension": "Archive",
        "classifications": [],
        "cloud_drive_id": None,
        "created": datetime(
            2022, 4, 23, 23, 35, 59, 946000, tzinfo=timezone.utc
        ).strftime(MICROSECOND_FORMAT)[:-4]
        + "Z",
        "directory": "C:/Users/Documents/TestData/",
        "directory_id": [],
        "hash": {
            "md5": "b85d6fb9ef4260dcf1ce0a1b0bff80d3",
            "md5_error": None,
            "sha256": "95b532cc4381affdff0d956e12520a04129ed49d37e154228368fe5621f0b9a2",
            "sha256_error": None,
        },
        "id": None,
        "mime_type_by_bytes": "application/octet-stream",
        "mime_type_by_extension": "application/zip",
        "modified": datetime(2022, 4, 6, 14, 40, 40, tzinfo=timezone.utc).strftime(
            MICROSECOND_FORMAT
        )[:-4]
        + "Z",
        "name": "new-file.zip",
        "owner": "qa",
        "size_in_bytes": 10000,
        "url": None,
    },
    "report": {
        "count": None,
        "description": None,
        "headers": [],
        "id": None,
        "name": None,
        "type": None,
    },
    "source": {
        "category": None,
        "domain": None,
        "domains": [],
        "email": {"from_": None, "sender": None},
        "ip": "50.159.105.116",
        "name": None,
        "operating_system": "Windows 10",
        "private_ip": [
            "192.168.86.249",
            "fe80:0:0:0:a590:29af:1a88:a75b%eth7",
            "172.29.128.1",
            "fe80:0:0:0:d8bc:2bdf:bf78:dee%eth6",
            "0:0:0:0:0:0:0:1",
            "127.0.0.1",
        ],
        "removable_media": {
            "bus_type": None,
            "capacity": None,
            "media_name": None,
            "name": None,
            "partition_id": [],
            "serial_number": None,
            "vendor": None,
            "volume_name": [],
        },
        "tabs": [],
        "user": {"email": ["test@example.com"]},
    },
    "destination": {
        "account_name": None,
        "account_type": None,
        "category": "Cloud Storage",
        "domains": ["drive.google.com"],
        "email": {"recipients": None, "subject": None},
        "ip": None,
        "name": "Google Drive",
        "operating_system": None,
        "print_job_name": None,
        "printer_name": None,
        "private_ip": [],
        "removable_media": {
            "bus_type": None,
            "capacity": None,
            "media_name": None,
            "name": None,
            "partition_id": [],
            "serial_number": None,
            "vendor": None,
            "volume_name": [],
        },
        "tabs": [
            {
                "title": "QA Test Folder",
                "title_error": None,
                "url": "https://drive.google.com",
                "url_error": None,
            }
        ],
        "user": {"email": []},
    },
    "process": {
        "executable": "\\Device\\HarddiskVolume2\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "owner": "qa",
    },
    "risk": {
        "indicators": [
            {"name": "First use of destination", "weight": 3},
            {"name": "Remote", "weight": 0},
            {"name": "Google Drive upload", "weight": 5},
            {"name": "Zip", "weight": 3},
        ],
        "score": 11,
        "severity": "CRITICAL",
        "trust_reason": None,
        "trusted": False,
    },
}

TEST_EVENT_QUERY = (
    EventQuery(start_date="P14D")
    .equals("user.email", ["test@code42.com", "john.doe@code42.com"])
    .equals("file.category", "SourceCode")
)
TEST_EVENT_QUERY.page_size = 10000
TEST_SAVED_SEARCH_1 = SavedSearch(
    api_version=2,
    columns=None,
    created_by_uid="884180379747227785",
    created_by_username="test@code42.com",
    creation_timestamp=datetime(2019, 6, 27, 18, 15, 26, 191726, tzinfo=timezone.utc),
    group_clause="AND",
    groups=[
        SearchFilterGroup(
            filterClause="AND",
            filters=[
                SearchFilter(
                    operator="WITHIN_THE_LAST", term="@timestamp", value="P14D"
                )
            ],
        ),
        SearchFilterGroup(
            filterClause="OR",
            filters=[
                SearchFilter(operator="IS", term="user.email", value="test@code42.com"),
                SearchFilter(
                    operator="IS", term="user.email", value="john.doe@code42.com"
                ),
            ],
        ),
        SearchFilterGroup(
            filterClause="AND",
            filters=[
                SearchFilter(operator="IS", term="file.category", value="SOURCE_CODE")
            ],
        ),
    ],
    id="saved-search-1",
    modified_by_uid="884180379747227785",
    modified_by_username="test@code42.com",
    modified_timestamp=datetime(2019, 6, 27, 18, 15, 26, 191726, tzinfo=timezone.utc),
    name="Departing Employee Source Code",
    notes=None,
    srt_dir="asc",
    srt_key=None,
    tenantId="c4e43418-07d9-4a9f-a138-29f39a124d33",
)
TEST_SAVED_SEARCH_2 = SavedSearch(
    api_version=2,
    columns=None,
    created_by_uid="884180379747227785",
    created_by_username="john.doe@code42.com",
    creation_timestamp=datetime(2019, 6, 26, 12, 24, 45, 117610, tzinfo=timezone.utc),
    group_clause="AND",
    groups=[
        SearchFilterGroup(
            filterClause="AND",
            filters=[
                SearchFilter(
                    operator="IS", term="user.email", value="jane.doe@code42.com"
                )
            ],
        ),
        SearchFilterGroup(
            filterClause="AND",
            filters=[
                SearchFilter(
                    operator="WITHIN_THE_LAST", term="@timestamp", value="P14D"
                )
            ],
        ),
        SearchFilterGroup(
            filterClause="OR",
            filters=[
                SearchFilter(operator="IS", term="event.action", value="file-deleted"),
                SearchFilter(
                    operator="IS", term="event.action", value="removable-media-deleted"
                ),
                SearchFilter(
                    operator="IS", term="event.action", value="sync-app-deleted"
                ),
            ],
        ),
    ],
    id="saved-search-2",
    modified_by_uid="884180379747227785",
    modified_by_username="john.doe@code42.com",
    modified_timestamp=datetime(2019, 6, 26, 12, 24, 45, 117610, tzinfo=timezone.utc),
    name="Departing Employee Deleted Files",
    notes=None,
    srt_dir="asc",
    srt_key=None,
    tenantId="c4e43418-07d9-4a9f-a138-29f39a124d33",
)


TEST_DICT_QUERY = {
    "groupClause": "AND",
    "groups": [
        {
            "filterClause": "AND",
            "filters": [
                {"term": "@timestamp", "operator": "WITHIN_THE_LAST", "value": "P14D"}
            ],
        },
        {
            "filterClause": "OR",
            "filters": [
                {"term": "user.email", "operator": "IS", "value": "test@code42.com"},
                {
                    "term": "user.email",
                    "operator": "IS",
                    "value": "john.doe@code42.com",
                },
            ],
        },
        {
            "filterClause": "AND",
            "filters": [
                {"term": "file.category", "operator": "IS", "value": "SourceCode"}
            ],
        },
    ],
    "pgNum": 1,
    "pgSize": 10000,
    "pgToken": "",
    "srtDir": "asc",
    "srtKey": "event.id",
}

TEST_SAVED_SEARCH_QUERY = {
    "groupClause": "AND",
    "groups": [
        {
            "filterClause": "AND",
            "filters": [
                {"term": "@timestamp", "operator": "WITHIN_THE_LAST", "value": "P14D"}
            ],
        },
        {
            "filterClause": "OR",
            "filters": [
                {"term": "user.email", "operator": "IS", "value": "test@code42.com"},
                {
                    "term": "user.email",
                    "operator": "IS",
                    "value": "john.doe@code42.com",
                },
            ],
        },
        {
            "filterClause": "AND",
            "filters": [
                {"term": "file.category", "operator": "IS", "value": "SOURCE_CODE"}
            ],
        },
    ],
    "pgNum": 1,
    "pgSize": 10000,
    "pgToken": "",
    "srtDir": "asc",
    "srtKey": "event.id",
}

TEST_SAVED_SEARCH_ID = "saved-search-1"


@pytest.fixture
def mock_get_saved_search(httpserver_auth):
    search_data = {"searches": [json.loads(TEST_SAVED_SEARCH_1.json())]}
    httpserver_auth.expect_request(
        f"/v2/file-events/saved-searches/{TEST_SAVED_SEARCH_ID}", method="GET"
    ).respond_with_json(search_data)


@pytest.fixture
def mock_list_saved_searches(httpserver_auth):
    search_data = {
        "searches": [
            json.loads(TEST_SAVED_SEARCH_1.json()),
            json.loads(TEST_SAVED_SEARCH_2.json()),
        ]
    }
    httpserver_auth.expect_request(
        "/v2/file-events/saved-searches", method="GET"
    ).respond_with_json(search_data)


@pytest.mark.parametrize(
    "query, expected_query",
    [(TEST_EVENT_QUERY, TEST_DICT_QUERY)],
)
def test_search_sends_expected_query(
    httpserver_auth: HTTPServer, query, expected_query
):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": "",
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=expected_query
    ).respond_with_json(event_data)

    client = Client()
    response = client.file_events.v2.search(query)
    assert isinstance(response, FileEventsPage)


def test_search_returns_expected_data(httpserver_auth: HTTPServer):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request("/v2/file-events", method="POST").respond_with_json(
        event_data
    )

    client = Client()
    query = EventQuery.construct(**TEST_DICT_QUERY)
    page = client.file_events.v2.search(query)
    assert isinstance(page, FileEventsPage)
    assert page.file_events[0] == FileEventV2.parse_obj(TEST_EVENT_1)
    assert page.file_events[1] == FileEventV2.parse_obj(TEST_EVENT_2)
    assert page.total_count == len(page.file_events)


def test_list_saved_searches_returns_expected_data(mock_list_saved_searches):
    client = Client()
    page = client.file_events.v2.list_saved_searches()
    assert isinstance(page, List)
    for item in page:
        assert isinstance(item, SavedSearch)
    assert page[0].json() == TEST_SAVED_SEARCH_1.json()
    assert page[1].json() == TEST_SAVED_SEARCH_2.json()


def test_get_saved_search_returns_expected_data(mock_get_saved_search):
    client = Client()
    search = client.file_events.v2.get_saved_search(TEST_SAVED_SEARCH_ID)
    assert isinstance(search, SavedSearch)
    assert search.json() == TEST_SAVED_SEARCH_1.json()


# ************************************************ CLI ************************************************

format_arg = pytest.mark.parametrize(
    "format_",
    [
        TableFormat.json_pretty,
        TableFormat.json_lines,
        TableFormat.csv,
        TableFormat.table,
    ],
)


@format_arg
def test_cli_search_with_checkpointing_stores_new_checkpoint(
    httpserver_auth, runner, mocker, format_
):
    query = (
        EventQuery(start_date="2022-06-01")
        .equals("file.category", "DOCUMENT")
        .greater_than("risk.score", 1)
    )
    query.page_size = 10000

    httpserver_auth.expect_ordered_request(
        "/v2/file-events", method="POST", json=query.dict()
    ).respond_with_json(
        {
            "fileEvents": [TEST_EVENT_1],
            "nextPgToken": None,
            "problems": None,
            "totalCount": 1,
        }
    )

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = None
    with mock.patch(
        "_cli.cmds.file_events._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store, mock.patch.object(mock_cursor, "replace") as mock_replace:
        result = runner.invoke(
            incydr,
            [
                "file-events",
                "search",
                "--start",
                "2022-06-01",
                "--file-category",
                "DOCUMENT",
                "--checkpoint",
                "test-chkpt",
                "-f",
                format_,
            ],
        )
    httpserver_auth.check()
    mock_get_store.assert_called()
    query.pgToken = TEST_EVENT_1["event"]["id"]
    mock_replace.assert_called_once_with("test-chkpt", json.dumps(query.dict()))
    assert result.exit_code == 0


@format_arg
def test_cli_search_with_checkpointing_ignores_params_and_uses_existing_checkpoint(
    httpserver_auth, runner, mocker, format_
):
    query = (
        EventQuery(start_date="2022-06-01")
        .equals("file.category", "DOCUMENT")
        .greater_than("risk.score", 1)
    )
    query.pgToken = TEST_EVENT_1["event"]["id"]

    httpserver_auth.expect_ordered_request(
        "/v2/file-events", method="POST", json=query.dict()
    ).respond_with_json(
        {
            "fileEvents": [TEST_EVENT_1],
            "nextPgToken": None,
            "problems": None,
            "totalCount": 1,
        }
    )

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = json.dumps(query.dict())
    with mock.patch(
        "_cli.cmds.file_events._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store:
        result = runner.invoke(
            incydr,
            [
                "file-events",
                "search",
                "--start",
                "2020-08-10",
                "--risk-score",
                "10",
                "--checkpoint",
                "test-chkpt",
                "-f",
                format_,
            ],
        )

    httpserver_auth.check()
    mock_get_store.assert_called()
    assert result.exit_code == 0


def test_cli_search_when_no_start_param_raises_bad_option_usage_exception(
    runner, httpserver_auth: HTTPServer
):
    result = runner.invoke(
        incydr,
        [
            "file-events",
            "search",
        ],
    )
    assert result.exit_code == 2
    assert (
        "--start option required if not using --saved-search or --advanced-query options."
        in result.output
    )


def test_cli_search_when_default_params_makes_expected_api_call(
    runner, httpserver_auth: HTTPServer
):
    query = {
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "@timestamp",
                        "operator": "ON_OR_AFTER",
                        "value": "2022-06-01T00:00:00.000Z",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "risk.score", "operator": "GREATER_THAN", "value": 1}
                ],
            },
        ],
        "pgNum": 1,
        "pgSize": 10000,
        "pgToken": "",
        "srtDir": "asc",
        "srtKey": "event.id",
    }

    event_data = {
        "fileEvents": [TEST_EVENT_1],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }

    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=query
    ).respond_with_json(event_data)

    result = runner.invoke(
        incydr,
        [
            "file-events",
            "search",
            "--start",
            "2022-06-01",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_search_when_filter_params_makes_expected_api_call(
    runner, httpserver_auth: HTTPServer
):
    query = {
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "@timestamp",
                        "operator": "ON_OR_AFTER",
                        "value": "2022-06-01T00:00:00.000Z",
                    },
                    {
                        "term": "@timestamp",
                        "operator": "ON_OR_BEFORE",
                        "value": "2022-08-10T00:00:00.000Z",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "event.action", "operator": "IS", "value": "file-created"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "user.email", "operator": "IS", "value": "foo@bar.com"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "file.hash.md5", "operator": "IS", "value": "foo"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "file.hash.sha256", "operator": "IS", "value": "bar"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "source.category",
                        "operator": "IS",
                        "value": "Coding Tools",
                    }
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "destination.category",
                        "operator": "IS",
                        "value": "Web Hosting",
                    }
                ],
            },
            {
                "filterClause": "AND",
                "filters": [{"term": "file.name", "operator": "IS", "value": "baz"}],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "file.directory",
                        "operator": "IS",
                        "value": "C://foo/bar.txt",
                    }
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "file.category", "operator": "IS", "value": "Document"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "risk.indicators.name",
                        "operator": "IS",
                        "value": "Bitbucket upload",
                    }
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "risk.severity", "operator": "IS", "value": "HIGH"}
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {"term": "risk.score", "operator": "GREATER_THAN", "value": 10}
                ],
            },
        ],
        "pgNum": 1,
        "pgSize": 10000,
        "pgToken": "",
        "srtDir": "asc",
        "srtKey": "event.id",
    }

    event_data = {
        "fileEvents": [TEST_EVENT_1],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }

    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=query
    ).respond_with_json(event_data)

    result = runner.invoke(
        incydr,
        [
            "file-events",
            "search",
            "--start",
            "2022-06-01",
            "--end",
            "2022-08-10",
            "--event-action",
            "file-created",
            "--username",
            "foo@bar.com",
            "--md5",
            "foo",
            "--sha256",
            "bar",
            "--source-category",
            "Coding Tools",
            "--destination-category",
            "Web Hosting",
            "--file-name",
            "baz",
            "--file-directory",
            "C://foo/bar.txt",
            "--file-category",
            "Document",
            "--risk-indicator",
            "Bitbucket upload",
            "--risk-severity",
            "HIGH",
            "--risk-score",
            "10",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_search_when_advanced_query_makes_expected_api_call(
    runner, httpserver_auth
):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=TEST_DICT_QUERY
    ).respond_with_json(event_data)

    result = runner.invoke(
        incydr,
        [
            "file-events",
            "search",
            "--advanced-query",
            json.dumps(TEST_DICT_QUERY),
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_search_when_advanced_query_from_file_makes_expected_api_call(
    runner, httpserver_auth, tmp_path
):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=TEST_DICT_QUERY
    ).respond_with_json(event_data)

    p = tmp_path / "query.json"
    p.write_text(json.dumps(TEST_DICT_QUERY))

    result = runner.invoke(
        incydr,
        ["file-events", "search", "--advanced-query", "@" + str(p)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_search_when_saved_search_makes_expected_api_call(
    runner, mock_get_saved_search, httpserver_auth
):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=TEST_SAVED_SEARCH_QUERY
    ).respond_with_json(event_data)

    result = runner.invoke(
        incydr, ["file-events", "search", "--saved-search", TEST_SAVED_SEARCH_ID]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_saved_search_makes_expected_sdk_call(
    httpserver_auth: HTTPServer, runner, mock_get_saved_search
):
    result = runner.invoke(
        incydr,
        ["file-events", "show-saved-search", TEST_SAVED_SEARCH_ID],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_saved_searches_makes_expected_api_call(
    httpserver_auth: HTTPServer, runner, mock_list_saved_searches
):
    result = runner.invoke(incydr, ["file-events", "list-saved-searches"])
    httpserver_auth.check()
    assert result.exit_code == 0
