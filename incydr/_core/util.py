import re
from enum import Enum

from requests import Response


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


def get_filename_from_content_disposition(response: Response, fallback=None) -> str:
    if "content-disposition" in response.headers:
        match = re.search("filename=(.*)", response.headers["content-disposition"])
        if match:
            return match.group(1)
    return fallback
