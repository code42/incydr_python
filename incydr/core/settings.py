from pydantic import BaseSettings
from pydantic import Field
from pydantic import SecretStr
from pydantic import validator
import logging


def default_logger():
    return logging.getLogger("incydr")


class IncydrSettings(BaseSettings):
    api_client_id: str = Field(env='incydr_api_client_id')
    api_client_secret: SecretStr = Field(env='incydr_api_client_secret')
    url: str = Field(env='incydr_url')
    page_size: int = 100
    max_response_history: int = 5
    logger: logging.Logger = Field(default_factory=default_logger)
    log_level: int = Field(default=logging.WARNING, env="incydr_log_level", )

    def __init__(self, **kwargs):
        """Overload init so we can clear any keys from kwargs that are passed as None, which forces lookup of values
        from env.
        """
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    class Config:
        env_file = '.env'
        validate_assignment = True

    @validator("log_level", pre=True, always=True)
    def validate_log_level(cls, v, values, **kwargs):
        logger = values["logger"]
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger("dummy")
        logger.setLevel(v)
        return logger.getEffectiveLevel()

