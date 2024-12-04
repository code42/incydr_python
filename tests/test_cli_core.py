from typing import Optional

import pytest

from _incydr_cli.main import incydr


def test_cli_auth_missing_error_prints_missing_vars(runner, monkeypatch):
    monkeypatch.setenv("INCYDR_URL", "http://localhost")
    monkeypatch.setenv("INCYDR_API_CLIENT_ID", "key-1234")
    result = runner.invoke(incydr, ["users", "list"])
    assert "Missing authentication variables in environment." in result.output
    assert "INCYDR_API_CLIENT_SECRET" in result.output
    assert "INCYDR_URL" not in result.output
    assert "INCYDR_API_CLIENT_ID" not in result.output


@pytest.mark.disable_autouse
def test_cli_user_agent(runner, httpserver_auth):
    def starts_with_matcher(
        header_name: str, actual: Optional[str], expected: str
    ) -> bool:
        if actual is None:
            return False

        return actual.startswith(expected)

    httpserver_auth.expect_ordered_request(
        "/v1/users",
        method="GET",
        headers={"User-Agent": "incydrCLI"},
        header_value_matcher=starts_with_matcher,
    ).respond_with_json({"users": [], "totalCount": 0})
    result = runner.invoke(
        incydr, ["users", "list", "--log-stderr", "--log-level", "DEBUG"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0
    assert "No results found" in result.output
