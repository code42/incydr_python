from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class GetRulesRequest(BaseModel):
    PageNumber: int = 0
    PageSize: int
    WatchlistId: Optional[str] = None


class UserRequest(BaseModel):
    userIdFromAuthority: str = Field(
        None, description="User ID from authority.", example="userIdFromAuthority"
    )
    aliases: List[str] = Field(
        None,
        description="List of user aliases corresponding to the user ID from the authority.",
        example=["userAlias1", "userAlias2"],
    )
