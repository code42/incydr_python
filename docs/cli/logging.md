# Logging

By default, the `incydr.Client` uses the [Rich library's logging handler](https://rich.readthedocs.io/en/stable/logging.html) and defaults to log level `warning`.

Incydr CLI logging options can be provided at any level of a command.  Any options provided will override the corresponding environment variable settings.

For example, the following command will output debug logging to stderr:

```bash
    incydr users list --log-stderr --log-level debug
```

Environment variables can be set and are loaded in the following priority:

* Shell environment variables
* An .env file in the current working directory
* An .env file in `~/.config/incydr` directory

See [Incydr SDK Settings](../sdk/settings.md) for more details on available settings.

### Log Level

The level for logging messages, defaults to `warning`.

Use the `--log-level` option at any level of a command to change the logging level.
Corresponds with the `INCYDR_LOG_LEVEL` environment variable.

See [Log Levels](https://docs.python.org/3/library/logging.html#logging-levels) for valid Python logging levels.

### Log File

The file path or file-like object to write log output to, defaults to `~/.incydr/log/incydr_cli.log`

Use the `--log-file` option at any level of a command to change the log file.
Corresponds with the `INCYDR_LOG_FILE` environment variable.

### Log StdErr

Use the `--log-stderr` flag to log full errors to `stderr` output, in addition to the log file.
Corresponds with the `INCYDR_LOG_STDERR` environment variable.
