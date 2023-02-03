from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import constr
from pydantic import Field

from _incydr_sdk.enums.watchlists import WatchlistType


class UpdateExcludedUsersRequest(BaseModel):
    userIds: Optional[List[str]] = Field(
        None, description="A list of user IDs to add or remove."
    )


class UpdateIncludedDepartmentsRequest(BaseModel):
    departments: Optional[List[str]] = Field(
        None, description="A list of departments to add or remove."
    )


class UpdateIncludedDirectoryGroupsRequest(BaseModel):
    groupIds: Optional[List[str]] = Field(
        None, description="A list of group IDs to add or remove."
    )


class UpdateIncludedUsersRequest(BaseModel):
    userIds: Optional[List[str]] = Field(
        None, description="A list of user IDs to add or remove."
    )
    watchlistId: Optional[str] = Field(
        None, description="A unique watchlist ID.", example="123"
    )


class CreateWatchlistRequest(BaseModel):
    description: Optional[constr(max_length=250)] = Field(
        None,
        description="The optional description of a custom watchlist.",
        example="List of users that fit a custom use case.",
    )
    title: Optional[constr(max_length=50)] = Field(
        None,
        description="The required title for a custom watchlist.",
        example="My Custom List",
    )
    watchlistType: WatchlistType

    class Config:
        use_enum_values = True


class ListWatchlistsRequest(BaseModel):
    page: int = 1
    pageSize: int = 100
    userId: Optional[str]


class UpdateWatchlistRequest(BaseModel):
    description: Optional[constr(max_length=250)] = Field(
        None,
        description="The updated description of a custom watchlist.",
        example="List of users that fit a custom use case.",
    )
    title: Optional[constr(max_length=50)] = Field(
        None,
        description="The updated title for a custom watchlist.",
        example="My Custom List",
    )
