from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums import _Enum


class SortKeys(_Enum):
    """Possible keys to sort agents list results by."""

    NAME = "NAME"
    USER_ID = "USER_ID"
    AGENT_TYPE = "AGENT_TYPE"
    OS_HOSTNAME = "OS_HOSTNAME"
    LAST_CONNECTED = "LAST_CONNECTED"
    OS_NAME = "OS_NAME"


class AgentType(_Enum):
    """Possible types of agents."""

    CODE42AAT = "CODE42AAT"
    COMBINED = "COMBINED"
    CODE42 = "CODE42"


class Agent(ResponseModel):
    """
    A model representing an Incydr agent.

    **Fields**:

    * **agent_id**: `str` The globally unique ID (guid) for this agent.
    * **name**: `str` The editable name of the agent.
    * **user_id**: `str` The unique ID of the user the agent is assigned to.
    * **os_hostname**: `str` The hostname reported by the OS the agent is running on.
    * **os_name**: `str` The name of the OS the agent is running on.
    * **active**: `bool` If the agent status is active.
    * **agent_type**: `[AgentType][agent-type]` The type of agent.
    * **app_version**: `str` The app version of the agent.
    * **product_version**: `str` The product version of the agent.
    * **last_connected**: `datetime` The time the agent last connected to a Code42 Authority server.
    * **external_reference**: `str` Editable reference information (useful for identifying an agent in external systems).
    * **creation_date**: `datetime` The time the agent was first registered.
    * **modification_date**: `datetime` The time the agent's database entry was last updated.
    """

    agent_id: Optional[str] = Field(alias="agentId")
    name: Optional[str]
    user_id: Optional[str] = Field(alias="userId")
    os_hostname: Optional[str] = Field(alias="osHostname")
    os_name: Optional[str] = Field(alias="osName")
    active: Optional[bool]
    agent_type: Optional[AgentType] = Field(alias="agentType")
    app_version: Optional[str] = Field(alias="appVersion")
    product_version: Optional[str] = Field(alias="productVersion")
    last_connected: Optional[datetime] = Field(alias="lastConnected")
    external_reference: Optional[str] = Field(alias="externalReference")
    creation_date: Optional[datetime] = Field(alias="creationDate")
    modification_date: Optional[datetime] = Field(alias="modificationDate")


class AgentsPage(ResponseModel):
    """
    A model representing a page of Agents.

    **Fields**:

    * **agents**: `List[[Agent][agent-model]]` The list of agents returned from the query.
    * **total_count**: `int` Total number of agents found in query results.
    * **page_size**: `int` The maximum number of agents returned in query results page.
    * **page_num**: `int` The current page number of the query result set.
    """

    agents: List[Agent]
    total_count: int = Field(alias="totalCount")
    page_size: int = Field(alias="pageSize")
    page_num: int = Field(alias="page")


class AgentUpdateRequest(BaseModel):
    name: str
    externalReference: str


class QueryAgentsRequest(BaseModel):
    active: Optional[bool]
    agentType: Optional[AgentType]
    userId: Optional[str]
    srtKey: Optional[SortKeys]
    srtDir: Optional[str]
    pageSize: Optional[int]
    page: Optional[int]

    @validator("srtDir")
    def _validate(cls, value):  # noqa
        value = str(value).upper()
        assert value in ("ASC", "DESC")
        return value
