from typing import Optional

from pydantic import Field
from pydantic import root_validator

from incydr._core.models import CSVModel
from incydr._core.models import Model


class UserCSV(CSVModel):
    user: str = Field(csv_aliases=["user", "user_id", "username", "id", "userId"])


class UserJSON(Model):
    username: Optional[str]
    userId: Optional[str]

    @root_validator(pre=True)
    def _validate(cls, values):
        if "username" not in values and "userId" not in values:
            raise ValueError("A json key of 'username' or 'userId' is required")
        return values

    @property
    def user(self):
        return self.userId or self.username
