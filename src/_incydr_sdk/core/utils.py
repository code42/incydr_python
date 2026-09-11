import logging
import re
from typing import Optional

from requests import Response
from urllib3 import Retry


def get_filename_from_content_disposition(response: Response, fallback=None) -> str:
    if "content-disposition" in response.headers:
        match = re.search("filename=(.*)", response.headers["content-disposition"])
        if match:
            return match.group(1)
    return fallback


class IncydrRequestRetryStrategy(Retry):
    """We subclass :class:`urllib3.Retry` just to add a bit of logging so the user can tell why the
    request might look like it's hanging when we are retrying due to 429.
    """

    _logger: Optional[logging.Logger] = None

    def __init__(self, *args, logger: logging.Logger = None, **kwargs):
        self._logger = logger
        super().__init__(*args, **kwargs)

    def new(self, **kw):
        return super().new(logger=self._logger, **kw)

    def get_retry_after(self, response):
        retry_after = super().get_retry_after(response)
        if retry_after is not None and self._logger is not None:
            self._logger.warning(
                f"Rate limit hit, retrying after: {int(retry_after)} seconds."
            )
        return retry_after

    def get_backoff_time(self):
        backoff_time = super().get_backoff_time()
        if self._logger is not None and backoff_time > 0:
            self._logger.warning(
                f"Rate limit hit, retrying after: {backoff_time} seconds."
            )
        return backoff_time
