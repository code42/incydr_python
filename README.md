# Incydr

[![PyPI - Version](https://img.shields.io/pypi/v/incydr.svg)](https://pypi.org/project/incydr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/incydr.svg)](https://pypi.org/project/incydr)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
-----

The Incydr SDK is a Python client for interacting with the [Code42 Incydr API](https://developer.code42.com/api).

It provides a thin wrapper around the [Requests](https://requests.readthedocs.io/en/latest/) HTTP library with
helper clients that model Code42 data and validate requests with the help of [Pydantic](https://pydantic-docs.helpmanual.io).

Documentation can be found at https://developer.code42.com.

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

Install the Incydr SDK with the following command:

```console
pip install incydr
```

Use either of the following to install Incydr CLI extension alongside the SDK:

```bash
$ pip install 'incydr[cli]'
```

```bash
$ pip install 'incydr[all]'.
```

For more details see the [SDK Documentation](https://developer.code42.com/sdk/) and the [CLI Documentation](https://developer.code42.com/cli/).

## License

`incydr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
