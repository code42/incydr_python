# prevent loggers from printing stacks to stderr if a pipe is broken
import logging
from threading import Lock

import click
from _cli.logger.enums import ServerProtocol
from _cli.logger.handlers import NoPrioritySysLogHandler
from click import BadOptionUsage

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


def get_server_logger(output, certs, ignore_cert_validation):

    # parse output
    output = output.split(":")

    protocol = ServerProtocol.UDP
    port = 514

    if len(output) == 1:  # HOSTNAME
        hostname = output[0]
    elif len(output) == 2:  # HOSTNAME:PORT
        hostname = output[0]
        port = output[1]
    elif len(output) == 3:  # PROTOCOL:HOSTNAME:PORT
        protocol = output[0].upper()
        hostname = output[1]
        port = output[2]
    else:
        raise BadOptionUsage(
            "output",
            "Error parsing output string.  Pass a string in the format PROTOCOL:HOSTNAME:PORT to output "
            "to the specified server endpoint, where format is either UDP, TCP or TLS_TCP.  Also accepts strings of the format HOSTNAME "
            "and HOSTNAME:PORT where port will default to 514 and protocol will default to UDP.",
        )

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
