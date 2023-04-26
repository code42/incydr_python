from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import Field
from rich.markdown import Markdown

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel


class Date(ResponseModel):
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
    * **cloud_alias**: `List[str]` - List of cloud aliases for the user.
    * **country**: `str` - The user's country.
    * **deleted**: `bool` - Whether the user has been deleted.
    * **department**: `str` - The user's department.
    * **display_name**: `str` - The user's display name.
    * **division**: `str` - The user's division.
    * **employment_type**: `str` - The user's employment type.
    * **end_date**: `Date` - Departure date for the user
    * **locality**: `str` - The user's locality (city).
    * **manager_display_name**: `str` - The user's manager's display name.
    * **manager_id**: `str` - Unique user ID of the user's manager.
    * **manager_username**: `str` - The Code42 username of the user's manager.
    * **notes**: `str` - Additional notes about the user.
    * **region**: `str` - The user's region (state).
    * **start_date**: `Date` - Starting date for the user.
    * **support_user**: `bool` - Whether the user is a support user.
    * **tenant_id**: `str` - Unique tenant ID.
    * **title**: `str` - The user's job title.
    * **user_id**: `str` - Unique user ID.
    * **username**: `str` - User's Code42 username.
    """

    active: Optional[bool] = Field(None, description="Whether the user is active.")
    cloud_aliases: Optional[List[str]] = Field(
        None, description="A list of cloud aliases for the user.", alias="cloudAliases"
    )
    country: Optional[str] = Field(None, description="The user's country.")
    deleted: Optional[bool] = Field(None, description="Whether the user is deleted.")
    department: Optional[str] = Field(None, description="The user's department.")
    display_name: Optional[str] = Field(
        None, description="The user's friendly display name.", alias="displayName"
    )
    division: Optional[str] = Field(None, description="The user's division.")
    employment_type: Optional[str] = Field(
        None, description="The user's employment type.", alias="employmentType"
    )
    end_date: Optional[Date] = Field(None, alias="endDate")
    locality: Optional[str] = Field(None, description="The user's locality (city).")
    manager_display_name: Optional[str] = Field(
        None,
        description="The user's manager's friendly display name.",
        alias="managerDisplayName",
    )
    manager_id: Optional[str] = Field(
        None, description="The Code42 user ID of the user's manager.", alias="managerId"
    )
    manager_username: Optional[str] = Field(
        None,
        description="The Code42 username of the user's manager.",
        alias="managerUsername",
    )
    notes: Optional[str] = Field(
        None,
        description="Notes about the user.",
        table=lambda f: f if f is None else Markdown(f),
    )
    region: Optional[str] = Field(None, description="The user's region (state).")
    start_date: Optional[Date] = Field(None, alias="startDate")
    support_user: Optional[bool] = Field(
        None, description="Whether the user is a support user.", alias="supportUser"
    )
    tenant_id: Optional[str] = Field(
        None, description="A unique tenant ID.", alias="tenantId"
    )
    title: Optional[str] = Field(None, description="The user's job title.")
    user_id: Optional[str] = Field(
        None, description="A unique user ID.", alias="userId"
    )
    username: Optional[str] = Field(None, description="The user's Code42 username.")


class UserRiskProfilesPage(ResponseModel):
    """
    A model representing a page of `UserRiskProfile` objects.

    **Fields**:

    * **total_count**: `int` The total count of all user risk profiles.
    * **user_risk_profiles**: `List[UserRiskProfile]` The list of `n` number of user risk profiles
                            retrieved from the query, where `n=page_size`.
    """

    total_count: Optional[int] = Field(
        None,
        description="The total count of all user risk profiles.",
        example=10,
        alias="totalCount",
    )
    user_risk_profiles: Optional[List[UserRiskProfile]] = Field(
        None, alias="userRiskProfiles"
    )


class QueryUserRiskProfilesRequest(Model):
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
    support_user: Optional[bool]

    class Config:
        use_enum_values = True


class UpdateUserRiskProfileRequest(Model):
    endDate: Optional[Date] = None
    notes: Optional[str] = Field(
        None,
        description="Notes to add to the user risk profile.",
        example="These are my notes",
    )
    startDate: Optional[Date] = None


class AddCloudAliasesRequest(Model):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to add cloud aliases.", example="123"
    )


class DeleteCloudAliasesRequest(Model):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the user to delete cloud aliases.", example="123"
    )
