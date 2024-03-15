import json
from datetime import datetime
from urllib.parse import urlencode

import pytest
import requests
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from incydr import Client
from incydr.enums import SortDirection
from incydr.enums.agents import SortKeys
from incydr.models import Agent
from incydr.models import AgentsPage

TEST_AGENT_ID = "agent-1"

TEST_AGENT_1 = {
    "agentId": TEST_AGENT_ID,
    "name": "DESKTOP-H6V9R95",
    "userId": "user-1",
    "osHostname": "DESKTOP-H6V9R95",
    "osName": "Win",
    "machineId": "123",
    "serialNumber": "A12B34",
    "active": True,
    "agentType": "COMBINED",
    "agentHealthIssueTypes": ["NOT_CONNECTING"],
    "appVersion": "1.0",
    "productVersion": "2.0",
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "externalReference": None,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}


TEST_AGENT_2 = {
    "agentId": TEST_AGENT_ID,
    "name": "DESKTOP-H6V9R95",
    "userId": "user-1",
    "osHostname": "DESKTOP-H6V9R95",
    "osName": "Win",
    "machineId": "456",
    "serialNumber": "A45B67",
    "active": True,
    "agentType": "COMBINED",
    "agentHealthIssueTypes": [],
    "appVersion": "1.0",
    "productVersion": "2.0",
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "externalReference": None,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}

TEST_AGENT_3 = {
    "agentId": TEST_AGENT_ID,
    "name": "DESKTOP-H6V9R95",
    "userId": "user-1",
    "osHostname": "DESKTOP-H6V9R95",
    "osName": "Win",
    "machineId": "1",
    "serialNumber": "C42",
    "active": True,
    "agentType": "COMBINED",
    "agentHealthIssueTypes": [],
    "appVersion": "1.0",
    "productVersion": "2.0",
    "lastConnected": "2022-07-14T17:05:44.524000Z",
    "externalReference": None,
    "creationDate": "2022-07-14T16:49:11.166000Z",
    "modificationDate": "2022-07-14T17:05:44.524000Z",
}


@pytest.fixture
def mock_get_all_agents_default(httpserver_auth: HTTPServer):
    query = {
        "srtKey": "NAME",
        "srtDir": "ASC",
        "pageSize": 500,
        "page": 1,
    }
    agents_data = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 2,
        "pageSize": 500,
        "page": 1,
    }
    httpserver_auth.expect_request(
        "/v1/agents", method="GET", query_string=urlencode(query)
    ).respond_with_json(agents_data)


@pytest.fixture
def mock_get_agent(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/agents/{TEST_AGENT_ID}", method="GET"
    ).respond_with_json(TEST_AGENT_1)


def test_get_agent_returns_expected_data(mock_get_agent):
    client = Client()
    agent = client.agents.v1.get_agent("agent-1")
    assert isinstance(agent, Agent)
    assert agent.agent_id == "agent-1"
    assert agent.json() == json.dumps(TEST_AGENT_1)

    # test timestamp conversion
    assert agent.last_connected == datetime.fromisoformat(
        TEST_AGENT_1["lastConnected"].replace("Z", "+00:00")
    )
    assert agent.creation_date == datetime.fromisoformat(
        TEST_AGENT_1["creationDate"].replace("Z", "+00:00")
    )
    assert agent.modification_date == datetime.fromisoformat(
        TEST_AGENT_1["modificationDate"].replace("Z", "+00:00")
    )


def test_get_page_when_default_query_params_returns_expected_data(
    mock_get_all_agents_default,
):
    client = Client()
    page = client.agents.v1.get_page()
    assert isinstance(page, AgentsPage)
    assert page.agents[0].json() == json.dumps(TEST_AGENT_1)
    assert page.agents[1].json() == json.dumps(TEST_AGENT_2)
    assert page.total_count == len(page.agents) == 2


def test_get_page_when_custom_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "active": True,
        "srtKey": "LAST_CONNECTED",
        "srtDir": "DESC",
        "pageSize": 10,
        "page": 2,
    }

    agents_data = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 2,
        "pageSize": 10,
        "page": 2,
    }
    httpserver_auth.expect_request(
        uri="/v1/agents", method="GET", query_string=urlencode(query)
    ).respond_with_json(agents_data)

    client = Client()
    page = client.agents.v1.get_page(
        active=True,
        page_num=2,
        page_size=10,
        sort_dir=SortDirection.DESC,
        sort_key=SortKeys.LAST_CONNECTED,
    )
    assert isinstance(page, AgentsPage)
    assert page.agents[0].json() == json.dumps(TEST_AGENT_1)
    assert page.agents[1].json() == json.dumps(TEST_AGENT_2)
    assert page.total_count == len(page.agents) == 2


def test_iter_all_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query_1 = {
        "srtKey": "NAME",
        "srtDir": "ASC",
        "pageSize": 2,
        "page": 1,
    }
    query_2 = {
        "srtKey": "NAME",
        "srtDir": "ASC",
        "pageSize": 2,
        "page": 2,
    }

    agents_data_1 = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 3,
        "pageSize": 2,
        "page": 1,
    }
    agents_data_2 = {
        "agents": [TEST_AGENT_3],
        "totalCount": 3,
        "pageSize": 2,
        "page": 2,
    }

    httpserver_auth.expect_ordered_request(
        "/v1/agents", method="GET", query_string=urlencode(query_1)
    ).respond_with_json(agents_data_1)
    httpserver_auth.expect_ordered_request(
        "/v1/agents", method="GET", query_string=urlencode(query_2)
    ).respond_with_json(agents_data_2)

    client = Client()
    iterator = client.agents.v1.iter_all(page_size=2)
    total_agents = 0
    expected_agents = [TEST_AGENT_1, TEST_AGENT_2, TEST_AGENT_3]
    for item in iterator:
        total_agents += 1
        assert isinstance(item, Agent)
        assert item.json() == json.dumps(expected_agents.pop(0))
    assert total_agents == 3


def test_update_makes_expected_request(httpserver_auth: HTTPServer):
    agent_id = "1234"
    new_name = "new"
    new_reference = "new_ref"
    httpserver_auth.expect_request(
        f"/v1/agents/{agent_id}",
        method="PUT",
        json={"name": new_name, "externalReference": new_reference},
    ).respond_with_data(status=204)
    client = Client()
    response = client.agents.v1.update(
        agent_id, name=new_name, external_reference=new_reference
    )
    assert isinstance(response, requests.Response)


def test_activate_makes_expected_request(httpserver_auth: HTTPServer):
    agent_ids = ["1234", "5678"]
    httpserver_auth.expect_request(
        "/v1/agents/activate",
        method="POST",
        json={"agentIds": agent_ids},
    ).respond_with_data(status=204)
    client = Client()
    response = client.agents.v1.activate(agent_ids)
    assert isinstance(response, requests.Response)


def test_deactivate_makes_expected_request(httpserver_auth: HTTPServer):
    agent_ids = ["1234", "5678"]
    httpserver_auth.expect_request(
        "/v1/agents/deactivate",
        method="POST",
        json={"agentIds": agent_ids},
    ).respond_with_data(status=204)
    client = Client()
    response = client.agents.v1.deactivate(agent_ids)
    assert isinstance(response, requests.Response)


# ************************************************ CLI ************************************************


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_all_agents_default
):
    result = runner.invoke(incydr, ["agents", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "active": True,
        "agentHealthy": True,
        "srtKey": "NAME",
        "srtDir": "ASC",
        "pageSize": 500,
        "page": 1,
    }

    agents_data = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 2,
        "pageSize": 500,
        "page": 1,
    }
    httpserver_auth.expect_request(
        uri="/v1/agents", method="GET", query_string=urlencode(query)
    ).respond_with_json(agents_data)

    result = runner.invoke(incydr, ["agents", "list", "--active", "--healthy"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_unhealthy_option_passed_with_default_value_passes_no_issue_types(
    httpserver_auth: HTTPServer, runner
):
    query = {
        "agentHealthy": False,
        "srtKey": "NAME",
        "srtDir": "ASC",
        "pageSize": 500,
        "page": 1,
    }

    agents_data = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 2,
        "pageSize": 500,
        "page": 1,
    }
    httpserver_auth.expect_request(
        uri="/v1/agents", method="GET", query_string=urlencode(query)
    ).respond_with_json(agents_data)

    result = runner.invoke(incydr, ["agents", "list", "--unhealthy"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_unhealthy_option_passed_with_string_parses_issue_types_correctly(
    httpserver_auth: HTTPServer, runner
):
    query = [
        ("agentHealthy", False),
        ("anyOfAgentHealthIssueTypes", "NOT_CONNECTED"),
        ("anyOfAgentHealthIssueTypes", "TEST_VALUE"),
        ("srtKey", "NAME"),
        ("srtDir", "ASC"),
        ("pageSize", 500),
        ("page", 1),
    ]

    agents_data = {
        "agents": [TEST_AGENT_1, TEST_AGENT_2],
        "totalCount": 2,
        "pageSize": 500,
        "page": 1,
    }
    httpserver_auth.expect_request(
        uri="/v1/agents", method="GET", query_string=urlencode(query)
    ).respond_with_json(agents_data)

    result = runner.invoke(
        incydr, ["agents", "list", "--unhealthy", "NOT_CONNECTED,TEST_VALUE"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_agent
):
    result = runner.invoke(incydr, ["agents", "show", TEST_AGENT_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_bulk_activate_CSV_file_input(httpserver_auth: HTTPServer, runner):
    csv_lines = (
        "agent_id,some_extra_column\n",
        "1234,not_relevant\n",
        "2345,extra_data\n",
    )

    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)

    with runner.isolated_filesystem():
        with open("tmpfile", "w") as tmpfile:
            tmpfile.writelines(csv_lines)
        result = runner.invoke(incydr, ["agents", "bulk-activate", "tmpfile"])
        httpserver_auth.check()
        assert "Activating agents..." in result.output


def test_cli_bulk_activate_JSON_file_input(httpserver_auth: HTTPServer, runner):
    json_lines = (
        {"agent_id": "1234", "extra": "not_relevant"},
        {"agentId": "2345", "extra": "ignore"},
    )

    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)

    with runner.isolated_filesystem():
        with open("tmpfile", "w") as tmpfile:
            for line in json_lines:
                json.dump(line, tmpfile)
                tmpfile.write("\n")
        result = runner.invoke(
            incydr, ["agents", "bulk-activate", "--format", "json-lines", "tmpfile"]
        )
        httpserver_auth.check()
        assert "Activating agents..." in result.output


def test_cli_bulk_deactivate_CSV_file_input(httpserver_auth: HTTPServer, runner):
    csv_lines = (
        "agent_id,some_extra_column\n",
        "1234,not_relevant\n",
        "2345,extra_data\n",
    )

    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)

    with runner.isolated_filesystem():
        with open("tmpfile", "w") as tmpfile:
            tmpfile.writelines(csv_lines)
        result = runner.invoke(incydr, ["agents", "bulk-deactivate", "tmpfile"])
        httpserver_auth.check()
        assert "Deactivating agents..." in result.output


def test_cli_bulk_deactivate_JSON_file_input(httpserver_auth: HTTPServer, runner):
    json_lines = (
        {"agent_id": "1234", "extra": "not_relevant"},
        {"agentId": "2345", "extra": "ignore"},
    )

    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)

    with runner.isolated_filesystem():
        with open("tmpfile", "w") as tmpfile:
            for line in json_lines:
                json.dump(line, tmpfile)
                tmpfile.write("\n")
        result = runner.invoke(
            incydr, ["agents", "bulk-deactivate", "--format", "json-lines", "tmpfile"]
        )
        httpserver_auth.check()
        assert "Deactivating agents..." in result.output


def test_cli_bulk_activate_retries_with_agent_ids_not_found_removed(
    httpserver_auth: HTTPServer, runner
):
    input_lines = "\n".join(("agent_id", "1234", "5678", "2345", "9876"))

    httpserver_auth.expect_request(
        uri="/v1/agents/activate",
        method="POST",
        json={"agentIds": ["1234", "5678", "2345", "9876"]},
    ).respond_with_json(response_json={"agentsNotFound": ["5678", "9876"]}, status=404)
    # order of agentIds in CLI requests aren't deterministic for retries because of usage of sets
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["2345", "1234"]}
    ).respond_with_data(status=204)

    result = runner.invoke(
        incydr, ["agents", "bulk-activate", "--format", "csv", "-"], input=input_lines
    )
    assert (
        "404 Error processing batch of 4 agent activations, agent_ids not found: ['5678', '9876']"
        in result.output
    )
    assert "Activating agents..." in result.output


def test_cli_bulk_activate_retries_ids_individually_when_unknown_error_occurs(
    httpserver_auth: HTTPServer, runner
):
    input_lines = "\n".join(("agent_id", "1234", "5678", "2345", "9876"))

    httpserver_auth.expect_request(
        uri="/v1/agents/activate",
        method="POST",
        json={"agentIds": ["1234", "5678", "2345", "9876"]},
    ).respond_with_data(response_data="Unknown Server Error", status=500)
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["1234"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["2345"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["5678"]}
    ).respond_with_data(response_data="Unknown Server Error", status=500)
    httpserver_auth.expect_request(
        uri="/v1/agents/activate", method="POST", json={"agentIds": ["9876"]}
    ).respond_with_data(status=204)

    result = runner.invoke(
        incydr, ["agents", "bulk-activate", "--format", "csv", "-"], input=input_lines
    )
    assert "Unknown error processing batch of 4 agent activations" in result.output
    assert "Trying agent activation for this batch individually" in result.output
    assert "Activating agents..." in result.output
    assert (
        "Failed to process activation for 5678: Unknown Server Error" in result.output
    )


def test_cli_bulk_deactivate_retries_with_agent_ids_not_found_removed(
    httpserver_auth: HTTPServer, runner
):
    input_lines = "\n".join(("agent_id", "1234", "5678", "2345", "9876"))

    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate",
        method="POST",
        json={"agentIds": ["1234", "5678", "2345", "9876"]},
    ).respond_with_json(response_json={"agentsNotFound": ["5678", "9876"]}, status=404)
    # order of agentIds in CLI requests aren't deterministic for retries because of usage of sets
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["1234", "2345"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["2345", "1234"]}
    ).respond_with_data(status=204)

    result = runner.invoke(
        incydr, ["agents", "bulk-deactivate", "--format", "csv", "-"], input=input_lines
    )
    assert (
        "404 Error processing batch of 4 agent deactivations, agent_ids not found: ['5678', '9876']"
        in result.output
    )
    assert "Deactivating agents..." in result.output


def test_cli_bulk_deactivate_retries_ids_individually_when_unknown_error_occurs(
    httpserver_auth: HTTPServer, runner
):
    input_lines = "\n".join(("agent_id", "1234", "5678", "2345", "9876"))

    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate",
        method="POST",
        json={"agentIds": ["1234", "5678", "2345", "9876"]},
    ).respond_with_data(response_data="Unknown Server Error", status=500)
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["1234"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["2345"]}
    ).respond_with_data(status=204)
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["5678"]}
    ).respond_with_data(response_data="Unknown Server Error", status=500)
    httpserver_auth.expect_request(
        uri="/v1/agents/deactivate", method="POST", json={"agentIds": ["9876"]}
    ).respond_with_data(status=204)

    result = runner.invoke(
        incydr, ["agents", "bulk-deactivate", "--format", "csv", "-"], input=input_lines
    )
    assert "Unknown error processing batch of 4 agent deactivations" in result.output
    assert "Trying agent deactivation for this batch individually" in result.output
    assert "Deactivating agents..." in result.output
    assert (
        "Failed to process deactivation for 5678: Unknown Server Error" in result.output
    )
