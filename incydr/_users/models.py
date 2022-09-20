from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel


class User(ResponseModel):
    """
    A model representing a user.

    **Fields**:

    * **legacy_user_id**: `str` - The user ID to use for older console-based APIs that require a device ID.
    * **user_id**: `str` - The globally unique ID (guid) for this user.
    * **username**: `str` - The name the user uses to log in to Code42.
    * **first_name**: `str` - The first (given) name of the user.
    * **last_name**: `str` - The last (family) name of the user.
    * **legacy_org_id**: `str` - The org ID to use for older console-based APIs that require an org Id. If your endpoint domain starts with "console" instead of "api", use this Id for endpoints that require an orgId.
    * **org_id**: `str` - The ID of the Code42 organization this user belongs to.
    * **org_guid**: `str` - The unique org ID of the Code42 organization this user belongs to. This value should be used for actions conducted through the org APIs.
    * **org_name**: `str` - The name of the Code42 organization this user belongs to.
    * **notes**: `str` - Descriptive information about the user.
    * **active**: `bool` - Whether or not the user is enabled.
    * **blocked**: `bool` - Whether or not logins and restores are disabled for the user.
    * **creation_date**: `str` - The date and time the user was created.
    * **modification_date**: `str` - The date and time the user was last modified.
    """

    legacy_user_id: Optional[str] = Field(
        alias="legacyUserId",
        description="The user ID to use for older console-based APIs that require a "
        'user Id. If your endpoint domain starts with "console" '
        'instead of "api", use this Id for endpoints that require a '
        "userId.",
        allow_mutation=False,
    )
    user_id: Optional[str] = Field(
        alias="userId",
        description="A globally unique ID for this user.",
        allow_mutation=False,
    )
    username: Optional[str] = Field(
        description="The name the user uses to log in to Code42.",
        allow_mutation=False,
    )
    first_name: Optional[str] = Field(
        alias="firstName",
        description="The first (given) name of the user.",
        allow_mutation=False,
    )
    last_name: Optional[str] = Field(
        alias="lastName",
        description="The last (family) name of the user.",
        allow_mutation=False,
    )
    legacy_org_id: Optional[str] = Field(
        alias="legacyOrgId",
        description="The org ID to use for older console-based APIs that require an "
        'org Id. If your endpoint domain starts with "console" instead '
        'of "api", use this Id for endpoints that require an orgId.',
        allow_mutation=False,
    )
    org_id: Optional[str] = Field(
        alias="orgId",
        description="The ID of the Code42 organization this user belongs to.",
        allow_mutation=False,
    )
    org_guid: Optional[str] = Field(
        alias="orgGuid",
        description="The unique org ID of the Code42 organization this user belongs to. This value should be used for actions conducted through the org APIs.",
        allow_mutation=False,
    )
    org_name: Optional[str] = Field(
        alias="orgName",
        description="The name of the Code42 organization this user belongs to.",
        allow_mutation=False,
    )
    notes: Optional[str] = Field(
        description="Descriptive information about the user.",
        allow_mutation=False,
    )
    active: Optional[bool] = Field(
        description="Whether or not the user is enabled.",
        allow_mutation=False,
    )
    blocked: Optional[bool] = Field(
        description="Whether or not logins and restores are disabled for the user.",
        allow_mutation=False,
    )
    creation_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="creationDate",
        description="The date and time the user was created.",
    )
    modification_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="modificationDate",
        description="The date and time the user was last modified.",
    )

    class Config:
        validate_assignment = True


class UsersPage(ResponseModel):
    """
    A model representing a page of `User` objects.

    **Fields**:

    * **users**: `List[User]` - The list of `n` number of users retrieved from the query, where `n=page_size`.
    * **total_count**: `int` - Total count of users found by query.
    """

    users: Optional[List[User]] = Field(description="A list of users")
    total_count: Optional[int] = Field(
        alias="totalCount", description="The total number of users"
    )


class QueryUsersRequest(BaseModel):
    active: Optional[bool]
    blocked: Optional[bool]
    username: Optional[str]
    page: Optional[int] = 1
    pageSize: Optional[int] = 100

    class Config:
        use_enum_values = True


class Role(ResponseModel):
    """
    A model representing a user role.

    **Fields**:

    * **role_id**: `str` - A role ID.
    * **role_name**: `str` - A role name.
    * **modification_date**: `str` - The date and time this role for the user was last modified.
    * **creation_date**: `str` - The date and time this role for the user was created.
    * **permission_ids**: `str` - The permission IDs associated with this role.
    """

    role_id: Optional[str] = Field(
        alias="roleId", description="A role ID.", allow_mutation=False
    )
    role_name: Optional[str] = Field(
        alias="roleName", description="A role name.", allow_mutation=False
    )
    creation_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="creationDate",
        description="The date and time this role for the user was created.",
    )
    modification_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="modificationDate",
        description="The date and time this role for the user was last modified.",
    )
    permission_ids: Optional[List[str]] = Field(
        allow_mutation=False,
        alias="permissionIds",
        description="The permission IDs associated with this role.",
    )

    class Config:
        validate_assignment = True


class UpdateRolesRequest(BaseModel):
    roleIds: Optional[List[str]]


class UpdateRolesResponse(ResponseModel):
    """
    A model representing a user role.

    **Fields**:

    * **processed_replacement_role_ids**: `List[str]` - The role IDs processed.
    * **newly_assigned_roles_ids**: `List[str]` - The role IDs newly assigned to the user.
    * **unassigned_roles_ids**: `List[str]` - The role IDs unassigned from the user.
    * **ignored_roles_ids**: `List[str]` - The role IDs ignored.
    """

    processed_replacement_role_ids: Optional[List[str]] = Field(
        alias="processedReplacementRoleIds",
        description="The role IDs processed.",
        allow_mutation=False,
    )
    newly_assigned_roles_ids: Optional[List[str]] = Field(
        alias="newlyAssignedRolesIds",
        description="The role IDs newly assigned to the user.",
        allow_mutation=False,
    )
    unassigned_roles_ids: Optional[List[str]] = Field(
        alias="unassignedRolesIds",
        description="The role IDs unassigned from the user.",
        allow_mutation=False,
    )
    ignored_roles_ids: Optional[List[str]] = Field(
        alias="ignoredRolesIds",
        description="The role IDs ignored.",
        allow_mutation=False,
    )

    class Config:
        validate_assignment = True


class MoveUserRequest(BaseModel):
    orgGuid: Optional[str]
