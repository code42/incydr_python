import logging
import re
import sys

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
        self, httpserver_auth: HTTPServer, capsys
    ):
        client = Client()

        client.settings.use_rich = False
        client.settings.logger.warning("Log should not match Rich format.")
        captured = capsys.readouterr()
        match = re.search(
            r"]\s+-\s+incydr:WARNING\s+-\s+Log should not match Rich format.$",
            captured.err,
        )
        assert match is not None

        client.settings.use_rich = True
        client.settings.logger.warning("Log should match Rich format.")
        captured = capsys.readouterr()
        current_file = __file__.split('/')[-1]
        match = re.search(
            rf"]\s+WARNING\s+Log should match Rich format.\s+{current_file}:\d+$",
            captured.err,
        )
        assert match is not None

    def test_modifying_use_rich_setting_affects_console_repr(
        self, httpserver_auth: HTTPServer, capsys
    ):
        # the rich.pretty.install() function replaces sys.displayhook, which is used to print objects in a python
        # console. The rich version looks for __rich_repr__ method on objects to help with pretty printing, so we can
        # check to see if that output is printed to determine if rich is active or not
        class TestRepr:
            def __rich_repr__(self):
                yield "<rich>"

        class_with_rich_repr = TestRepr()
        client = Client()

        client.settings.use_rich = False
        sys.displayhook(class_with_rich_repr)
        captured = capsys.readouterr()
        assert ".TestRepr object at" in captured.out

        client.settings.use_rich = True
        sys.displayhook(class_with_rich_repr)
        captured = capsys.readouterr()
        assert "TestRepr('<rich>')" in captured.out
