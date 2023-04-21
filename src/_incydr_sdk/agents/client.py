from itertools import count
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

import requests

from ..enums import SortDirection
from .models import Agent
from .models import AgentsPage
from .models import AgentType
from .models import AgentUpdateRequest
from .models import QueryAgentsRequest
from .models import SortKeys


class AgentsV1:
    """
    Client for `/v1/agents` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.agents.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_page(
        self,
        active: bool = None,
        agent_type: Optional[AgentType] = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
        page_num: int = 1,
        page_size: int = 500,
    ) -> AgentsPage:
        """
        Get a page of agents.

        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **active**: `bool | None` - When `True`, return only active agents. When `False`, return only deactivated agents. Defaults to `None` (returning both).
        * **agent_type**: `AgentType | str | None` - Return only agents of given type.
        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page.
        * **sort_dir**: `SortDirection` - `asc` or `desc`. The direction in which to sort the response based on the corresponding key. Defaults to `asc`.
        * **sort_key**: `[SortKeys][agents-sort-keys]` - Values on which the response will be sorted. Defaults to agent name.

        **Returns**: An `[AgentsPage][agentspage-model]` object.
        """
        data = QueryAgentsRequest(
            active=active,
            agentType=agent_type,
            srtDir=sort_dir,
            srtKey=sort_key,
            pageSize=page_size,
            page=page_num,
        )
        response = self._parent.session.get("/v1/agents", params=data.dict())
        return AgentsPage.parse_response(response)

    def iter_all(
        self,
        active: bool = None,
        agent_type: Optional[AgentType] = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NAME,
        page_size: int = 500,
    ) -> Iterator[Agent]:
        """
        Iterate over all agents.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Agent`][agent-model] objects.
        """
        for page_num in count(1):
            page = self.get_page(
                active=active,
                agent_type=agent_type,
                sort_dir=sort_dir,
                sort_key=sort_key,
                page_num=page_num,
                page_size=page_size,
            )
            yield from page.agents
            if len(page.agents) < page_size:
                break

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get a single agent.

        **Parameters**:

        * **agent_id**: `str` (required) - The unique ID for the agent.

        **Returns**: An [`Agent`][agent-model] object representing the agent.
        """
        response = self._parent.session.get(f"/v1/agents/{agent_id}")
        return Agent.parse_response(response)

    def update(
        self, agent_id: str, name: str = None, external_reference: str = None
    ) -> requests.Response:
        """
        Update an agent.

        **Parameters:**

        * **agent_id**: `str` (required) - The unique ID for the agent.
        * **name**: `str | None` - The updated name for the agent.
        * **external_reference**: `str | None` - The updated external reference info for the agent.

        **Returns**: A `requests.Response` indicating success.
        """
        data = AgentUpdateRequest(name=name, externalReference=external_reference)
        return self._parent.session.put(f"/v1/agents/{agent_id}", json=data.dict())

    def activate(self, agent_ids: Union[str, List[str]]) -> requests.Response:
        """
        Activate a set of agents.

        **Parameters**:

        * **agent_ids**: `str | List[str]` - An agent ID or list of agent IDs to activate.

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(agent_ids, str):
            agent_ids = [agent_ids]
        return self._parent.session.post(
            "/v1/agents/activate", json={"agentIds": agent_ids}
        )

    def deactivate(self, agent_ids: Union[str, List[str]]) -> requests.Response:
        """
        Deactivate a set of agents.

        **Parameters**:

        * **agent_ids**: `str | List[str]` - An agent ID or list of agent IDs to deactivate.

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(agent_ids, str):
            agent_ids = [agent_ids]
        return self._parent.session.post(
            "/v1/agents/deactivate", json={"agentIds": agent_ids}
        )


class AgentsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = AgentsV1(self._parent)
        return self._v1
