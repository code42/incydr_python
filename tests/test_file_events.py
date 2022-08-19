from datetime import datetime
from datetime import timezone

import pytest
from pytest_httpserver import HTTPServer

from incydr._core.client import Client
from incydr._file_events.models.event import FileEventV2
from incydr._file_events.models.request import SearchFilter
from incydr._file_events.models.request import SearchFilterGroup
from incydr._file_events.models.response import FileEventsPage
from incydr._file_events.models.response import SavedSearch
from incydr._file_events.models.response import SavedSearchesPage
from incydr._queries.file_events import EventQuery

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
TEST_SAVED_SEARCH_1 = SavedSearch(
    api_version=2,
    columns=None,
    created_by_uid="884180379747227785",
    created_by_username="test@code42.com",
    creation_timestamp=datetime(
        2019, 6, 27, 18, 15, 26, 191726, tzinfo=timezone.utc
    ).strftime(MICROSECOND_FORMAT)[:-4]
    + "Z",
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
                SearchFilter(operator="IS", term="file.category", value="SourceCode")
            ],
        ),
    ],
    id="saved-search-1",
    modified_by_uid="884180379747227785",
    modified_by_username="test@code42.com",
    modified_timestamp=datetime(
        2019, 6, 27, 18, 15, 26, 191726, tzinfo=timezone.utc
    ).strftime(MICROSECOND_FORMAT)[:-4]
    + "Z",
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
    creation_timestamp=datetime(
        2019, 6, 26, 12, 24, 45, 117610, tzinfo=timezone.utc
    ).strftime(MICROSECOND_FORMAT)[:-4]
    + "Z",
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
    modified_timestamp=datetime(
        2019, 6, 26, 12, 24, 45, 117610, tzinfo=timezone.utc
    ).strftime(MICROSECOND_FORMAT)[:-4]
    + "Z",
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
    "pgSize": 100,
    "pgToken": None,
    "srtDir": "asc",
    "srtKey": "event.id",
}


@pytest.mark.parametrize(
    "query", [TEST_EVENT_QUERY, TEST_SAVED_SEARCH_1, TEST_DICT_QUERY]
)
def test_search_sends_expected_query(httpserver_auth: HTTPServer, query):
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }
    httpserver_auth.expect_request(
        "/v2/file-events", method="POST", json=TEST_DICT_QUERY
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
    page = client.file_events.v2.search(TEST_DICT_QUERY)
    assert isinstance(page, FileEventsPage)
    assert page.file_events[0] == FileEventV2.parse_obj(TEST_EVENT_1)
    assert page.file_events[1] == FileEventV2.parse_obj(TEST_EVENT_2)
    assert page.total_count == len(page.file_events)


def test_get_all_saved_searches_returns_expected_data(httpserver_auth: HTTPServer):
    search_data = {
        "searches": [TEST_SAVED_SEARCH_1.dict(), TEST_SAVED_SEARCH_2.dict()],
        "problems": None,
    }
    httpserver_auth.expect_request(
        "/v2/file-events/saved-searches", method="GET"
    ).respond_with_json(search_data)

    client = Client()
    page = client.file_events.v2.get_all_saved_searches()
    assert isinstance(page, SavedSearchesPage)
    assert page.searches[0].json() == TEST_SAVED_SEARCH_1.json()
    assert page.searches[1].json() == TEST_SAVED_SEARCH_2.json()


def test_get_saved_search_by_id_returns_expected_data(httpserver_auth: HTTPServer):
    search_id = "saved-search-1"
    search_data = {"searches": [TEST_SAVED_SEARCH_1.dict()], "problems": None}

    httpserver_auth.expect_request(
        f"/v2/file-events/saved-searches/{search_id}", method="GET"
    ).respond_with_json(search_data)

    client = Client()
    search = client.file_events.v2.get_saved_search_by_id(search_id)
    assert isinstance(search, SavedSearch)
    assert search.json() == TEST_SAVED_SEARCH_1.json()


def test_execute_saved_search_makes_expected_calls(httpserver_auth: HTTPServer):
    search_id = "saved-search-1"
    search_data = {"searches": [TEST_SAVED_SEARCH_1.dict()], "problems": None}
    event_data = {
        "fileEvents": [TEST_EVENT_1, TEST_EVENT_2],
        "nextPgToken": None,
        "problems": None,
        "totalCount": 2,
    }

    httpserver_auth.expect_ordered_request(
        f"/v2/file-events/saved-searches/{search_id}", method="GET"
    ).respond_with_json(search_data)
    httpserver_auth.expect_ordered_request(
        "/v2/file-events", method="POST", json=TEST_DICT_QUERY
    ).respond_with_json(event_data)

    client = Client()
    response = client.file_events.v2.execute_saved_search(search_id)
    assert isinstance(response, FileEventsPage)
