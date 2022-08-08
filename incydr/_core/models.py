from datetime import datetime
from datetime import timedelta

import requests
from pydantic import BaseModel
from pydantic import PrivateAttr
from pydantic import SecretStr
from pydantic import ValidationError


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

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}
        extra = "allow"

    def __rich_repr__(self):
        """Get fields for Rich library"""
        for name, field_repr in self.__repr_args__():
            if name is None:
                yield field_repr
            else:
                yield name, field_repr


class AuthResponse(ResponseModel):
    token_type: str
    expires_in: int
    access_token: SecretStr
    _init_time: datetime = PrivateAttr(default_factory=datetime.utcnow)

    @property
    def expired(self):
        return (datetime.utcnow() - self._init_time) > timedelta(
            seconds=self.expires_in
        )
