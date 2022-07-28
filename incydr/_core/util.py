import re

from requests import Response


def get_filename_from_content_disposition(response: Response, fallback=None) -> str:
    if "content-disposition" in response.headers:
        match = re.search("filename=(.*)", response.headers["content-disposition"])
        if match:
            return match.group(1)
    return fallback
