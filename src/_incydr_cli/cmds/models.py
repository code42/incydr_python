from typing import Optional

from pydantic import Field
from pydantic import root_validator

from _incydr_sdk.core.models import CSVModel
from _incydr_sdk.core.models import Model


class UserCSV(CSVModel):
    user: str = Field(csv_aliases=["user", "user_id", "username", "id", "userId"])


class UserJSON(Model):
    username: Optional[str]
    userId: Optional[str]

    @root_validator(pre=True)
    def _validate(cls, values):  # noqa
        if "username" not in values and "userId" not in values:
            raise ValueError("A json key of 'username' or 'userId' is required")
        return values

    @property
    def user(self):
        return self.userId or self.username


class AgentCSV(CSVModel):
    agent_id: str = Field(csv_aliases=["agent_id", "agentId", "guid"])


class AgentJSON(Model):
    agent_id: Optional[str]

    @root_validator(pre=True)
    def _validate(cls, values):  # noqa
        if "agent_id" in values:
            return values
        elif "agentId" in values:
            values["agent_id"] = values["agentId"]
            return values
        elif "guid" in values:
            values["agent_id"] = values["guid"]
            return values
        else:
            raise ValueError(
                "A json key of 'agent_id', 'agentId', or 'guid' is required"
            )
