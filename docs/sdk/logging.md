# Logging

By default, the `incydr.Client` uses the [Rich library's logging handler](https://rich.readthedocs.io/en/stable/logging.html),
sending logging to standard err, and defaults to log level `logging.WARNING`.

Basic request details are logged for every http request made at INFO level:
```python
import incydr
client = incydr.Client(log_level="INFO")
client.cases.v1.get_case(21)
```

Log custom messages in your scripts from the `client.settings.logger` object directly:
```python
client.settings.logger.warning("Logged warning message!")
```

Increase to DEBUG level for much more detailed logging of the request/response cycle:

```python
client.settings.log_level = "DEBUG"
client.cases.v1.get_case(21)
```

The output from the above code snippets would look like this:

![Rich INFO Logging](./rich_logging.svg)


### Disable logging to stderr

To disable logging to stderr, you can do any of the following:

- Set `INCYDR_LOG_STDERR=false` in your environment
- Initialize client with `log_stderr` argument set to False: `client = incydr.Client(log_stderr=False)`
- Change the setting property after instantiation: `client.settings.log_stderr = False`


### Disable Rich formatting

To disable Rich formatting in your log output, you can do any of the following:

- Set `INCYDR_USE_RICH=false` in your environment
- Initialize client with `use_rich` argument set to False: `client = incydr.Client(use_rich=False)`
- Change the setting property after instantiation: `client.settings.use_rich = False`

### Log to a file

To output logs to a file, set the `client.settings.log_file` property to any of the following:

- A string representing a valid file path
- A [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) object represting a valid file path
- A file object inheriting from [`io.IOBase`](https://docs.python.org/3/library/io.html?highlight=io#io.IOBase)
