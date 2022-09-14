from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel


class Date(BaseModel):
    year: Optional[int] = Field(
        None,
        description="Year of date. Must be from 1 to 9999, or 0 if specifying a date without\n a year.",
    )
    month: Optional[int] = Field(
        None,
        description="Month of year. Must be from 1 to 12, or 0 if specifying a year without a\n month and day.",
    )
    day: Optional[int] = Field(
        None,
        description="Day of month. Must be from 1 to 31 and valid for the year and month, or 0\n if specifying a year "
                    "by itself or a year and month where the day is not\n significant.",
    )


class UserRiskProfile(ResponseModel):
    """A model representing a user risk profile.

    **Fields**:

    * **active**: `bool` - Whether the user is active.
    * **cloudAliases**: `List[str]` - List of cloud aliases for the user.
    * **country**: `str` - The user's country.
    * **deleted**: `bool` - Whether the user is deleted.
    * **department**: `str` - The user's department.
    * **displayName**: `str` - The user's friendly display name.
    * **division**: `str` - The user's division.
    * **employmentType**: `str` - The user's employment type.
    * **endDate**: `Date` - The end date
    * **locality**: `str` - The user's locality (city).
    * **managerDisplayName**: `str` - The user's manager's friendly display name.
    * **managerId**: `str` - The Code42 user ID of the user's manager.
    * **managerUsername**: `str` - The Code42 username of the user's manager.
    * **notes**: `str` - Notes about the user.
    * **region**: `str` - The user's region (state).
    * **startDate**: `Date` - The start date
    * **supportUser**: `bool` - Whether the user is a support user.
    * **tenantId**: `str` - The unique tenant ID.
    * **title**: `str` - The user's job title.
    * **userId**: `str` - The unique user ID.
    * **username**: `str` - The user's Code42 username.
    """

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


class UserRiskProfilesPage(ResponseModel):
    """
    A model representing a page of `UserRiskProfile` objects.

    **Fields**:

    * **total_count**: `int` The total count of all user risk profiles.
    * **userRiskProfiles**: `List[UserRiskProfile]` The list of `n` number of user risk profiles
                            retrieved from the query, where `n=page_size`.
    """

    totalCount: Optional[int] = Field(
        None, description="The total count of all user risk profiles.", example=10
    )
    userRiskProfiles: Optional[List[UserRiskProfile]] = None


class QueryUserRiskProfilesRequest(BaseModel):
    page: Optional[int]
    page_size: Optional[int]
    manager_id: Optional[str]
    title: Optional[str]
    division: Optional[str]
    department: Optional[str]
    employment_type: Optional[str]
    country: Optional[str]
    region: Optional[str]
    locality: Optional[str]
    active: Optional[bool]
    deleted: Optional[bool]
    supportUser: Optional[bool]

    class Config:
        use_enum_values = True


class UpdateUserRiskProfile(BaseModel):
    endDate: Optional[Date] = None
    notes: Optional[str] = Field(
        None,
        description="Notes to add to the user risk profile.",
        example="These are my notes",
    )
    startDate: Optional[Date] = None


class AddCloudAliasesRequest(BaseModel):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to add cloud aliases.", example="123"
    )


class DeleteCloudAliasesRequest(BaseModel):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to delete cloud aliases.", example="123"
    )
