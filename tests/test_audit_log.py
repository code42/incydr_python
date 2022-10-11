import datetime
from pathlib import Path

from pytest_httpserver import HTTPServer

from incydr import Client
from incydr._audit_log.models import AuditEventsPage

Test_Audit_Log_1 = {
    "type$": "audit_log::logged_in/1",
    "actorId": "898209175991065670",
    "actorName": "whiteoak_ffs_user2@code42.com",
    "actorAgent": "py42 0.2.0 python 2.7.14 Code42ForSplunk.v3.0.12.b250",
    "actorIpAddress": "50.93.255.223, 64.252.71.111",
    "timestamp": "2022-10-03T13:14:46.962Z",
    "actorType": "UNKNOWN",
}

Test_Audit_Log_2 = {
    "type$": "audit_log::federation_metadata_updated/1",
    "actorId": "thwlhuOyiq2svbdcqfmm2demndi",
    "actorName": "SYSTEM",
    "actorAgent": "null",
    "actorIpAddress": "null",
    "timestamp": "2022-09-28T19:57:10.072Z",
    "actorType": "SYSTEM",
    "federationId": "1034183599256332463",
    "metadataUrl": "https://md.incommon.org/InCommon/InCommon-metadata.xml",
    "displayName": "Auth Provider Federation",
    "metadataMd5sum": "4df933958e17eea24f51f3bf0d375327",
}


def test_get_page_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_data = {
        "events": [
            Test_Audit_Log_1,
            Test_Audit_Log_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    httpserver_auth.expect_request("/v1/audit/search-audit-log").respond_with_json(
        audit_events_data
    )

    client = Client()
    page = client.audit_log.v1.get_page()
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == Test_Audit_Log_1
    assert page.events[1] == Test_Audit_Log_2
    assert page.pagination_range_end_index == len(page.events) == 2


def test_get_page_when_all_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_data = {
        "events": [
            Test_Audit_Log_1,
            Test_Audit_Log_2,
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
        actor_ip_addresses=["50.93.255.223, 64.252.71.111", "null"],
        actor_names=["whiteoak_ffs_user2@code42.com", "SYSTEM"],
        start_time=datetime.datetime.strptime("09/19/18 13:55:26", "%m/%d/%y %H:%M:%S"),
        end_time=datetime.datetime.strptime("10/03/23 13:14:46", "%m/%d/%y %H:%M:%S"),
        event_types=["logged_in", "federation_metadata_updated"],
        resource_ids=["1"],
        user_types=["UNKNOWN", "SYSTEM"],
    )
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == Test_Audit_Log_1
    assert page.events[1] == Test_Audit_Log_2
    assert page.pagination_range_end_index == len(page.events) == 2


def test_search_events_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_data = {
        "events": [
            Test_Audit_Log_1,
            Test_Audit_Log_2,
        ],
        "pagination_range_start_index": 0,
        "pagination_range_end_index": 2,
    }
    httpserver_auth.expect_request("/v1/audit/search-results-export").respond_with_json(
        audit_events_data
    )

    client = Client()
    page = client.audit_log.v1.search_events()
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == Test_Audit_Log_1
    assert page.events[1] == Test_Audit_Log_2
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
