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


def test_search_results_export_when_default_params_returns_expected_data(
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
    page = client.audit_log.v1.search_results_export()
    assert isinstance(page, AuditEventsPage)
    assert page.events[0] == Test_Audit_Log_1
    assert page.events[1] == Test_Audit_Log_2
    assert page.pagination_range_end_index == len(page.events) == 2


def test_search_results_count_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    audit_events_count_data = {"totalResultCount": 2}
    httpserver_auth.expect_request("/v1/audit/search-results-count").respond_with_json(
        audit_events_count_data
    )

    client = Client()
    results_count = client.audit_log.v1.search_results_count()
    assert isinstance(results_count, int)
    assert results_count == 2
