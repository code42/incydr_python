from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import StringConstraints
from typing_extensions import Annotated

from _incydr_sdk.enums.watchlists import WatchlistType


class UpdateExcludedUsersRequest(BaseModel):
    userIds: Optional[List[str]] = Field(
        None,
        description="A list of user IDs to add or remove.",
        max_length=100,
    )


class UpdateExcludedActorsRequest(BaseModel):
    actorIds: Optional[List[str]] = Field(
        None,
        description="A list of actor IDs to add or remove.",
        max_length=100,
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
        None,
        description="A list of user IDs to add or remove.",
        max_length=100,
    )
    watchlistId: Optional[str] = Field(
        None, description="A unique watchlist ID.", examples=["123"]
    )


class UpdateIncludedActorsRequest(BaseModel):
    actorIds: Optional[List[str]] = Field(
        None,
        description="A list of actor IDs to add or remove.",
        max_length=100,
    )
    watchlistId: Optional[str] = Field(
        None, description="A unique watchlist ID.", examples=["123"]
    )


class CreateWatchlistRequest(BaseModel):
    description: Optional[Annotated[str, StringConstraints(max_length=250)]] = Field(
        None,
        description="The optional description of a custom watchlist.",
        examples=["List of users that fit a custom use case."],
    )
    title: Optional[Annotated[str, StringConstraints(max_length=50)]] = Field(
        None,
        description="The required title for a custom watchlist.",
        examples=["My Custom List"],
    )
    watchlistType: Union[WatchlistType, str]
    model_config = ConfigDict(use_enum_values=True)


class ListWatchlistsRequest(BaseModel):
    page: int = 1
    pageSize: int = 100
    userId: Optional[str] = None


class ListWatchlistsRequestV2(BaseModel):
    page: int = 1
    pageSize: int = 100
    actorId: Optional[str] = None


class UpdateWatchlistRequest(BaseModel):
    description: Optional[Annotated[str, StringConstraints(max_length=250)]] = Field(
        None,
        description="The updated description of a custom watchlist.",
        examples=["List of users that fit a custom use case."],
    )
    title: Optional[Annotated[str, StringConstraints(max_length=50)]] = Field(
        None,
        description="The updated title for a custom watchlist.",
        examples=["My Custom List"],
    )
