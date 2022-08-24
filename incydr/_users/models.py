from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel


class User(ResponseModel):
    legacy_user_id: Optional[str] = Field(alias="legacyUserId",
                                          description="The user ID to use for older console-based APIs that require a "
                                                      "user Id. If your endpoint domain starts with \"console\" "
                                                      "instead of \"api\", use this Id for endpoints that require a "
                                                      "userId.")
    user_id: Optional[str] = Field(alias="userId", description="A globally unique ID for this user.")
    username: Optional[str] = Field(description="The name the user uses to log in to Code42.")
    first_name: Optional[str] = Field(alias="firstName", description="The first (given) name of the user.")
    last_name: Optional[str] = Field(alias="lastName", description="The last (family) name of the user.")
    legacy_org_id: Optional[str] = Field(alias="legacyOrgId",
                                         description="The org ID to use for older console-based APIs that require an "
                                                     "org Id. If your endpoint domain starts with \"console\" instead "
                                                     "of \"api\", use this Id for endpoints that require an orgId.")
    org_id: Optional[str] = Field(alias="orgId",
                                  description="The globally unique ID of the Code42 organization this user belongs to.")
    org_name: Optional[str] = Field(alias="orgName",
                                    description="The name of the Code42 organization this user belongs to.")
    notes: Optional[str] = Field(description="Descriptive information about the user.")
    active: Optional[bool] = Field(description="Whether or not the user is enabled.")
    blocked: Optional[bool] = Field(description="Whether or not logins and restores are disabled for the user.")
    creation_date: datetime = Field(allow_mutation=False, alias="creationDate",
                                    description="The date and time the user was created.")
    modification_date: Optional[datetime] = Field(allow_mutation=False, alias="modificationDate",
                                                  description="The date and time the user was last modified.")

    class Config:
        validate_assignment = True


class UsersPage(ResponseModel):
    users: Optional[List[User]] = Field(description="A list of users")
    total_count: Optional[int] = Field(alias="totalCount", description="The total number of users")


class QueryUsersRequest(BaseModel):
    active: Optional[bool]
    blocked: Optional[bool]
    username: Optional[str]
    page: Optional[int] = 1
    pageSize: Optional[int] = 100

    class Config:
        use_enum_values = True
