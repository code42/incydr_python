# Introduction

The Incydr SDK is a Python client for interacting with the [Code42 Incydr API](https://developer.code42.com/api).

It provides a thin wrapper around the [Requests](https://requests.readthedocs.io/en/latest/) HTTP library with
helper clients that model Code42 data and validate requests with the help of [Pydantic](https://pydantic-docs.helpmanual.io).

## Installation

---

Install using pip:

```bash
$ pip install incydr
```

Import the `incydr.Client` initialize with your Incydr API Client:

```python
import incydr

client = incydr.Client(
    url="https://api.us.code42.com",
    api_client_id="my_id",
    api_client_secret="my_secret" # (1)
)
```

Any arguments that are not provided to the `incydr.Client` will attempt to be loaded from environment variables or
   .env files. See [Settings](/sdk/settings) for more details


The [`incydr.Client`](client.md) provides helper methods that map to each API action described in the
[Code42 API Reference](https://developer.code42.com/api). It offers a sub-client for each endpoint namespace and API
version. For example, to interact with `/v1/cases` endpoints:

```pycon
>>> import incydr
>>> client = incydr.Client()
>>> client.cases.v1.create(name="Test", description="Created with Incydr SDK")
Case(
    number=28,
    name='Test',
    created_at=datetime.datetime(2022, 8, 2, 13, 11, 7, 803762, tzinfo=datetime.timezone.utc),
    updated_at=datetime.datetime(2022, 8, 2, 13, 11, 7, 803762, tzinfo=datetime.timezone.utc),
    description='Created with Incydr SDK',
    findings=None,
    subject=None,
    subject_username=None,
    status='OPEN',
    assignee=None,
    assignee_username=None,
    created_by_user_id=None,
    created_by_username=None,
    last_modified_by_user_id=None,
    last_modified_by_username=None
)
```

Methods return data wrapped in [Pydantic](https://pydantic-docs.helpmanual.io) model classes, providing great editor
support like autocomplete and type hinting.
