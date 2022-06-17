from requests import Session
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel, PrivateAttr, SecretStr
from typing import Optional
from datetime import datetime, timedelta


class APIClientAuth(AuthBase):
    def __init__(self, session: Session, api_client_id: str, api_client_secret: SecretStr):
        self.session = session
        self.api_client_id = api_client_id
        self.api_client_secret = api_client_secret
        self.token_response: Optional[AuthResponse] = None

    def refresh(self):
        auth = HTTPBasicAuth(username=self.api_client_id, password=self.api_client_secret.get_secret_value())
        r = self.session.post("/v1/oauth", auth=auth)
        self.token_response = AuthResponse(**r.json())

    def __call__(self, request):
        if self.token_response is None or self.token_response.expired:
            self.refresh()
        token = self.token_response.access_token.get_secret_value()
        request.headers["Authorization"] = f"Bearer {token}"
        return request


class AuthResponse(BaseModel):
    token_type: str
    expires_in: int
    access_token: SecretStr
    _init_time: datetime = PrivateAttr(default_factory=datetime.utcnow)

    @property
    def expired(self):
        return (datetime.utcnow() - self._init_time) > timedelta(seconds=self.expires_in)
