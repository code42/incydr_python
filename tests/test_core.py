from io import StringIO
from unittest.mock import MagicMock

import pytest
from pydantic import Field
from pytest_httpserver import HTTPServer
from requests.exceptions import HTTPError

from .conftest import TEST_HOST
from .conftest import TEST_TOKEN
from _incydr_sdk.core.auth import RefreshTokenAuth
from _incydr_sdk.core.models import CSVModel
from _incydr_sdk.core.models import Model
from _incydr_sdk.core.settings import IncydrSettings
from _incydr_sdk.core.utils import IncydrRequestRetryStrategy
from _incydr_sdk.exceptions import AuthMissingError
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


def test_csv_model_parsing():
    class Test(CSVModel):
        required_field: str = Field(
            csv_aliases=["required_field", "requiredField", "RF"]
        )

    csv_with_all_aliases = StringIO(
        """required_field,RF,requiredField,extra\n1,2,3,4\na,b,c,d\n"""
    )
    row_1, row_2 = tuple(Test.parse_csv(csv_with_all_aliases))

    assert row_1.required_field == "1"
    assert row_1.RF == "2"
    assert row_1.requiredField == "3"
    assert row_1.extra == "4"

    assert row_2.required_field == "a"
    assert row_2.RF == "b"
    assert row_2.requiredField == "c"
    assert row_2.extra == "d"

    csv_with_two_aliases = StringIO("""RF,requiredField,extra\n2,3,4\nb,c,d\n""")
    row_1, row_2 = tuple(Test.parse_csv(csv_with_two_aliases))

    assert row_1.required_field == "3"
    assert row_1.RF == "2"
    assert row_1.requiredField == "3"
    assert row_1.extra == "4"

    assert row_2.required_field == "c"
    assert row_2.RF == "b"
    assert row_2.requiredField == "c"
    assert row_2.extra == "d"

    csv_with_one_alias = StringIO("""RF,extra\n2,4\nb,d\n""")
    row_1, row_2 = tuple(Test.parse_csv(csv_with_one_alias))

    assert row_1.required_field == "2"
    assert row_1.RF == "2"
    assert row_1.extra == "4"

    assert row_2.required_field == "b"
    assert row_2.RF == "b"
    assert row_2.extra == "d"

    csv_with_no_required_aliases = StringIO("""data,extra\n1,2\na,b\n""")
    with pytest.raises(ValueError) as err:
        list(Test.parse_csv(csv_with_no_required_aliases))
    assert (
        str(err.value)
        == "CSV header missing column: Value error, 'required_field' required. Valid column aliases: ['required_field', 'requiredField', 'RF']"
    )


def test_json_lines_model_parsing():
    class Test(Model):
        field_1: str
        field_2: int

    json_lines = StringIO(
        """{ "field_1": "value1", "field_2": 10 }\n{ "field_1": "value2", "field_2": 20 }"""
    )

    line_1, line_2 = list(Test.parse_json_lines(json_lines))
    assert line_1.field_1 == "value1"
    assert line_1.field_2 == 10

    assert line_2.field_1 == "value2"
    assert line_2.field_2 == 20

    not_json_lines = StringIO(
        """{"field_1": "value1","field_2": 10}\n{\n\t"field_1": "value1",\n\t"field_2": 10\n},\n{\n\t"field_1": "value_2",\n\t"field_2": 20\n }"""
    )
    with pytest.raises(ValueError) as err:
        list(Test.parse_json_lines(not_json_lines))
    assert (
        str(err.value)
        == "Unable to parse line 2. Expecting JSONLines format: https://jsonlines.org"
    )

    invalid_model_data = StringIO(
        """{ "field_1": "value1", "field_2": 10 }\n{ "field_1": "value2", "field_2": "not_int" }"""
    )
    with pytest.raises(ValueError) as err:
        list(Test.parse_json_lines(invalid_model_data))
    assert "Error parsing object on line 2: 1 validation error for Test" in str(
        err.value
    )
    assert "Input should be a valid integer" in str(err.value)


def test_user_agent(httpserver_auth: HTTPServer):
    c = Client()
    assert c._session.headers["User-Agent"].startswith("incydrSDK")


@pytest.fixture
def httpserver_refresh_token_auth(httpserver: HTTPServer, monkeypatch):
    monkeypatch.setenv("incydr_url", TEST_HOST)
    monkeypatch.setenv("incydr_refresh_token", "test_refresh_token")
    monkeypatch.setenv("incydr_refresh_url", f"{TEST_HOST}/v1/refresh")

    refresh_response = {
        "accessToken": {
            "tokenValue": TEST_TOKEN,
            "expiresAt": "2099-01-01T00:00:00Z",
        },
        "refreshToken": {
            "tokenValue": "new_refresh_token",
            "expiresAt": "2099-01-01T00:00:00Z",
        },
    }
    httpserver.expect_request("/v1/refresh", method="POST").respond_with_json(
        refresh_response
    )
    return httpserver


def test_client_init_with_refresh_token_and_refresh_url_uses_refresh_token_auth(
    httpserver_refresh_token_auth: HTTPServer,
):
    c = Client()
    assert isinstance(c._session.auth, RefreshTokenAuth)
    assert c.settings.refresh_token.get_secret_value() == "test_refresh_token"
    assert c.settings.refresh_url == f"{TEST_HOST}/v1/refresh"


def test_client_init_with_refresh_token_does_not_require_api_client_credentials(
    httpserver_refresh_token_auth: HTTPServer,
):
    c = Client()
    assert c.settings.api_client_id is None
    assert c.settings.api_client_secret is None


def test_client_init_with_refresh_token_passed_as_args(
    httpserver: HTTPServer, monkeypatch
):
    monkeypatch.setenv("incydr_url", TEST_HOST)

    refresh_response = {
        "accessToken": {
            "tokenValue": TEST_TOKEN,
            "expiresAt": "2099-01-01T00:00:00Z",
        },
        "refreshToken": {
            "tokenValue": "new_refresh_token",
            "expiresAt": "2099-01-01T00:00:00Z",
        },
    }
    httpserver.expect_request("/v1/refresh", method="POST").respond_with_json(
        refresh_response
    )

    c = Client(
        refresh_token="arg_refresh_token",
        refresh_url=f"{TEST_HOST}/v1/refresh",
    )
    assert isinstance(c._session.auth, RefreshTokenAuth)
    assert c.settings.refresh_token.get_secret_value() == "arg_refresh_token"


def test_settings_with_only_refresh_token_raises_auth_missing_error(monkeypatch):
    with pytest.raises(AuthMissingError) as exc_info:
        IncydrSettings(
            url=TEST_HOST,
            refresh_token="test_refresh_token",
            _env_file="",
        )

    assert "api_client_id" in exc_info.value.error_keys
    assert "api_client_secret" in exc_info.value.error_keys


def test_settings_with_only_refresh_url_raises_auth_missing_error(monkeypatch):
    with pytest.raises(AuthMissingError) as exc_info:
        IncydrSettings(
            url=TEST_HOST,
            refresh_url=f"{TEST_HOST}/v1/refresh",
            _env_file="",
        )

    assert "api_client_id" in exc_info.value.error_keys
    assert "api_client_secret" in exc_info.value.error_keys


def test_client_prefers_refresh_token_auth_when_both_auth_methods_provided(
    httpserver: HTTPServer, monkeypatch
):
    monkeypatch.setenv("incydr_url", TEST_HOST)
    monkeypatch.setenv("incydr_api_client_id", "env_id")
    monkeypatch.setenv("incydr_api_client_secret", "env_secret")
    monkeypatch.setenv("incydr_refresh_token", "test_refresh_token")
    monkeypatch.setenv("incydr_refresh_url", f"{TEST_HOST}/v1/refresh")

    refresh_response = {
        "accessToken": {
            "tokenValue": TEST_TOKEN,
            "expiresAt": "2099-01-01T00:00:00Z",
        },
        "refreshToken": {
            "tokenValue": "new_refresh_token",
            "expiresAt": "2099-01-01T00:00:00Z",
        },
    }
    httpserver.expect_request("/v1/refresh", method="POST").respond_with_json(
        refresh_response
    )

    c = Client()
    assert isinstance(c._session.auth, RefreshTokenAuth)


def test_settings_retry_on_rate_limit_defaults_to_true(monkeypatch):
    monkeypatch.setenv("incydr_url", TEST_HOST)
    monkeypatch.setenv("incydr_api_client_id", "env_id")
    monkeypatch.setenv("incydr_api_client_secret", "env_secret")

    settings = IncydrSettings()
    assert settings.retry_on_rate_limit is True


def test_client_mounts_rate_limit_retry_adapter_by_default(
    httpserver_auth: HTTPServer,
):
    client = Client()
    adapter = client.session.get_adapter(TEST_HOST)

    assert isinstance(adapter.max_retries, IncydrRequestRetryStrategy)
    assert adapter.max_retries.status == 3
    assert adapter.max_retries.total is None
    assert adapter.max_retries.connect is False
    assert adapter.max_retries.read is False
    assert not adapter.max_retries.redirect
    assert not adapter.max_retries.other
    assert 429 in adapter.max_retries.status_forcelist
    assert adapter.max_retries._logger is client.settings.logger


def test_client_does_not_mount_rate_limit_retry_adapter_when_disabled(
    httpserver_auth: HTTPServer,
):
    client = Client(retry_on_rate_limit=False)
    adapter = client.session.get_adapter(TEST_HOST)

    assert not isinstance(adapter.max_retries, IncydrRequestRetryStrategy)
    assert adapter.max_retries.total == 0


def test_client_retries_get_request_on_429(httpserver_auth: HTTPServer):
    httpserver_auth.expect_ordered_request(
        "/v1/users/user-1", method="GET"
    ).respond_with_data("", status=429, headers={"Retry-After": "0"})
    httpserver_auth.expect_ordered_request(
        "/v1/users/user-1", method="GET"
    ).respond_with_json({"userId": "user-1"})

    client = Client()
    response = client.session.get("/v1/users/user-1")

    assert response.status_code == 200
    assert response.json() == {"userId": "user-1"}
    httpserver_auth.check()


def test_client_does_not_retry_post_request_on_429(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/cases", method="POST").respond_with_data(
        "", status=429, headers={"Retry-After": "0"}
    )

    client = Client()
    with pytest.raises(HTTPError) as err:
        client.session.post("/v1/cases", json={"name": "test"})

    assert err.value.response.status_code == 429
    httpserver_auth.check()


def test_client_logs_when_retrying_on_429(httpserver_auth: HTTPServer, mocker):
    httpserver_auth.expect_ordered_request(
        "/v1/users/user-1", method="GET"
    ).respond_with_data("", status=429, headers={"Retry-After": "0"})
    httpserver_auth.expect_ordered_request(
        "/v1/users/user-1", method="GET"
    ).respond_with_json({"userId": "user-1"})

    client = Client()
    mock_warning = mocker.patch.object(client.settings.logger, "warning")
    client.session.get("/v1/users/user-1")

    mock_warning.assert_called_with("Rate limit hit, retrying after: 0 seconds.")


def test_incydr_request_retry_strategy_new_preserves_logger():
    mock_logger = MagicMock()
    retry = IncydrRequestRetryStrategy(
        logger=mock_logger, status=3, status_forcelist=[429]
    )

    cloned = retry.new()

    assert isinstance(cloned, IncydrRequestRetryStrategy)
    assert cloned._logger is mock_logger
    assert cloned.status == 3
    assert 429 in cloned.status_forcelist
