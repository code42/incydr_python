# Contributing

To test changes on a branch that haven't been released yet, you'll have to pull down the branch and
install the SDK/CLI in `editable` mode using `pip intall -e`. Navigate to the `incydr_python` directory and to install from your local path
(rather than from a released version on PyPI) use:

```bash
pip install -e .
```

To install the CLI extension in a similar manner:

 ```bash
 pip install -e .'[cli]'
 ```

## Install hatch

The Incydr SDK uses [Hatch](https://hatch.pypa.io/latest/) as its Python project manager.

```bash
pip install hatch
```

#### Run style checks

```bash
hatch run style:check
```

Run the style check action without printing the diff.

```bash
hatch run style:check-no-diff
```

#### Run tests

Run tests with a coverage report:

```bash
hatch run test:cov
```

Run tests without a coverage report:


```bash
hatch run test:no-cov
```

#### Serve docs locally

```bash
hatch run docs:serve
```

To just build the docs:

```bash
hatch run docs:build
```
