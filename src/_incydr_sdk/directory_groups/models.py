from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class DirectoryGroup(ResponseModel):
    group_id: Optional[str] = Field(
        None, description="A unique group ID.", example="23", alias="groupId"
    )
    name: Optional[str] = Field(None, example="Research and development")


class DirectoryGroupsPage(ResponseModel):
    """
    A model representing a list of directory groups.

    **Fields**:

    * **directory_groups**: `List[DirectoryGroup`] - The list of `n` directory groups retrieved by the query, where `n=page_size`.
    * **total_count**: `int` - Total count of directory groups retrieved by the query.
    """

    directory_groups: Optional[List[DirectoryGroup]] = Field(
        None, alias="directoryGroups"
    )
    total_count: Optional[int] = Field(
        None,
        description="The total count of all directory groups.",
        example=10,
        alias="totalCount",
    )
