import pytest

import logging
from incydr.cli.logger import _init_logger
from incydr.cli.logger import get_logger_for_server
from incydr.cli.logger.enums import ServerProtocol
from incydr.cli.logger.handlers import NoPrioritySysLogHandler


@pytest.fixture(autouse=True)
def init_socket_mock(mocker):
    return mocker.patch("incydr.cli.logger.NoPrioritySysLogHandler.connect_socket")


@pytest.fixture(autouse=True)
def fresh_syslog_handler(init_socket_mock):
    # Set handlers to empty list so it gets initialized each test
    get_logger_for_server(
        ServerProtocol.TCP,
        "example.com",
        None,
        None,
    ).handlers = []
    init_socket_mock.call_count = 0


def test_init_logger_does_as_expected():
    logger = logging.getLogger("TEST_INCYDR_CLI")
    handler = logging.Handler()
    _init_logger(logger, handler)
    assert handler in logger.handlers
    assert isinstance(handler.formatter, logging.Formatter)


def test_get_logger_for_server_has_info_level():
    logger = get_logger_for_server(ServerProtocol.TCP, "example.com", None, None)
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_called_twice_only_has_one_handler():
    get_logger_for_server(ServerProtocol.TCP, "example.com", None, None)
    logger = get_logger_for_server(ServerProtocol.TCP, "example.com", None, None)
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler():
    logger = get_logger_for_server(ServerProtocol.TCP, "example.com", None, None)
    assert type(logger.handlers[0]) == NoPrioritySysLogHandler


def test_get_logger_for_server_constructs_handler_with_expected_args(
    mocker, monkeypatch
):
    no_priority_syslog_handler = mocker.patch(
        "incydr.cli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(ServerProtocol.TCP, "example.com", None, "cert")
    no_priority_syslog_handler.assert_called_once_with(
        "example.com", 601, ServerProtocol.TCP.value, "cert"
    )


def test_get_logger_for_server_when_hostname_includes_port_constructs_handler_with_expected_args(
    mocker,
):
    no_priority_syslog_handler = mocker.patch(
        "incydr.cli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(ServerProtocol.TCP, "example.com", 999, None)
    no_priority_syslog_handler.assert_called_once_with(
        "example.com",
        999,
        ServerProtocol.TCP.value,
        None,
    )


def test_get_logger_for_server_inits_socket(init_socket_mock):
    get_logger_for_server(ServerProtocol.TCP, "example.com", None, None)
    assert init_socket_mock.call_count == 1
