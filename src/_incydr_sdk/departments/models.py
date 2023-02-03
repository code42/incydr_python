from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class DepartmentsPage(ResponseModel):
    """
    A model representing a list of departments.

    **Fields**:

    * **departments**: `List[str]` - The list of `n` department names retrieved by the query, where `n=page_size`.
    * **total_count**: `int` - Total count of departments retrieved by the query.
    """

    departments: Optional[List[str]] = None
    total_count: Optional[int] = Field(
        None,
        description="The total count of all departments.",
        example=10,
        alias="totalCount",
    )


class GetPageRequest(BaseModel):
    page: int = 1
    page_size: int = None
    name: str = None
