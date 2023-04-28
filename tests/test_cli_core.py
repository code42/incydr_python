from _incydr_cli.main import incydr


def test_cli_auth_missing_error_prints_missing_vars(runner, monkeypatch):
    monkeypatch.setenv("INCYDR_URL", "http://localhost")
    monkeypatch.setenv("INCYDR_API_CLIENT_ID", "key-1234")
    result = runner.invoke(incydr, ["users", "list"])
    assert "Missing authentication variables in environment." in result.output
    assert "INCYDR_API_CLIENT_SECRET" in result.output
    assert "INCYDR_URL" not in result.output
    assert "INCYDR_API_CLIENT_ID" not in result.output
