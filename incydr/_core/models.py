from datetime import datetime, timedelta

import requests
from pydantic import BaseModel, ValidationError, SecretStr, PrivateAttr


class ResponseModel(BaseModel):
    @classmethod
    def parse_response(cls, response: requests.Response):
        try:
            return cls.parse_raw(response.text)
        except ValidationError as err:
            err.response = response
            raise

    def json(self, **kwargs):
        if "by_alias" not in kwargs:
            kwargs["by_alias"] = True
        return super().json(**kwargs)


class AuthResponse(BaseModel):
    token_type: str
    expires_in: int
    access_token: SecretStr
    _init_time: datetime = PrivateAttr(default_factory=datetime.utcnow)

    @property
    def expired(self):
        return (datetime.utcnow() - self._init_time) > timedelta(
            seconds=self.expires_in
        )
