from typing import Optional, Union
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from incydr.core.auth import APIClientAuth
from incydr.core.models import ResponseModel
from incydr.core.settings import IncydrSettings


def always_raise_for_status(response, *args, **kwargs):
    response.raise_for_status()


class IncydrSession(requests.Session):
    base_url = None

    def __init__(self, client):
        self.settings = settings
        self.base_url = settings.url
        super().__init__()

        self.hooks["response"] = [always_raise_for_status]
        self.auth = APIClientAuth(
            session=self,
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
        )

    def request(self, method, url, *args, **kwargs):
        """Send the request after generating the complete URL."""
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)

    def get(self, url: str, model: Optional[ResponseModel] = None, **kwargs):
        response = super().get(url=url, **kwargs)
        if model:
            return model.parse_response(response)
        else:
            return response

    def put(
        self, url: str, data: Union[BaseModel, str] = None, **kwargs
    ) -> requests.Response:
        if isinstance(data, BaseModel):
            data = data.json(by_alias=True)
        _kwargs = {
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "data": data,
            **kwargs,
        }
        return super().put(**_kwargs)

    def post(
        self, url: str, data: Union[BaseModel, str] = None, **kwargs
    ) -> requests.Response:
        if isinstance(data, BaseModel):
            data = data.json(by_alias=True)
        _kwargs = {
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "data": data,
            **kwargs,
        }
        return super().post(**_kwargs)
