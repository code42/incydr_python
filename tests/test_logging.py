import logging
import re
import sys

import pytest
from incydr import Client
from pytest_httpserver import HTTPServer
from rich.logging import RichHandler


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
        client = Client(log_stderr=True)
        captured = capsys.readouterr()
        assert client.settings.log_level == expected
        assert client.settings.logger.getEffectiveLevel() == expected
        if expected < logging.INFO:
            assert "DEBUG    POST /v1/oauth HTTP/1.1" in captured.err

    @pytest.mark.parametrize(
        ["env_level", "init_level", "expected"],
        [
            ("INFO", "DEBUG", logging.DEBUG),
            ("INFO", "ERROR", logging.ERROR),
            ("INFO", "WARNING", logging.WARNING),
            ("WARNING", "INFO", logging.INFO),
        ],
    )
    def test_init_param_overrides_env_var(
        self, httpserver_auth: HTTPServer, monkeypatch, env_level, init_level, expected
    ):
        monkeypatch.setenv("incydr_log_level", env_level)
        client = Client(log_level=init_level, log_stderr=False)
        assert client.settings.log_level == expected

    def test_modifying_log_level_setting_affects_logging(
        self, httpserver_auth: HTTPServer, capsys, tmp_path
    ):
        client = Client(log_stderr=True)
        client.settings.log_file = tmp_path / "test.log"
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
    @pytest.mark.parametrize("false_value", ["false", "False", "0"])
    def test_env_var_disables_rich(
        self, httpserver_auth: HTTPServer, monkeypatch, capsys, false_value
    ):
        monkeypatch.setenv("incydr_use_rich", false_value)
        client = Client()
        assert not client.settings.use_rich
        for handler in client.settings.logger.handlers:
            assert not isinstance(handler, RichHandler)

    def test_modifying_use_rich_setting_affects_logging(
        self, httpserver_auth: HTTPServer, capsys
    ):
        client = Client(log_stderr=True)
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
        current_file = __file__.split("/")[-1]
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


class TestLoggers:
    def test_setting_file_logger(self, httpserver_auth: HTTPServer, tmp_path):
        log_file_1 = tmp_path / "incydr_test.log"
        log_file_2 = tmp_path / "incydr_test2.log"

        client = Client(log_file=log_file_1)
        client.settings.log_level = "INFO"
        client.settings.logger.info("Should log to file 1.")
        assert "Should log to file 1." in log_file_1.read_text()

        client.settings.log_file = log_file_2
        client.settings.logger.info("Should log to file 2.")
        assert "Should log to file 2." not in log_file_1.read_text()
        assert "Should log to file 2." in log_file_2.read_text()

    def test_setting_log_file_and_stderr_env_vars(
        self, httpserver_auth: HTTPServer, tmp_path, monkeypatch, capsys
    ):
        log_file = tmp_path / "test.log"
        monkeypatch.setenv("incydr_log_file", str(log_file))
        monkeypatch.setenv("incydr_log_stderr", "false")

        client = Client()
        client.settings.log_level = "INFO"
        client.settings.logger.info("Should log to file.")
        captured = capsys.readouterr()
        assert captured.err == ""
        assert "Should log to file." in log_file.read_text()

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_setting_custom_logger(self, httpserver_auth: HTTPServer, tmp_path):
        test_logger = logging.getLogger("test_logger_1")
        log_file = tmp_path / "log1.log"
        handler = logging.FileHandler(filename=str(log_file.absolute()))
        test_logger.addHandler(handler)

        client = Client(logger=test_logger)
        assert len(client.settings.logger.handlers) == 1
        client.settings.logger.warning("Should go to log file.")
        assert "Should go to log file." in log_file.read_text()
        with pytest.warns(UserWarning):
            client.settings.log_stderr = False
        with pytest.warns(UserWarning):
            client.settings.use_rich = False
        with pytest.warns(UserWarning):
            client.settings.log_file = "test"

    def test_setting_stderr_logger(self, httpserver_auth: HTTPServer, capsys):
        client = Client(log_stderr=True, log_level="INFO")
        client.settings.logger.info("Should log to stderr.")
        captured = capsys.readouterr()
        assert "Should log to stderr." in captured.err
        client.settings.log_stderr = False
        client.settings.logger.info("Should not log to stderr.")
        captured = capsys.readouterr()
        assert "Should not log to stderr." not in captured.err
