# prevent loggers from printing stacks to stderr if a pipe is broken
import logging
from threading import Lock

import click

from incydr.cli.logger.enums import ServerProtocol
from incydr.cli.logger.handlers import NoPrioritySysLogHandler

logging.raiseExceptions = False

logger_deps_lock = Lock()


def _init_logger(logger, handler):
    logger.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter())
    logger.addHandler(handler)
    return logger


def get_logger_for_server(protocol, hostname, port, certs):
    """Gets the logger that sends logs to a server..

    Args:
        hostname: The hostname of the server. It may include the port.
        protocol: The transfer protocol for sending logs.
        certs: Use for passing SSL/TLS certificates when connecting to the server.
    """
    logger = logging.getLogger("incydr_syslog")
    if len(logger.handlers):  # if logger has handlers
        return logger.handlers

    with logger_deps_lock:
        hostname = hostname
        port = port or 514
        if not len(logger.handlers):
            handler = NoPrioritySysLogHandler(hostname, port, protocol, certs)
            handler.connect_socket()
            return _init_logger(logger, handler)
    return logger


def try_get_logger_for_server(output, certs, ignore_cert_validation):

    # parse output
    output = output.split(":")
    protocol = output[0].upper()  # TODO
    hostname = output[1]
    port = 514
    if len(output) > 1 and output[2] != "":
        port = int(output[2])

    # certs and ignore-cert-validation only compatible with TLS_TCP
    if protocol != ServerProtocol.TLS_TCP:
        arg = None
        if ignore_cert_validation:
            arg = ("ignore-cert-validation",)
        elif certs is not None:
            arg = "certs"
        if arg is not None:
            raise click.BadOptionUsage(
                arg,
                f"'{arg}' can only be used with '--protocol {ServerProtocol.TLS_TCP}'.",
            )

    if ignore_cert_validation:
        certs = "ignore"

    try:
        return get_logger_for_server(protocol, hostname, port, certs)
    except Exception as err:
        raise ConnectionError(
            f"Unable to connect to {hostname}. Failed with error: {err}."
        )
