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


class RiskProfile(ResponseModel):
    """A model representing a risk profile.

    **Fields**:

    * **active**: `bool` - Whether the actor is active.
    * **cloud_alias**: `List[str]` - List of cloud aliases for the actor.
    * **country**: `str` - The actor's country.
    * **deleted**: `bool` - Whether the actor has been deleted.
    * **department**: `str` - The actor's department.
    * **display_name**: `str` - The actor's display name.
    * **division**: `str` - The actor's division.
    * **employment_type**: `str` - The actor's employment type.
    * **end_date**: `Date` - Departure date for the actor
    * **locality**: `str` - The actor's locality (city).
    * **manager_display_name**: `str` - The actor's manager's display name.
    * **manager_id**: `str` - Unique actor ID of the actor's manager.
    * **manager_username**: `str` - The Code42 actorname of the actor's manager.
    * **notes**: `str` - Additional notes about the actor.
    * **region**: `str` - The actor's region (state).
    * **start_date**: `Date` - Starting date for the actor.
    * **support_user**: `bool` - Whether the actor is a support actor.
    * **tenant_id**: `str` - Unique tenant ID.
    * **title**: `str` - The actor's job title.
    * **user_id**: `str` - Unique actor ID.
    * **username**: `str` - actor's Code42 actorname.
    """

    active: Optional[bool] = Field(None, description="Whether the actor is active.")
    cloud_aliases: Optional[List[str]] = Field(
        None, description="A list of cloud aliases for the actor.", alias="cloudAliases"
    )
    country: Optional[str] = Field(None, description="The actor's country.")
    deleted: Optional[bool] = Field(None, description="Whether the actor is deleted.")
    department: Optional[str] = Field(None, description="The actor's department.")
    display_name: Optional[str] = Field(
        None, description="The actor's friendly display name.", alias="displayName"
    )
    division: Optional[str] = Field(None, description="The actor's division.")
    employment_type: Optional[str] = Field(
        None, description="The actor's employment type.", alias="employmentType"
    )
    end_date: Optional[Date] = Field(None, alias="endDate")
    locality: Optional[str] = Field(None, description="The actor's locality (city).")
    manager_display_name: Optional[str] = Field(
        None,
        description="The actor's manager's friendly display name.",
        alias="managerDisplayName",
    )
    manager_id: Optional[str] = Field(
        None,
        description="The Code42 actor ID of the actor's manager.",
        alias="managerId",
    )
    manager_username: Optional[str] = Field(
        None,
        description="The Code42 actorname of the actor's manager.",
        alias="managerUsername",
    )
    notes: Optional[str] = Field(
        None,
        description="Notes about the actor.",
        table=lambda f: f if f is None else Markdown(f),
    )
    region: Optional[str] = Field(None, description="The actor's region (state).")
    start_date: Optional[Date] = Field(None, alias="startDate")
    support_user: Optional[bool] = Field(
        None, description="Whether the actor is a support actor.", alias="supportUser"
    )
    tenant_id: Optional[str] = Field(
        None, description="A unique tenant ID.", alias="tenantId"
    )
    title: Optional[str] = Field(None, description="The actor's job title.")
    user_id: Optional[str] = Field(
        None, description="A unique actor ID.", alias="userId"
    )
    username: Optional[str] = Field(None, description="The actor's Code42 actorname.")


class RiskProfilesPage(ResponseModel):
    """
    A model representing a page of `RiskProfile` objects.

    **Fields**:

    * **total_count**: `int` The total count of all risk profiles.
    * **user_risk_profiles**: `List[RiskProfile]` The list of `n` number of risk profiles
                            retrieved from the query, where `n=page_size`.
    """

    total_count: Optional[int] = Field(
        None,
        description="The total count of all risk profiles.",
        example=10,
        alias="totalCount",
    )
    user_risk_profiles: Optional[List[RiskProfile]] = Field(
        None, alias="userRiskProfiles"
    )


class QueryRiskProfilesRequest(Model):
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


class UpdateRiskProfileRequest(Model):
    endDate: Optional[Date] = None
    notes: Optional[str] = Field(
        None,
        description="Notes to add to the risk profile.",
        example="These are my notes",
    )
    startDate: Optional[Date] = None


class AddCloudAliasesRequest(Model):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the actor to add cloud aliases.", example="123"
    )


class DeleteCloudAliasesRequest(Model):
    cloudAliases: Optional[List[str]] = None
    userId: Optional[str] = Field(
        None, description="The ID of the actor to delete cloud aliases.", example="123"
    )
