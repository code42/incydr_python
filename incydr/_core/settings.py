import logging
from pathlib import Path

from pydantic import BaseSettings
from pydantic import Field
from pydantic import SecretStr
from pydantic import validator


def default_logger(filename=None):
    logger = logging.getLogger("incydr")
    if filename is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(filename=filename, encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s:%(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    return logger


class IncydrSettings(BaseSettings):
    """
    Configure settings on the `incydr.Client`.

    Usage:

        >> import incydr
        >>> client = incydr.Client()
        >>> client.settings.page_size = 10

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
    * **logger**: `logging.Logger` The logger used for client logging. Can be replaced with a custom `logging.Logger` or
        a `str` indicating the file to write log output to. Default logging goes to `sys.stderr`.
        env_var=`INCYDR_LOGGER`
    * **log_level**: `int` The level for logging messages. Defaults to `logging.WARNING`. env_var=`INCYDR_LOG_LEVEL`
    * **user_agent_prefix**: `str` Prefixes all `User-Agent` headers with the supplied string.
    * **use_rich**: `bool` Enables [rich](https://rich.readthedocs.io/en/stable/introduction.html) support in logging
        and the Python repl. Defaults to True. env_var=`INCYDR_USE_RICH`
    """

    api_client_id: str = Field(env="incydr_api_client_id")
    api_client_secret: SecretStr = Field(env="incydr_api_client_secret")
    url: str = Field(env="incydr_url")
    page_size: int = Field(env="incydr_page_size", default=100)
    max_response_history: int = Field(env="incydr_max_response_history", default=5)
    logger: logging.Logger = Field(default=None, env="incydr_logger")
    log_level: int = Field(
        default=logging.WARNING,
        env="incydr_log_level",
    )
    user_agent_prefix: str = Field(default=None, env="incydr_user_agent_prefix")
    use_rich: bool = Field(env="incydr_use_rich", default=True)

    def __init__(self, **kwargs):
        # clear any keys from kwargs that are passed as None, which forces lookup of values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # if .env file in CWD, use it instead of ~/.config/incydr/.env
        if Path(".env").exists():
            kwargs["_env_file"] = ".env"
        super().__init__(**kwargs)

    class Config:
        env_file = str(Path.home() / ".config" / "incydr" / ".env")
        validate_assignment = True

    @validator("logger", pre=True, always=True)
    def validate_logger(cls, value, values, **kwargs):
        if isinstance(value, str) or value is None:
            return default_logger(filename=value)
        assert isinstance(value, logging.Logger), f"{value} is not a logging.Logger"
        return value

    @validator("log_level", always=True)
    def validate_log_level(cls, value, values, **kwargs):
        logger = values.get("logger")
        assert isinstance(
            logger, logging.Logger
        ), f"settings.logger is not a logging.Logger"
        logger.setLevel(value)
        return logger.getEffectiveLevel()
