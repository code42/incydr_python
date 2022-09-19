from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel
from incydr.enums.trusted_activities import ActivityType
from incydr.enums.trusted_activities import Name
from incydr.enums.trusted_activities import PrincipalType


class ProviderObject(ResponseModel):
    name: Optional[Name] = Field(
        None,
        description="The name of a provider for a specified activity action.\n  ### Supported providers for trusted "
        "activity type and actions\n\n  - `DOMAIN`\n    - `CLOUD_SHARE`\n      - `BOX`\n      - "
        "`GOOGLE_DRIVE` \n      - `ONE_DRIVE`\n    - `CLOUD_SYNC`\n      - `BOX`\n      - `GOOGLE_DRIVE` "
        "\n      - `ICLOUD` \n      - `ONE_DRIVE` \n    - `EMAIL` \n      - `GMAIL`\n      - "
        "`OFFICE_365`\n  - `ACCOUNT_NAME`\n    - `CLOUD_SYNC`\n      - `DROPBOX`\n      - `ONE_DRIVE`\n",
    )


class ActivityAction(ResponseModel):
    providers: Optional[List[ProviderObject]] = Field(
        None,
        description="A list of enabled providers for the specified activity action.",
    )
    activity_type: Optional[ActivityType] = Field(
        None,
        description="The type of an activity action.\n### Supported trusted activity types for each activity action "
        "type\n\n- `CLOUD_SHARE` \n  - `DOMAIN`\n- `CLOUD_SYNC` \n  - `DOMAIN`\n  - `ACCOUNT_NAME`\n- "
        "`EMAIL` \n  - `DOMAIN`\n- `FILE_UPLOAD`\n  - `DOMAIN`\n\nNote: `SLACK` and `URL_PATH` do not "
        "need any activity actions specified.\n",
        alias="activityType",
    )


class ActivityActionGroup(ResponseModel):
    activity_actions: Optional[List[ActivityAction]] = Field(
        None,
        description="The list of activity actions for an activity action group.",
        alias="activityActions",
    )
    name: Optional[Name] = Field(
        None,
        description="The name of the activity action group. Currently, only `DEFAULT` activity action group is "
        "supported.",
    )


class TrustedActivity(ResponseModel):
    activity_action_groups: Optional[List[ActivityActionGroup]] = Field(
        None,
        description="The list of activity actions associated with the activity.",
        alias="activityActionGroups",
    )
    activity_id: Optional[str] = Field(
        None,
        description="The unique identifier of the trusted activity.",
        alias="activityId",
    )
    description: Optional[str] = Field(
        None, description="A description of the trusted activity."
    )
    principal_type: Optional[PrincipalType] = Field(None, alias="principalType")
    activity_type: Optional[ActivityType] = Field(
        None, description="The type of the trusted activity.", alias="activityType"
    )
    update_time: Optional[datetime] = Field(
        None,
        description="The time at which the trust activity was last created or modified.",
        alias="updateTime",
    )
    updated_by_principal_id: Optional[str] = Field(
        None,
        description="The unique identifier of the user who last updated the trust activity.",
        alias="updatedByPrincipalId",
    )
    updated_by_principal_name: Optional[str] = Field(
        None,
        description="The username of the user who last updated the trusted activity.",
        alias="updatedByPrincipalName",
    )
    value: Optional[str] = Field(None, description="The value of the trusted activity.")


class UpdateTrustedActivity(ResponseModel):
    activity_action_groups: Optional[List[ActivityActionGroup]] = Field(
        None,
        description="The list of activity action groups for the trusted activity. \n- `DOMAIN` - If array is empty, "
        "existing activity action groups are maintained. \n- `ACCOUNT_NAME` - Atleast 1 activity action "
        "group is required.\n- `SLACK` - No activity action groups are allowed - array must be empty.\n- "
        "`URL_PATH` - No activity action groups are allowed - array must be empty.\n",
        alias="activityActionGroups",
    )
    description: Optional[str] = Field(
        None, description="The description of the trusted activity."
    )
    activity_type: Optional[ActivityType] = Field(
        None,
        description="The type of the trusted activity.\n\nNote: The `ACCOUNT_NAME` trusted activity type requires "
        "agent version 1.5.0 or later for Incydr \nProfessional, Enterprise, Gov F2, and Horizon product "
        "plans, and Code42 app version 9.0.0 or later for \nIncydr Basic, Advanced, and Gov F1 product "
        "plans.\n",
        alias="activityType",
    )
    value: Optional[str] = Field(None, description="The value of the trusted activity.")


class TrustedActivitiesPage(ResponseModel):
    total_count: Optional[float] = Field(None, alias="totalCount")
    trusted_activities: Optional[List[TrustedActivity]] = Field(
        None,
        description="A list of TrustedActivityResponses",
        alias="trustedActivities",
    )


class QueryTrustedActivitiesRequest(BaseModel):
    page: Optional[int]
    page_size: Optional[int]
    activity_type: Optional[str]
    sort_key: Optional[str]
    sort_direction: Optional[str]

    class Config:
        use_enum_values = True


class CreateTrustedActivityRequest(BaseModel):
    activity_type: Optional[str]
    value: Optional[str]
    description: Optional[str]
    activity_action_groups: Optional[list[ActivityActionGroup]]
