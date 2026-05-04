import json
from csv import DictReader
from io import StringIO
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli import render as render_module
from _incydr_cli.cmds import risk_indicator_categories as risk_indicator_categories_cmd
from _incydr_cli.main import incydr
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.risk_indicator_categories.models import (
    RiskIndicatorCategoriesResponsePage,
)
from _incydr_sdk.risk_indicator_categories.models import RiskIndicatorCategory
from _incydr_sdk.risk_indicator_categories.models import RiskIndicatorSubcategory
from incydr import Client

TEST_CATEGORY_ID = "cat-1"
TEST_SUBCATEGORY_ID = "sub-1"

TEST_INDICATOR_STANDARD = {
    "id": "ind-std-1",
    "name": "Standard indicator",
    "description": "Standard description",
}

TEST_INDICATOR_CUSTOM = {
    "id": "ind-cust-1",
    "name": "Custom indicator",
    "description": None,
}

TEST_SUBCATEGORY_PAYLOAD = {
    "id": TEST_SUBCATEGORY_ID,
    "name": "Cloud storage",
    "description": "Cloud-related indicators",
    "standardIndicators": [TEST_INDICATOR_STANDARD],
    "customIndicators": [TEST_INDICATOR_CUSTOM],
}

TEST_CATEGORY_PAYLOAD = {
    "id": TEST_CATEGORY_ID,
    "name": "Data exfiltration",
    "description": "Category description",
    "subcategories": [TEST_SUBCATEGORY_PAYLOAD],
}

TEST_LIST_RESPONSE = {"categories": [TEST_CATEGORY_PAYLOAD]}


def test_list_categories_when_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request("/v1/risk-indicator-categories").respond_with_json(
        TEST_LIST_RESPONSE
    )

    client = Client()
    page = client.risk_indicator_categories.v1.list_categories()
    assert isinstance(page, RiskIndicatorCategoriesResponsePage)
    assert len(page.categories) == 1
    cat = page.categories[0]
    assert isinstance(cat, RiskIndicatorCategory)
    assert cat.json() == json.dumps(TEST_CATEGORY_PAYLOAD, separators=(",", ":"))


def test_list_categories_when_active_and_sort_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = urlencode({"isActive": True, "sort_direction": SortDirection.ASC.value})
    httpserver_auth.expect_request(
        "/v1/risk-indicator-categories", query_string=query
    ).respond_with_json(TEST_LIST_RESPONSE)

    client = Client()
    page = client.risk_indicator_categories.v1.list_categories(
        active=True, sort_direction=SortDirection.ASC
    )
    assert isinstance(page, RiskIndicatorCategoriesResponsePage)
    assert page.categories[0].id == TEST_CATEGORY_ID


def test_get_category_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/risk-indicator-categories/{TEST_CATEGORY_ID}"
    ).respond_with_json(TEST_CATEGORY_PAYLOAD)

    client = Client()
    category = client.risk_indicator_categories.v1.get_category(TEST_CATEGORY_ID)
    assert isinstance(category, RiskIndicatorCategory)
    assert category.json() == json.dumps(TEST_CATEGORY_PAYLOAD, separators=(",", ":"))


def test_get_subcategory_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/risk-indicator-categories/{TEST_CATEGORY_ID}/subcategories/{TEST_SUBCATEGORY_ID}"
    ).respond_with_json(TEST_SUBCATEGORY_PAYLOAD)

    client = Client()
    sub = client.risk_indicator_categories.v1.get_subcategory(
        TEST_CATEGORY_ID, TEST_SUBCATEGORY_ID
    )
    assert isinstance(sub, RiskIndicatorSubcategory)
    assert sub.json() == json.dumps(TEST_SUBCATEGORY_PAYLOAD, separators=(",", ":"))


# ************************************************ CLI ************************************************


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/risk-indicator-categories", method="GET"
    ).respond_with_json(TEST_LIST_RESPONSE)

    result = runner.invoke(incydr, ["risk-indicator-categories", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0
    assert "Data exfiltration" in result.output
    assert "Cloud storage" in result.output
    assert "Standard indicator" in result.output
    assert "Custom indicator" in result.output


def test_cli_list_json_lines_outputs_one_record_per_indicator(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/risk-indicator-categories", method="GET"
    ).respond_with_json(TEST_LIST_RESPONSE)

    result = runner.invoke(
        incydr, ["risk-indicator-categories", "list", "-f", "json-lines"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0
    lines = [ln for ln in result.output.strip().splitlines() if ln.strip()]
    assert len(lines) == 2
    rows = [json.loads(ln) for ln in lines]
    by_id = {r["id"]: r for r in rows}
    assert by_id["ind-std-1"]["type"] == "standard"
    assert by_id["ind-std-1"]["category_name"] == "Data exfiltration"
    assert by_id["ind-std-1"]["subcategory_name"] == "Cloud storage"
    assert by_id["ind-cust-1"]["type"] == "custom"
    assert by_id["ind-cust-1"]["description"] is None


def test_cli_list_csv_outputs_header_and_indicator_rows(
    httpserver_auth: HTTPServer, runner, monkeypatch
):
    """CSV uses render.csv default file= bound at import time; patch so output is readable."""
    buf = StringIO()
    real_csv = render_module.csv

    def csv_to_buffer(model, models, columns=None, flat=False, file=None):
        return real_csv(model, models, columns=columns, flat=flat, file=buf)

    monkeypatch.setattr(risk_indicator_categories_cmd.render, "csv", csv_to_buffer)

    httpserver_auth.expect_request(
        "/v1/risk-indicator-categories", method="GET"
    ).respond_with_json(TEST_LIST_RESPONSE)

    result = runner.invoke(incydr, ["risk-indicator-categories", "list", "-f", "csv"])
    httpserver_auth.check()
    assert result.exit_code == 0
    reader = DictReader(StringIO(buf.getvalue()))
    rows = list(reader)
    assert len(rows) == 2
    by_id = {r["id"]: r for r in rows}
    assert by_id["ind-std-1"]["type"] == "standard"
    assert by_id["ind-cust-1"]["type"] == "custom"
    assert by_id["ind-std-1"]["category_name"] == "Data exfiltration"


@pytest.mark.parametrize("format_", ["table", "csv", "json-pretty", "json-lines"])
def test_cli_list_when_empty_returns_no_results(
    httpserver_auth: HTTPServer, runner, format_
):
    httpserver_auth.expect_request(
        "/v1/risk-indicator-categories", method="GET"
    ).respond_with_json({"categories": []})

    result = runner.invoke(incydr, ["risk-indicator-categories", "list", "-f", format_])
    httpserver_auth.check()
    assert result.exit_code == 0
    assert "No results found" in result.output
