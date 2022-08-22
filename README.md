# incydr

[![PyPI - Version](https://img.shields.io/pypi/v/incydr.svg)](https://pypi.org/project/incydr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/incydr.svg)](https://pypi.org/project/incydr)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install incydr
```

## Hatch

```console
pip install hatch
```

#### Style check

```console
hatch run style:check
```

#### Run tests with coverage

```console
hatch run test:cov
```

## License

`incydr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


-----
## Getting Started

```python
from incydr import Client
client = Client(url="api-gateway-url.code42.com", api_client_id="key-42", api_client_secret="c42")
```
