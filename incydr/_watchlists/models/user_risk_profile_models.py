# USER RISK PROFILES
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field

from incydr._core.models import ResponseModel
from incydr._watchlists.models.responses import Date


class UpdatedUserRiskProfile(ResponseModel):
    class Config:
        extra = Extra.forbid

    endDate: Optional[Date] = None
    notes: Optional[str] = Field(
        None,
        description="Notes to add to the user risk profile.",
        example="These are my notes",
    )
    startDate: Optional[Date] = None


class UserRiskProfile(ResponseModel):
    class Config:
        extra = Extra.forbid

    active: Optional[bool] = Field(None, description="Whether the user is active.")
    cloudAliases: Optional[List[str]] = Field(
        None, description="A list of cloud aliases for the user."
    )
    country: Optional[str] = Field(None, description="The user's country.")
    deleted: Optional[bool] = Field(None, description="Whether the user is deleted.")
    department: Optional[str] = Field(None, description="The user's department.")
    displayName: Optional[str] = Field(
        None, description="The user's friendly display name."
    )
    division: Optional[str] = Field(None, description="The user's division.")
    employmentType: Optional[str] = Field(
        None, description="The user's employment type."
    )
    endDate: Optional[Date] = None
    locality: Optional[str] = Field(None, description="The user's locality (city).")
    managerDisplayName: Optional[str] = Field(
        None, description="The user's manager's friendly display name."
    )
    managerId: Optional[str] = Field(
        None, description="The Code42 user ID of the user's manager."
    )
    managerUsername: Optional[str] = Field(
        None, description="The Code42 username of the user's manager."
    )
    notes: Optional[str] = Field(None, description="Notes about the user.")
    region: Optional[str] = Field(None, description="The user's region (state).")
    startDate: Optional[Date] = None
    supportUser: Optional[bool] = Field(
        None, description="Whether the user is a support user."
    )
    tenantId: Optional[str] = Field(None, description="A unique tenant ID.")
    title: Optional[str] = Field(None, description="The user's job title.")
    userId: Optional[str] = Field(None, description="A unique user ID.")
    username: Optional[str] = Field(None, description="The user's Code42 username.")


class ListUserRiskProfilesResponse(ResponseModel):
    class Config:
        extra = Extra.forbid

    totalCount: Optional[int] = Field(
        None, description="The total count of all user risk profiles.", example=10
    )
    userRiskProfiles: Optional[List[UserRiskProfile]] = None


class AddCloudAliasesRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to add cloud aliases.", example="123"
    )


class DeleteCloudAliasesRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to delete cloud aliases.", example="123"
    )
