from __future__ import annotations

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

    def json(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=True,
        skip_defaults=None,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
        encoder=None,
        models_as_dict=True,
        **dumps_kwargs,
    ):
        """
        Generate a JSON representation of the model, optionally specifying which fields to include or exclude.

        See [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeljson) for full details.
        """
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=True,
        skip_defaults=None,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
    ):
        """
        Generate a dict representation of the model, optionally specifying which fields to include or exclude.

        See [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict) for full details.
        """
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}
        extra = "allow"


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
