import logging
import re
import sys
import warnings
from io import IOBase
from pathlib import Path
from textwrap import indent
from typing import Union

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from requests_toolbelt.utils.dump import dump_response
from rich import pretty
from rich.console import Console
from rich.logging import RichHandler

from _incydr_sdk.enums import _Enum

# capture default displayhook so we can "uninstall" rich
_sys_displayhook = sys.displayhook
_incydr_console = Console(stderr=True)


_log_level_map = {"ERROR": 40, "WARNING": 30, "WARN": 30, "INFO": 20, "DEBUG": 10}


class LogLevel(_Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


_std_log_formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(levelname)s - %(message)s", datefmt="[%x %X]"
)
_rich_log_formatter = logging.Formatter(fmt="%(message)s", datefmt="[%x %X]")

_auth_header_regex = re.compile(r"Authorization: (Bearer|Basic) \S+")


class IncydrSettings(BaseSettings):
    """
    Configure settings on the `incydr.Client`.

    Usage:

        >> import incydr
        >>> client = incydr.Client(page_size = 10)

    Settings can also be loaded from shell environment variables or .env files. Just prefix a setting's attribute name
    with `INCYDR_` when configuring via enviroment vars.

    For example: To load `client.settings.api_client_secret` from the environment, set
    `INCYDR_API_CLIENT_SECRET="my_secret"`.

    The `incydr.Client` loads settings in the following priority:

    - Args passed to `Client` constructor
    - Shell environment variables
    - An .env file in the current working directory
    - An .env file in `~/.config/incydr` directory

    **Attributes**:

    * **api_client_id**: `str` The API Client Identifier for authentication. env_var=`INCYDR_API_CLIENT_ID`
    * **api_client_secret**: `str` The API Client Secret for authentication. env_var=`INCYDR_API_CLIENT_SECRET`
    * **url**: `str` The URL of your Code42 API gateway instance. env_var=`INCYDR_URL`
    * **page_size**: `int` The default page size for all paginated requests. Defaults to 100. env_var=`INCYDR_PAGE_SIZE`
    * **max_response_history**: `int` The maximum number of responses the `incydr.Client.response_history` list will
        store. Defaults to 5. env_var=`INCYDR_MAX_RESPONSE_HISTORY`
    * **log_stderr**: `bool` Enables logging to stderr. Defaults to True. env_var=`INCYDR_LOG_STDERR`
    * **log_file**: `str` The file path or file-like object to write log output to. Defaults to None. env_var=`INCYDR_LOG_FILE`
    * **log_level**: `int` The level for logging messages. Defaults to `logging.WARNING`. env_var=`INCYDR_LOG_LEVEL`
    * **logger**: `logging.Logger` The logger used for client logging. Cannot be defined via environment variable. Can
        be replaced with a custom `logging.Logger`. If a custom `Logger` is supplied, the other log settings will have
        no effect and must be configured manually on the custom logger.
    * **user_agent_prefix**: `str` Prefixes all `User-Agent` headers with the supplied string.
    * **use_rich**: `bool` Enables [rich](https://rich.readthedocs.io/en/stable/introduction.html) support in logging
        and the Python repl. Defaults to True. env_var=`INCYDR_USE_RICH`
    """

    api_client_id: str
    api_client_secret: SecretStr
    url: str
    page_size: int = Field(default=100)
    max_response_history: int = Field(default=5)
    use_rich: bool = Field(default=True)
    log_stderr: bool = Field(default=True)
    log_file: Union[str, Path, IOBase] = Field(default=None)
    log_level: Union[int, str] = Field(default=logging.WARNING, validate_default=True)
    logger: logging.Logger = Field(default=None)
    user_agent_prefix: Union[str] = Field(default="")

    model_config = SettingsConfigDict(
        env_prefix="incydr_",
        extra="ignore",
        env_file=str(Path.home() / ".config" / "incydr" / ".env"),
        validate_assignment=True,
        custom_logger=False,
        validate_by_name=True,
        validate_by_alias=True,
    )

    def __init__(self, **kwargs):
        # clear any keys from kwargs that are passed as None, which forces lookup of values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # if .env file in CWD, use it instead of ~/.config/incydr/.env
        if Path(".env").exists():
            kwargs["_env_file"] = ".env"
        super().__init__(**kwargs)

    @field_validator("log_level", mode="before")
    def _validate_log_level(cls, value, **kwargs):  # noqa
        try:
            return int(value)
        except ValueError:
            value = value.upper()
            LogLevel(value)
            return _log_level_map[value]

    @field_validator("log_file", mode="plain")
    @classmethod
    def _validate_log_file(cls, value, **kwargs):  # noqa
        if isinstance(value, (str, Path)):
            p = Path(value)
            # existing file OK
            if p.exists() and p.is_file():
                value = str(p.absolute())
            # new file in existing dir OK
            elif not p.exists() and p.parent.is_dir():
                value = str(p.absolute())
            else:
                raise ValueError(f"{value} is not a valid file path for logging.")
        return value

    @field_validator("use_rich", mode="before")
    @classmethod
    def _validate_use_rich(cls, value, **kwargs):  # noqa
        if value:
            pretty.install()
        else:
            sys.displayhook = _sys_displayhook
        return value

    @field_validator("logger", mode="before")
    @classmethod
    def _validate_logger(cls, value, **kwargs):  # noqa
        if value is None:
            logger = logging.getLogger("incydr")
            # flag the logger we create with a custom attribute so we can detect user-provided loggers later
            logger._incydr = True
            return logger
        if isinstance(value, logging.Logger):
            return value
        else:
            raise ValueError(f"{value} is not a `logging.Logger`.")

    @model_validator(mode="after")
    @classmethod
    def _configure_logging(cls, values):  # noqa
        values_dict = values.dict()
        use_rich = values_dict["use_rich"]
        log_file = values_dict["log_file"]
        log_stderr = values_dict["log_stderr"]
        log_level = values_dict["log_level"]
        logger = values_dict["logger"]

        if not hasattr(logger, "_incydr"):
            warnings.warn(
                "A custom logger has been set, all other log-related settings on the `incydr.Client` are ignored for custom loggers.",
                stacklevel=2,
            )
            return values

        logger.handlers.clear()

        if log_stderr and use_rich:
            rich_handler = RichHandler(console=_incydr_console, rich_tracebacks=True)
            rich_handler.setFormatter(_rich_log_formatter)
            logger.addHandler(rich_handler)

        elif log_stderr and not use_rich:
            std_handler = logging.StreamHandler()
            std_handler.setFormatter(_std_log_formatter)
            logger.addHandler(std_handler)

        if log_file and use_rich:
            if isinstance(log_file, str):
                log_file = open(log_file, "a", encoding="utf-8")
            console = Console(file=log_file, no_color=True, width=200)
            rich_file_handler = RichHandler(console=console, rich_tracebacks=True)
            rich_file_handler.setFormatter(_rich_log_formatter)
            logger.addHandler(rich_file_handler)

        elif log_file and not use_rich:
            if isinstance(log_file, str):
                std_file_handler = logging.FileHandler(
                    filename=log_file, encoding="utf-8"
                )
            else:
                std_file_handler = logging.StreamHandler(stream=log_file)
            std_file_handler.setFormatter(_std_log_formatter)
            logger.addHandler(std_file_handler)

        logger.setLevel(log_level)
        cls.logger = logger
        return values

    def _log_response_info(self, response):
        self.logger.info(
            f"{response.request.method} {response.request.url} status_code={response.status_code}"
        )

    def _log_response_debug(self, response):
        try:
            dumped = dump_response(
                response, request_prefix=b"", response_prefix=b""
            ).decode("utf-8")
            dumped = re.sub(
                _auth_header_regex,
                "Authorization: <token_redacted>",
                dumped,
            )
            if not self.use_rich:
                dumped = indent(dumped, prefix="\t")
            self.logger.debug(dumped)
        except Exception as err:
            if isinstance(response.content, bytes):
                self.logger.debug("Unable to log binary response data.")
                self.logger.debug(response)
            else:
                self.logger.debug(f"Error dumping request/response info: {err}")
                self.logger.debug(response)

    def _log_error(self, err, invocation_str=None):
        message = str(err) if err else None
        if invocation_str:
            message = f"Exception occurred from input: '{invocation_str}'.\n" + message
        if message:
            self.logger.error(message)

    def _log_verbose_error(self, invocation_str=None, http_request=None):
        """For logging traces, invocation strs, and request parameters during exceptions to the
        error log file."""
        prefix = (
            "Exception occurred."
            if not invocation_str
            else f"Exception occurred from input: '{invocation_str}'."
        )
        self.logger.exception(f"{prefix}. See error below.")
        if http_request:
            self._log_error(f"Request parameters: {http_request.body}")
