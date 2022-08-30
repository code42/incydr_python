import logging

import pytest
from incydr import Client
from rich.logging import RichHandler
from pytest_httpserver import HTTPServer


class TestLogLevels:
    @pytest.mark.parametrize(
        "level_string,expected",
        [
            ("ERROR", logging.ERROR),
            ("WARNING", logging.WARNING),
            ("WARN", logging.WARN),
            ("INFO", logging.INFO),
            ("DEBUG", logging.DEBUG),
        ],
    )
    def test_env_var_sets_logging(
        self, httpserver_auth: HTTPServer, monkeypatch, capsys, level_string, expected
    ):
        monkeypatch.setenv("incydr_log_level", level_string)
        client = Client()
        captured = capsys.readouterr()
        assert client.settings.log_level == expected
        assert client.settings.logger.getEffectiveLevel() == expected
        if expected < logging.INFO:
            assert "DEBUG    POST /v1/oauth HTTP/1.1" in captured.err

    def test_modifying_log_level_setting_affects_logging(
        self, httpserver_auth: HTTPServer, capsys
    ):
        client = Client()
        assert client.settings.log_level == logging.WARNING

        client.settings.logger.info("SHOULD NOT LOG")
        captured = capsys.readouterr()
        assert captured.err == ""

        client.settings.log_level = "DEBUG"
        client.settings.logger.info("INFO SHOULD LOG")
        client.settings.logger.debug("DEBUG SHOULD LOG")
        captured = capsys.readouterr()
        assert client.settings.logger.getEffectiveLevel() == logging.DEBUG
        assert "INFO SHOULD LOG" in captured.err
        assert "DEBUG SHOULD LOG" in captured.err


class TestRich:
    @pytest.mark.parametrize("false_value", ["false", "False", 0])
    def test_env_var_disables_rich(
        httpserver_auth: HTTPServer, monkeypatch, capsys, false_value
    ):
        monkeypatch.setenv("incydr_use_rich", false_value)
        client = Client()
        assert not client.settings.use_rich
        for handler in client.settings.logger.handlers:
            assert not isinstance(handler, RichHandler)

    def test_modifying_use_rich_setting_affects_logging(
        self, httpserver_auth: HTTPServer, capsys, caplog
    ):
        client = Client()
        client.settings.use_rich = False
        client.settings.logger.warning("Should not match Rich format.")
        captured = capsys.readouterr()
        assert captured.err == ""  #
