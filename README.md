# incydr

[![PyPI - Version](https://img.shields.io/pypi/v/incydr.svg)](https://pypi.org/project/incydr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/incydr.svg)](https://pypi.org/project/incydr)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
-----

The Incydr SDK is a Python client for interacting with the [Code42 Incydr API](https://developer.code42.com/api).

It provides a thin wrapper around the [Requests](https://requests.readthedocs.io/en/latest/) HTTP library with
helper clients that model Code42 data and validate requests with the help of [Pydantic](https://pydantic-docs.helpmanual.io).

**This project is currently in BETA and subject to breaking changes prior to the 1.0 release.**

Documentation during the beta can be found at https://code42.github.io/incydr_python

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install incydr
```

# Contributing

## Install hatch

```console
pip install hatch
```

#### Run style checks

```console
hatch run style:check
```

#### Run tests with coverage

```console
hatch run test:cov
```

#### Serve docs locally

```console
hatch run docs:serve
```

## License

`incydr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

-----
## Getting Started

```python
from incydr import Client

client = Client(url="api-gateway-url.code42.com", api_client_id="key-42", api_client_secret="c42")
```
