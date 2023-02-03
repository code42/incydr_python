import json
from datetime import datetime
from unittest import mock

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.cursor import CursorStore
from _incydr_cli.main import incydr
from _incydr_sdk.alerts.models.response import AlertDetails
from _incydr_sdk.alerts.models.response import AlertQueryPage
from _incydr_sdk.alerts.models.response import AlertSummary
from _incydr_sdk.queries.utils import parse_ts_to_posix_ts
from incydr import AlertQuery
from incydr import Client


TEST_ALERT_ID = "000-42-code"

TEST_ALERTS_RESPONSE = {
    "type$": "ALERT_QUERY_RESPONSE",
    "alerts": [
        {
            "type$": "ALERT_SUMMARY",
            "tenantId": "abcd-1234",
            "type": "FED_COMPOSITE",
            "name": "Source Alert",
            "description": "",
            "actor": "user@example.com",
            "actorId": "8675309",
            "target": "N/A",
            "severity": "HIGH",
            "riskSeverity": "CRITICAL",
            "ruleId": "51aa0c99-66e7-44d0-bf2f-c91487796794",
            "watchlists": [
                {
                    "type$": "WATCHLIST",
                    "id": "b366e314-df8c-4c61-a963-7c0d5df31f1e",
                    "name": "SDK_TEST",
                    "type": "WATCHLIST_TYPE_UNSPECIFIED",
                    "isSignificant": True,
                }
            ],
            "id": "d020eee5-0a2d-4255-9f09-83aa7015dabc",
            "createdAt": "2022-09-15T20:48:25.519828Z",
            "state": "OPEN",
        },
        {
            "type$": "ALERT_SUMMARY",
            "tenantId": "abcd-1234",
            "type": "FED_COMPOSITE",
            "name": "Test Alerts",
            "description": "",
            "actor": "user@example.com",
            "actorId": "8675309",
            "target": "N/A",
            "severity": "HIGH",
            "riskSeverity": "CRITICAL",
            "ruleId": "9fdfec5b-afe1-4531-a8a3-61e1aa2edb91",
            "watchlists": [
                {
                    "type$": "WATCHLIST",
                    "id": "b366e314-df8c-4c61-a963-7c0d5df31f1e",
                    "name": "SDK_TEST",
                    "type": "WATCHLIST_TYPE_UNSPECIFIED",
                    "isSignificant": False,
                }
            ],
            "id": "259a5d1a-8cbb-45e2-af94-28a3a55f2902",
            "createdAt": "2022-09-15T20:48:25.575682Z",
            "state": "OPEN",
        },
    ],
    "totalCount": 2,
    "problems": [],
}

TEST_ALERT_DETAILS_RESPONSE = {
    "type$": "ALERT_DETAILS_RESPONSE",
    "alerts": [
        {
            "type$": "ALERT_DETAILS",
            "tenantId": "abcd-1234",
            "type": "FED_COMPOSITE",
            "name": "Test Alerts",
            "description": "Test Description",
            "actor": "user@example.com",
            "actorId": "1050590243935435820",
            "target": "N/A",
            "severity": "LOW",
            "riskSeverity": "LOW",
            "ruleId": "9fdfec5b-afe1-4531-a8a3-61e1aa2edb91",
            "id": "7239dede-da58-4214-8bc0-275e0ba8fda5",
            "createdAt": "2022-08-11T20:30:29.789018Z",
            "state": "OPEN",
            "observations": [
                {
                    "type$": "OBSERVATION",
                    "id": "ee8560eb-99f2-4dc1-9e04-e7d5553dad46-FedEndpointExfiltration",
                    "observedAt": "2022-08-11T19:40:00.0000000Z",
                    "type": "FedEndpointExfiltration",
                    "data": '{"type$":"OBSERVED_ENDPOINT_ACTIVITY","id":"ee8560eb-99f2-4dc1-9e04-e7d5553dad46-FedEndpointExfiltration","sources":["Endpoint"],"exposureTypes":["ApplicationRead"],"exposureTypeIsSignificant":true,"firstActivityAt":"2022-08-11T19:40:00.0000000Z","lastActivityAt":"2022-08-11T19:50:00.0000000Z","fileCount":1,"totalFileSize":50661,"fileCategories":[{"type$":"OBSERVED_FILE_CATEGORY","category":"Spreadsheet","fileCount":1,"totalFileSize":50661,"isSignificant":true}],"fileCategoryIsSignificant":false,"files":[{"type$":"OBSERVED_FILE","eventId":"0_abcd-1234_1070535026524210892_1072902336271326107_0_EPS_DARWIN","path":"/Users/user/Downloads/","name":"quarterly_results.csv","category":"Spreadsheet","size":50661,"riskSeverityInfo":{"type$":"RISK_SEVERITY_INFO","score":3,"severity":"LOW","matchedRiskIndicators":[{"type$":"RISK_INDICATOR","name":"Spreadsheet","weight":0},{"type$":"RISK_INDICATOR","name":"Remote","weight":0},{"type$":"RISK_INDICATOR","name":"Slack upload","weight":3}]},"observedAt":"2022-08-11T19:43:06.8700000Z"}],"riskSeverityIsSignificant":true,"riskSeveritySummary":[{"type$":"RISK_SEVERITY_SUMMARY","severity":"LOW","numEvents":1,"summarizedRiskIndicators":[{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Remote","numEvents":1},{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Slack upload","numEvents":1},{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Spreadsheet","numEvents":1}]}],"syncToServices":[],"sendingIpAddresses":["65.29.159.48"],"isRemoteActivity":true,"appReadDetails":[{"type$":"APP_READ_DETAILS","destinationCategory":"Messaging","destinationName":"Slack"}],"destinationIsSignificant":false}',
                }
            ],
        },
        {
            "type$": "ALERT_DETAILS",
            "tenantId": "abcd-1234",
            "type": "FED_COMPOSITE",
            "name": "Test Alerts",
            "description": "",
            "actor": "user@example.com",
            "actorId": "1050590243935435820",
            "target": "N/A",
            "severity": "HIGH",
            "riskSeverity": "CRITICAL",
            "ruleId": "9fdfec5b-afe1-4531-a8a3-61e1aa2edb91",
            "id": "8bcaef3b-4aa7-46ab-85ae-a2a0191927d9",
            "createdAt": "2022-08-09T14:04:43.058721Z",
            "state": "OPEN",
            "observations": [
                {
                    "type$": "OBSERVATION",
                    "id": "d34917a2-4c31-4103-9cce-a74b6f0df6d3-FedEndpointExfiltration",
                    "observedAt": "2022-08-09T13:40:00.0000000Z",
                    "type": "FedEndpointExfiltration",
                    "data": '{"type$":"OBSERVED_ENDPOINT_ACTIVITY","id":"d34917a2-4c31-4103-9cce-a74b6f0df6d3-FedEndpointExfiltration","sources":["Endpoint"],"exposureTypes":["ApplicationRead"],"exposureTypeIsSignificant":true,"firstActivityAt":"2022-08-09T13:40:00.0000000Z","lastActivityAt":"2022-08-09T13:50:00.0000000Z","fileCount":1,"totalFileSize":15116,"fileCategories":[{"type$":"OBSERVED_FILE_CATEGORY","category":"SourceCode","fileCount":1,"totalFileSize":15116,"isSignificant":true}],"fileCategoryIsSignificant":false,"files":[{"type$":"OBSERVED_FILE","eventId":"0_abcd-1234_1070535026524210892_1072575657351027611_0_EPS","path":"/Users/user/Downloads/","name":"source.py","category":"SourceCode","size":15116,"riskSeverityInfo":{"type$":"RISK_SEVERITY_INFO","score":9,"severity":"CRITICAL","matchedRiskIndicators":[{"type$":"RISK_INDICATOR","name":"Remote","weight":0},{"type$":"RISK_INDICATOR","name":"Slack upload","weight":3},{"type$":"RISK_INDICATOR","name":"First use of destination","weight":3},{"type$":"RISK_INDICATOR","name":"Source code","weight":3}]},"observedAt":"2022-08-09T13:40:24.5640000Z"}],"riskSeverityIsSignificant":true,"riskSeveritySummary":[{"type$":"RISK_SEVERITY_SUMMARY","severity":"CRITICAL","numEvents":1,"summarizedRiskIndicators":[{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Remote","numEvents":1},{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Slack upload","numEvents":1},{"type$":"SUMMARIZED_RISK_INDICATOR","name":"Source code","numEvents":1},{"type$":"SUMMARIZED_RISK_INDICATOR","name":"First use of destination","numEvents":1}]}],"syncToServices":[],"sendingIpAddresses":["65.29.159.48"],"isRemoteActivity":true,"appReadDetails":[{"type$":"APP_READ_DETAILS","destinationCategory":"Messaging","destinationName":"Slack"}],"destinationIsSignificant":false}',
                }
            ],
            "note": {
                "type$": "NOTE",
                "id": "6867b129-7f57-4acc-9209-360e1b76f249",
                "lastModifiedAt": "2022-09-12T15:56:52.0757340Z",
                "lastModifiedBy": "key-1234",
                "message": "sdk",
            },
        },
    ],
}

TEST_DICT_QUERY = {
    "tenantId": "abcd-1234",
    "groupClause": "AND",
    "groups": [
        {
            "filterClause": "AND",
            "filters": [
                {
                    "term": "CreatedAt",
                    "operator": "ON_OR_AFTER",
                    "value": "2022-06-01T00:00:00.000Z",
                },
            ],
        },
        {
            "filterClause": "AND",
            "filters": [
                {
                    "term": "Name",
                    "operator": "IS",
                    "value": "foo",
                },
            ],
        },
        {
            "filterClause": "AND",
            "filters": [
                {
                    "term": "State",
                    "operator": "IS",
                    "value": "OPEN",
                },
            ],
        },
    ],
    "pgNum": 0,
    "pgSize": 100,
    "srtDirection": "DESC",
    "srtKey": "CreatedAt",
}

TIMESTAMP = TEST_ALERTS_RESPONSE["alerts"][0]["createdAt"]
CURSOR_TIMESTAMP = parse_ts_to_posix_ts(TIMESTAMP)


def test_alert_query_class(httpserver_auth: HTTPServer):
    query = AlertQuery().equals("State", "OPEN")
    expected = query.dict()
    expected["tenantId"] = "abcd-1234"

    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=expected
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    client = Client()
    response = client.alerts.v1.search(query)
    assert isinstance(response, AlertQueryPage)

    with pytest.raises(ValueError):
        client.alerts.v1.search(dict())


def test_iter_all_class(httpserver_auth: HTTPServer):
    query = AlertQuery().equals("State", "OPEN")
    expected = query.dict()
    expected["tenantId"] = "abcd-1234"

    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=expected
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    client = Client()
    response = client.alerts.v1.iter_all(query)
    for alert in response:
        assert isinstance(alert, AlertSummary)

    with pytest.raises(ValueError):
        next(client.alerts.v1.iter_all(dict()))


def test_alert_detail_query(httpserver_auth: HTTPServer):
    expected = {"alertIds": ["123", "234"]}
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected
    ).respond_with_json(TEST_ALERT_DETAILS_RESPONSE)

    client = Client()
    response = client.alerts.v1.get_details(["123", "234"])
    assert isinstance(response, list)
    assert isinstance(response[0], AlertDetails)


def test_alert_detail_query_single(httpserver_auth: HTTPServer):
    expected = {"alertIds": ["123"]}
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected
    ).respond_with_json(TEST_ALERT_DETAILS_RESPONSE)

    client = Client()
    response = client.alerts.v1.get_details("123")
    assert isinstance(response, list)
    assert isinstance(response[0], AlertDetails)


def test_alert_detail_query_more_than_page_limit(httpserver_auth: HTTPServer):
    alert_ids = [str(i) for i in range(1, 251)]
    page_1_ids = alert_ids[:100]
    page_2_ids = alert_ids[100:200]
    page_3_ids = alert_ids[200:]
    expected_page_1 = {"alertIds": page_1_ids}
    expected_page_2 = {"alertIds": page_2_ids}
    expected_page_3 = {"alertIds": page_3_ids}
    response_page_1 = {
        "alerts": [
            json.loads(
                AlertDetails(
                    id=i,
                    tenantId="1234",
                    type="alert",
                    createdAt=datetime.now(),
                    state="OPEN",
                ).json()
            )
            for i in page_1_ids
        ]
    }
    response_page_2 = {
        "alerts": [
            json.loads(
                AlertDetails(
                    id=i,
                    tenantId="1234",
                    type="alert",
                    createdAt=datetime.now(),
                    state="OPEN",
                ).json()
            )
            for i in page_2_ids
        ]
    }
    response_page_3 = {
        "alerts": [
            json.loads(
                AlertDetails(
                    id=i,
                    tenantId="1234",
                    type="alert",
                    createdAt=datetime.now(),
                    state="OPEN",
                ).json()
            )
            for i in page_3_ids
        ]
    }
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected_page_1
    ).respond_with_json(response_page_1)
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected_page_2
    ).respond_with_json(response_page_2)
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected_page_3
    ).respond_with_json(response_page_3)

    client = Client()
    response = client.alerts.v1.get_details(alert_ids)
    assert isinstance(response, list)
    assert isinstance(response[0], AlertDetails)
    assert len(response) == 250


def test_alert_add_note(httpserver_auth: HTTPServer):
    expected = {
        "tenantId": "abcd-1234",
        "alertId": "1234",
        "note": "test",
    }
    httpserver_auth.expect_request(
        "/v1/alerts/add-note", method="POST", json=expected
    ).respond_with_data()

    client = Client()
    response = client.alerts.v1.add_note("1234", "test")
    assert response.status_code == 200


def test_alert_change_state(httpserver_auth: HTTPServer):
    expected = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "PENDING",
        "note": None,
    }
    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=expected
    ).respond_with_data()

    client = Client()
    response = client.alerts.v1.change_state(alert_ids=["1234"], state="PENDING")
    assert response.status_code == 200


def test_alert_change_state_single(httpserver_auth: HTTPServer):
    expected = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "PENDING",
        "note": None,
    }
    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=expected
    ).respond_with_data()

    client = Client()
    response = client.alerts.v1.change_state(alert_ids="1234", state="PENDING")
    assert response.status_code == 200


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
    query = {
        "tenantId": "abcd-1234",
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "CreatedAt",
                        "operator": "ON_OR_AFTER",
                        "value": "2022-06-01T00:00:00.000Z",
                    },
                ],
            },
        ],
        "pgNum": 0,
        "pgSize": 100,
        "srtDirection": "DESC",
        "srtKey": "CreatedAt",
    }

    # Only return one alert so `cursor.replace` is only called once.
    alerts_response = TEST_ALERTS_RESPONSE.copy()
    alerts_response["alerts"] = [TEST_ALERTS_RESPONSE["alerts"][0]]
    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=query
    ).respond_with_json(alerts_response)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = None
    with mock.patch(
        "_incydr_cli.cmds.alerts._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store, mock.patch.object(
        mock_cursor, "replace"
    ) as mock_replace, mock.patch.object(
        mock_cursor, "replace_items"
    ) as mock_replace_items:
        result = runner.invoke(
            incydr,
            [
                "alerts",
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
    mock_replace.assert_called_once_with(
        "test-chkpt",
        parse_ts_to_posix_ts(TEST_ALERTS_RESPONSE["alerts"][0]["createdAt"]),
    )
    mock_replace_items.assert_called_once_with(
        "test-chkpt", [TEST_ALERTS_RESPONSE["alerts"][0]["id"]]
    )
    assert result.exit_code == 0


@format_arg
def test_cli_search_with_checkpointing_ignores_start_param_and_uses_existing_checkpoint(
    httpserver_auth, runner, mocker, format_
):
    query = {
        "tenantId": "abcd-1234",
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "CreatedAt",
                        "operator": "ON_OR_AFTER",
                        "value": TIMESTAMP[:-4] + "Z",
                    },
                ],
            },
        ],
        "pgNum": 0,
        "pgSize": 100,
        "srtDirection": "DESC",
        "srtKey": "CreatedAt",
    }

    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=query
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    mock_cursor = mocker.MagicMock(spec=CursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    with mock.patch(
        "_incydr_cli.cmds.alerts._get_cursor_store", return_value=mock_cursor
    ) as mock_get_store:
        result = runner.invoke(
            incydr,
            [
                "alerts",
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


def test_search_when_no_start_or_on_param_raises_bad_option_usage_exception(
    runner, httpserver_auth: HTTPServer
):
    result = runner.invoke(
        incydr,
        [
            "alerts",
            "search",
        ],
    )
    assert result.exit_code == 2
    assert (
        "--start, --end, or --on options are required if not using the --advanced-query option or using an existing checkpoint."
        in result.output
    )


def test_cli_alerts_search_when_default_params_makes_expected_api_call(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "tenantId": "abcd-1234",
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "CreatedAt",
                        "operator": "ON_OR_AFTER",
                        "value": "2022-06-01T00:00:00.000Z",
                    },
                ],
            },
        ],
        "pgNum": 0,
        "pgSize": 100,
        "srtDirection": "DESC",
        "srtKey": "CreatedAt",
    }

    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=query
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    result = runner.invoke(
        incydr,
        [
            "alerts",
            "search",
            "--start",
            "2022-06-01",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_alerts_search_when_custom_params_makes_expected_api_call(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "tenantId": "abcd-1234",
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "CreatedAt",
                        "operator": "ON_OR_AFTER",
                        "value": "2022-06-01T00:00:00.000Z",
                    },
                    {
                        "term": "CreatedAt",
                        "operator": "ON_OR_BEFORE",
                        "value": "2022-07-02T00:00:00.000Z",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "AlertId",
                        "operator": "IS",
                        "value": "bar",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "Type",
                        "operator": "IS",
                        "value": "alert",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "Name",
                        "operator": "IS",
                        "value": "foo",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "Actor",
                        "operator": "IS",
                        "value": "foo@bar.com",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "ActorId",
                        "operator": "IS",
                        "value": "foo-42",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "RiskSeverity",
                        "operator": "IS",
                        "value": "LOW",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "State",
                        "operator": "IS",
                        "value": "OPEN",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "RuleId",
                        "operator": "IS",
                        "value": "baz",
                    },
                ],
            },
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "term": "AlertSeverity",
                        "operator": "IS",
                        "value": "HIGH",
                    },
                ],
            },
        ],
        "pgNum": 0,
        "pgSize": 100,
        "srtDirection": "DESC",
        "srtKey": "CreatedAt",
    }

    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=query
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    result = runner.invoke(
        incydr,
        [
            "alerts",
            "search",
            "--start",
            "2022-06-01",
            "--end",
            "2022-07-02",
            "--alert-id",
            "bar",
            "--type",
            "alert",
            "--name",
            "foo",
            "--actor",
            "foo@bar.com",
            "--actor-id",
            "foo-42",
            "--risk-severity",
            "LOW",
            "--state",
            "OPEN",
            "--rule-id",
            "baz",
            "--alert-severity",
            "HIGH",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_alerts_search_when_advanced_query_makes_expected_api_call(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=TEST_DICT_QUERY
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    result = runner.invoke(
        incydr,
        ["alerts", "search", "--advanced-query", json.dumps(TEST_DICT_QUERY)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_alerts_search_when_advanced_query_from_file_makes_expected_api_call(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    httpserver_auth.expect_request(
        "/v1/alerts/query-alerts", method="POST", json=TEST_DICT_QUERY
    ).respond_with_json(TEST_ALERTS_RESPONSE)

    p = tmp_path / "query.json"
    p.write_text(json.dumps(TEST_DICT_QUERY))

    result = runner.invoke(
        incydr,
        ["alerts", "search", "--advanced-query", "@" + str(p)],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_alerts_show_makes_expected_call(httpserver_auth: HTTPServer, runner):
    expected = {"alertIds": [TEST_ALERT_ID]}
    httpserver_auth.expect_request(
        "/v1/alerts/query-details", method="POST", json=expected
    ).respond_with_json(TEST_ALERT_DETAILS_RESPONSE)

    result = runner.invoke(incydr, ["alerts", "show", TEST_ALERT_ID])
    assert result.exit_code == 0


def test_cli_alerts_add_note_makes_expected_call(httpserver_auth: HTTPServer, runner):
    expected = {
        "tenantId": "abcd-1234",
        "alertId": TEST_ALERT_ID,
        "note": "test",
    }
    httpserver_auth.expect_request(
        "/v1/alerts/add-note", method="POST", json=expected
    ).respond_with_data()

    result = runner.invoke(incydr, ["alerts", "add-note", TEST_ALERT_ID, "test"])

    assert result.exit_code == 0


def test_cli_update_state_makes_expected_call(httpserver_auth: HTTPServer, runner):
    expected = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "PENDING",
        "note": None,
    }
    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=expected
    ).respond_with_data()

    result = runner.invoke(incydr, ["alerts", "update-state", "1234", "PENDING"])

    assert result.exit_code == 0


def test_cli_bulk_update_state_when_note_column_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    data_1 = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "RESOLVED",
        "note": None,
    }
    data_2 = {
        "tenantId": "abcd-1234",
        "alertIds": ["abcd"],
        "state": "PENDING",
        "note": "test note",
    }

    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=data_1
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=data_2
    ).respond_with_data()

    p = tmp_path / "alerts.csv"
    p.write_text("alert_id,state,note\n1234,RESOLVED,\nabcd,PENDING,test note")

    result = runner.invoke(incydr, ["alerts", "bulk-update-state", str(p)])
    assert result.exit_code == 0


def test_cli_bulk_update_state_when_no_note_column_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    data_1 = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "RESOLVED",
        "note": None,
    }
    data_2 = {
        "tenantId": "abcd-1234",
        "alertIds": ["abcd"],
        "state": "PENDING",
        "note": None,
    }

    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=data_1
    ).respond_with_data()
    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=data_2
    ).respond_with_data()

    p = tmp_path / "alerts.csv"
    p.write_text("alert_id,state\n1234,RESOLVED\nabcd,PENDING")

    result = runner.invoke(incydr, ["alerts", "bulk-update-state", str(p)])
    assert result.exit_code == 0


def test_cli_bulk_update_state_when_state_and_note_options_makes_expected_calls(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    note_override = "override"
    state_override = "PENDING"
    data_1 = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234", "abcd"],
        "state": state_override,
        "note": note_override,
    }

    httpserver_auth.expect_request(
        "/v1/alerts/update-state", method="POST", json=data_1
    ).respond_with_data()

    p = tmp_path / "alerts.csv"
    p.write_text("alert_id,state,note\n1234,RESOLVED,\nabcd,OPEN,test note")

    result = runner.invoke(
        incydr,
        [
            "alerts",
            "bulk-update-state",
            str(p),
            "--state",
            state_override,
            "--note",
            note_override,
        ],
    )
    assert result.exit_code == 0


def test_cli_bulk_update_state_when_404_retries_individual_alert_ids(
    httpserver_auth: HTTPServer, runner, tmp_path
):
    data_1 = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234", "abcd", "invalid"],
        "state": "RESOLVED",
        "note": None,
    }
    data_2 = {
        "tenantId": "abcd-1234",
        "alertIds": ["1234"],
        "state": "RESOLVED",
        "note": None,
    }
    data_3 = {
        "tenantId": "abcd-1234",
        "alertIds": ["abcd"],
        "state": "RESOLVED",
        "note": None,
    }
    data_4 = {
        "tenantId": "abcd-1234",
        "alertIds": ["invalid"],
        "state": "RESOLVED",
        "note": None,
    }
    httpserver_auth.expect_ordered_request(
        "/v1/alerts/update-state", method="POST", json=data_1
    ).respond_with_data(status=404)
    httpserver_auth.expect_ordered_request(
        "/v1/alerts/update-state", method="POST", json=data_2
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        "/v1/alerts/update-state", method="POST", json=data_3
    ).respond_with_data()
    httpserver_auth.expect_ordered_request(
        "/v1/alerts/update-state", method="POST", json=data_4
    ).respond_with_data()

    p = tmp_path / "alerts.csv"
    p.write_text("alert_id,state\n1234,RESOLVED\nabcd,RESOLVED\ninvalid,RESOLVED\n")

    result = runner.invoke(
        incydr,
        [
            "alerts",
            "bulk-update-state",
            str(p),
            "--format",
            "csv",
        ],
    )
    assert result.exit_code == 0
    httpserver_auth.check()
