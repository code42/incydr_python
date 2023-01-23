# Contributing

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
