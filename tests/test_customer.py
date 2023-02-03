import json

from pytest_httpserver import HTTPServer

from _incydr_sdk.customer.models import Customer
from incydr import Client

TEST_CUSTOMER = {
    "name": "test-customer",
    "registrationKey": "key-42",
    "tenantId": "424242",
}


def test_get_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request("/v1/customer").respond_with_json(TEST_CUSTOMER)
    client = Client()
    customer = client.customer.v1.get()
    assert isinstance(customer, Customer)
    assert customer.json() == json.dumps(TEST_CUSTOMER)
