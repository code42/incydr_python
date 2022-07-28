from pytest_httpserver import HTTPServer

from .conftest import TEST_HOST
from incydr import Client


def test_client_init_reads_environment_vars_when_no_arguments_passed(
    httpserver_auth: HTTPServer,
):
    c = Client()
    assert c.settings.url == TEST_HOST
    assert c.settings.api_client_id == "env_id"
    assert c.settings.api_client_secret.get_secret_value() == "env_secret"


def test_client_init_prefers_passed_arg_when_environment_vars_set(
    httpserver_auth: HTTPServer,
):
    c = Client(api_client_id="key-456")
    assert c.settings.api_client_id != "env_id"
    assert c.settings.url == TEST_HOST
    assert c.settings.api_client_secret.get_secret_value() == "env_secret"
