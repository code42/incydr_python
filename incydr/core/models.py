from collections.abc import Mapping

import requests
from pydantic import BaseModel, ValidationError


class ResponseModel(BaseModel, Mapping):
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

    def __getitem__(self, item):
        return self.dict().__getitem__(item)

    def __len__(self):
        return len(self.dict())

    def __iter__(self):
        yield from self.dict()
