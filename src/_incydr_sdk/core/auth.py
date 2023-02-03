from typing import Optional

from pydantic import SecretStr
from requests import Session
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

from _incydr_sdk.core.models import AuthResponse


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
