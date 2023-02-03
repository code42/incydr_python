from io import StringIO

import pytest
from pydantic import Field
from pytest_httpserver import HTTPServer

from .conftest import TEST_HOST
from _incydr_sdk.core.models import CSVModel
from _incydr_sdk.core.models import Model
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
        == "CSV header missing column: 'required_field' required. Valid column aliases: ['required_field', 'requiredField', 'RF']"
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
    assert "value is not a valid integer" in str(err.value)
