from datetime import datetime
from typing import Any
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel


class CreateMatterRequest(BaseModel):
    policyId: Optional[str] = Field(
        None,
        description="The unique identifier of the policy involved in the matter.",
    )
    name: Optional[str] = Field(None, description="The name to give to the matter.")
    description: Optional[str] = Field(
        None, description="An optional description to give to the matter."
    )
    notes: Optional[str] = Field(
        None, description="Optional notes to give to the matter"
    )


class ListMattersRequest(BaseModel):
    creatorUserId: str = None
    active: bool = None
    name: str = None
    page: int = 1
    pageSize: int = None


class MatterIdentifier(ResponseModel):
    matter_id: Optional[str] = Field(
        None, description="The unique identifier of the matter.", alias="matterId"
    )
    name: Optional[str] = Field(None, description="The name of the matter.")


class MatterCustodian(ResponseModel):
    user_id: Optional[str] = Field(
        None,
        description="The unique identifier of the Code42 user who is the custodian.",
        alias="userId",
    )
    username: Optional[str] = Field(
        None, description="The Code42 username of the custodian."
    )
    email: Optional[str] = Field(None, description="The email of the custodian.")


class CreatorUser(ResponseModel):
    userId: Optional[str] = Field(
        None, description="A globally unique ID for this user.", alias="userId"
    )
    username: Optional[str] = Field(
        None, description="The name the user uses to log in to Code42."
    )


class CustodianMembership(ResponseModel):
    """
    A model representing a custodian's membership to a matter.

    **Fields**:

    * **membership_active**: `bool` - Whether the custodian's membership is active. True if active, else False.
    * **membership_creation_date**: `str` - The date the custodian was added to the matter.
    * **matter_id**: `str` - Unique ID of the matter.
    * **name**: `str` - Name of the matter.
    """

    membership_active: Optional[bool] = Field(
        None,
        description="Whether the custodian's membership is active.",
        alias="membershipActive",
    )
    membership_creation_date: Optional[str] = Field(
        None,
        description="The data the custodian was added to the matter.",
        alias="membershipCreationDate",
    )
    matter_id: Optional[str] = Field(
        None, description="The unique identifier of the matter.", alias="matterId"
    )
    name: Optional[str] = Field(None, description="The name of the matter.")


class Custodian(ResponseModel):
    """
    A model representing a matter custodian.

    **Fields**:

    * **membership_active**: `bool` - Whether the custodian's membership is active. True if active, else False.
    * **membership_creation_date**: `str` - The date the custodian was added to the matter.
    * **user_id**: `str` - Unique user ID of the custodian.
    * **username**: `str` - Username of the custodian.
    * **email**: `str` - Email of the custodian.
    """

    membership_active: Optional[bool] = Field(
        None,
        description="Whether the custodian's membership is active.",
        alias="membershipActive",
    )
    membership_creation_date: Optional[str] = Field(
        None,
        description="The date the custodian was added to the matter.",
        alias="membershipCreationDate",
    )
    user_id: Optional[str] = Field(
        None,
        description="The unique identifier of the Code42 user who is the custodian.",
        alias="userId",
    )
    username: Optional[str] = Field(
        None, description="The Code42 username of the custodian."
    )
    email: Optional[str] = Field(None, description="The email of the custodian.")


class MatterMembership(ResponseModel):
    """
    A model representing a matter membership.

    **Fields**:

    * **membership_active**: `bool` - Whether the custodian's membership to this matter is active. True if active, else False.
    * **membership_creation_date**: `str` - The date the custodian was added to the matter.
    * **matter**: `MatterIdentifier` - Identifying information for the matter.  Includes the `matter_id` and the `name`.
    * **custodian**: `MatterCustodian` - Identifying information for the custodian.  Includes the `username`, `user_id`, and `email`.
    """

    membership_active: Optional[bool] = Field(
        None,
        description="Whether the custodian's membership is active.",
        alias="membershipActive",
    )
    membership_creation_date: Optional[datetime] = Field(
        None,
        description="The data the custodian was added to the matter.",
        alias="membershipCreationDate",
    )
    matter: Optional[MatterIdentifier] = None
    custodian: Optional[MatterCustodian] = None


class ReactivateMatterResponse(ResponseModel):
    """
    A model representing a reactivated matter response.

    **Fields**:

    * **memberships_changed**: `bool` - Whether the memberships were changed upon reactivation. If true, this means that there were custodians on the matter at the time the matter got deactivated, and when reactivating, these users were placed back in legal hold.
    """

    memberships_changed: Optional[bool] = Field(
        None,
        description="Whether the memberships were changed upon reactivation.\r\nIf true, this means that there were custodians on the matter at the time the matter got deactivated,\r\nand when reactivating, these users were placed back in legal hold.",
        alias="membershipsChanged",
    )


class CustodianMembershipsPage(ResponseModel):
    """
    A model representing a page of `CustodianMembership` objects.

    **Fields**:

    * **matters**: `List[CustodianMembership]` - The list of the `n` number of matter memberships for a custodian, where `n=page_size`.
    """

    matters: Optional[List[CustodianMembership]] = Field(
        None, description="A list of Legal Hold matters for a custodian."
    )


class CustodiansPage(ResponseModel):
    """
    A model representing a page of `Custodian` objects.

    **Fields**:

    * **custodians**: `List[Custodian]` - The list of `n` number of custodians on a matter, where `n=page_size`.
    """

    custodians: Optional[List[Custodian]] = Field(
        None, description="A list of Legal Hold custodians on a matter."
    )


class CreatorPrincipal(ResponseModel):
    type: Optional[str] = None
    principal_id: Optional[str] = Field(None, alias="principalId")
    display_name: Optional[str] = Field(None, alias="displayName")


class Matter(ResponseModel):
    """
    A model representing a legal hold matter.

    **Fields**:

    * **matter_id**: `str` - Unique ID of the matter.
    * **name**: `str` - Name of the matter.
    * **description**: `str` - Description of the matter.
    * **notes**: `str` - Additional notes on the matter
    * **active**: `bool` - True if the matter is currently active.  False if the matters been deactivated.
    * **creation_date**: `datetime` - Date the matter was created.
    * **last_modified_date**: `CreatorUser` - Date the matter was last modified.
    * **creator_object**: `Any` - Information about the user who created the matter.
    * **creator_principal**: `CreatorPrincipal` - Information on the creator principal.
    * **policy_id**: `str` - Unique ID of the policy.
    """

    matter_id: Optional[str] = Field(
        None, description="The unique identifier of the matter.", alias="matterId"
    )
    name: Optional[str] = Field(None, description="The name of the matter.")
    description: Optional[str] = Field(
        None, description="The description of the matter."
    )
    notes: Optional[str] = Field(None, description="Notes about the matter.")
    active: Optional[bool] = Field(
        None, description="Whether the matter is currently active."
    )
    creation_date: Optional[datetime] = Field(
        None,
        description="The date and time the matter was created.",
        alias="creationDate",
    )
    last_modified_date: Optional[datetime] = Field(
        None,
        description="The date and time the matter was last modified.",
        alias="lastModifiedDate",
    )
    creator_object: Optional[Any] = Field(
        None,
        description="Information about the user who created the matter.",
        alias="creatorObject",
    )
    creator_principal: Optional[CreatorPrincipal] = Field(
        None, alias="creatorPrincipal"
    )
    policy_id: Optional[str] = Field(
        None,
        description="The ID of the policy containing the matter.",
        alias="policyId",
    )


class Policy(ResponseModel):
    """
    A model representing a legal hold policy.

    **Fields**:

    * **policy_id**: `str` - Unique ID of the policy.
    * **name**: `str` - Name of the policy.
    * **creator_user**: `CreatorUser` - Information on the user who created the policy.  Includes the `user_id` and the `username`.
    * **creator_principal**: `CreatorPrincipal` - Information on the principal which created the policy.
    * **creation_date**: `datetime` - Date the policy was created.
    * **modification_date**: `datetime` - Date the policy was last modified.
    """

    policy_id: Optional[str] = Field(
        None,
        description="The unique identifier for a legal hold policy.",
        alias="policyId",
    )
    name: Optional[str] = Field(None, description="The name of the legal hold policy.")
    creator_user: Optional[CreatorUser] = Field(None, alias="creatorUser")
    creator_principal: Optional[CreatorPrincipal] = Field(
        None, alias="creatorPrincipal"
    )
    creation_date: Optional[datetime] = Field(
        None, description="The date the policy was created.", alias="creationDate"
    )
    modification_date: Optional[datetime] = Field(
        None,
        description="The date the policy was last modified.",
        alias="modificationDate",
    )


class MattersPage(ResponseModel):
    """
    A model representing a list of `Policy` objects.

    **Fields**:

    * **policies**: `List[Policy]` - The list of `n` number of legal hold matters, where `n=page_size`.
    """

    matters: Optional[List[Matter]] = Field(
        None, description="A list of Legal Hold matters."
    )


class PoliciesList(ResponseModel):
    """
    A model representing a list of `Policy` objects.

    **Fields**:

    * **policies**: `List[Policy]` - The list of legal hold policies.
    """

    policies: Optional[List[Policy]] = Field(
        None, description="A list of Legal Hold policies."
    )
