from typing import Optional

import requests
from pydantic import SecretStr
from requests import Session
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

from _incydr_sdk.core.models import AuthResponse
from _incydr_sdk.core.models import RefreshTokenAuthResponse


class APIClientAuth(AuthBase):
    def __init__(
        self, session: Session, api_client_id: str, api_client_secret: SecretStr
    ):
        self.session = session
        self.api_client_id = api_client_id
        self.api_client_secret = api_client_secret
        self.token_response: Optional[AuthResponse] = None

    def refresh(self):
        auth = HTTPBasicAuth(
            username=self.api_client_id,
            password=self.api_client_secret.get_secret_value(),
        )
        r = self.session.post("/v1/oauth", auth=auth)
        r.raise_for_status()
        self.token_response = AuthResponse.parse_response(r)

    def __call__(self, request):
        if self.token_response is None or self.token_response.expired:
            self.refresh()
        token = self.token_response.access_token.get_secret_value()
        request.headers["Authorization"] = f"Bearer {token}"
        return request


class RefreshTokenAuth(AuthBase):
    def __init__(self, session: Session, refresh_url: str, refresh_token: str):
        self.session = session
        self.refresh_url = refresh_url
        self.refresh_token = SecretStr(refresh_token)
        self.token_response: Optional[RefreshTokenAuthResponse] = None

    def refresh(self):
        auth_body = {"refreshToken": self.refresh_token.get_secret_value()}
        r = requests.post(self.refresh_url, json=auth_body)
        r.raise_for_status()
        self.token_response = RefreshTokenAuthResponse.parse_response(r)
        self.refresh_token = self.token_response.refreshToken.tokenValue

    def __call__(self, request):
        if self.token_response is None or self.token_response.accessToken.expired:
            self.refresh()
        token = self.token_response.accessToken.tokenValue.get_secret_value()
        request.headers["Authorization"] = f"Bearer {token}"
        return request
