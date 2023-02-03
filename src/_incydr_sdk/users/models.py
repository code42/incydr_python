from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field
from rich.markdown import Markdown

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel


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
        None,
        alias="legacyUserId",
        description="The user ID to use for older console-based APIs that require a "
        'user Id. If your endpoint domain starts with "console" '
        'instead of "api", use this Id for endpoints that require a '
        "userId.",
    )
    user_id: Optional[str] = Field(
        None,
        alias="userId",
        description="A globally unique ID for this user.",
    )
    username: Optional[str] = Field(
        None,
        description="The name the user uses to log in to Code42.",
    )
    first_name: Optional[str] = Field(
        None,
        alias="firstName",
        description="The first (given) name of the user.",
    )
    last_name: Optional[str] = Field(
        None,
        alias="lastName",
        description="The last (family) name of the user.",
    )
    legacy_org_id: Optional[str] = Field(
        None,
        alias="legacyOrgId",
        description="The org ID to use for older console-based APIs that require an "
        'org Id. If your endpoint domain starts with "console" instead '
        'of "api", use this Id for endpoints that require an orgId.',
    )
    org_id: Optional[str] = Field(
        None,
        alias="orgId",
        description="The ID of the Code42 organization this user belongs to.",
    )
    org_guid: Optional[str] = Field(
        None,
        alias="orgGuid",
        description="The unique org ID of the Code42 organization this user belongs to. This value should be used for actions conducted through the org APIs.",
    )
    org_name: Optional[str] = Field(
        None,
        alias="orgName",
        description="The name of the Code42 organization this user belongs to.",
    )
    notes: Optional[str] = Field(
        None,
        description="Descriptive information about the user.",
        table=lambda f: f if f is None else Markdown(f),
    )
    active: Optional[bool] = Field(
        None,
        description="Whether or not the user is enabled.",
    )
    blocked: Optional[bool] = Field(
        None,
        description="Whether or not logins and restores are disabled for the user.",
    )
    creation_date: Optional[datetime] = Field(
        None,
        alias="creationDate",
        description="The date and time the user was created.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        alias="modificationDate",
        description="The date and time the user was last modified.",
    )


class UsersPage(ResponseModel):
    """
    A model representing a page of `User` objects.

    **Fields**:

    * **users**: `List[User]` - The list of `n` number of users retrieved from the query, where `n=page_size`.
    * **total_count**: `int` - Total count of users found by query.
    """

    users: Optional[List[User]] = Field(None, description="A list of users")
    total_count: Optional[int] = Field(
        None, alias="totalCount", description="The total number of users"
    )


class QueryUsersRequest(Model):
    active: Optional[bool]
    blocked: Optional[bool]
    username: Optional[str]
    page: Optional[int] = 1
    pageSize: Optional[int] = 100


class UserRole(ResponseModel):
    """
    A model representing a user role.

    **Fields**:

    * **role_id**: `str` - A role ID.
    * **role_name**: `str` - A role name.
    * **modification_date**: `str` - The date and time this role for the user was last modified.
    * **creation_date**: `str` - The date and time this role for the user was created.
    * **permission_ids**: `str` - The permission IDs associated with this role.
    """

    role_id: Optional[str] = Field(None, alias="roleId", description="A role ID.")
    role_name: Optional[str] = Field(None, alias="roleName", description="A role name.")
    creation_date: Optional[datetime] = Field(
        None,
        alias="creationDate",
        description="The date and time this role for the user was created.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        alias="modificationDate",
        description="The date and time this role for the user was last modified.",
    )
    permission_ids: Optional[List[str]] = Field(
        None,
        alias="permissionIds",
        description="The permission IDs associated with this role.",
    )


class UpdateRolesResponse(ResponseModel):
    """
    A model representing the response to updating a user's role.

    **Fields**:

    * **processed_replacement_role_ids**: `List[str]` - The role IDs processed.
    * **newly_assigned_roles_ids**: `List[str]` - The role IDs newly assigned to the user.
    * **unassigned_roles_ids**: `List[str]` - The role IDs unassigned from the user.
    * **ignored_roles_ids**: `List[str]` - The role IDs ignored.
    """

    processed_replacement_role_ids: Optional[List[str]] = Field(
        None,
        alias="processedReplacementRoleIds",
        description="The role IDs processed.",
    )
    newly_assigned_roles_ids: Optional[List[str]] = Field(
        None,
        alias="newlyAssignedRolesIds",
        description="The role IDs newly assigned to the user.",
    )
    unassigned_roles_ids: Optional[List[str]] = Field(
        None,
        alias="unassignedRolesIds",
        description="The role IDs unassigned from the user.",
    )
    ignored_roles_ids: Optional[List[str]] = Field(
        None,
        alias="ignoredRolesIds",
        description="The role IDs ignored.",
    )


class Permission(Model):
    """
    A model representing a role permission.

    **Fields**:

    * **permission**: `str` - Permission ID.
    * **description**: `str` - Brief description of the permission.
    """

    permission: Optional[str] = Field(None, description="Permission ID.")
    description: Optional[str] = Field(None, description="Permission description.")


class Role(ResponseModel):
    """
    A model representing a role.

    **Fields**:

    * **role_id**: `str` - A role ID.
    * **role_name**: `str` - A role name.
    * **modification_date**: `str` - The date and time this role for the user was last modified.
    * **creation_date**: `str` - The date and time this role for the user was created.
    * **permission_ids**: `str` - The permission IDs associated with this role.
    """

    role_id: Optional[str] = Field(None, alias="roleId", description="A role ID.")
    role_name: Optional[str] = Field(None, alias="roleName", description="A role name.")
    creation_date: Optional[datetime] = Field(
        None,
        alias="creationDate",
        description="The date and time this role for the user was created.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        alias="modificationDate",
        description="The date and time this role for the user was last modified.",
    )
    permissions: Optional[List[Permission]] = Field(
        None,
        description="The permission IDs associated with this role.",
    )
