from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class CreatorUser(ResponseModel):
    user_id: Optional[str] = Field(
        None,
        alias="userId",
    )
    username: Optional[str] = Field(
        None,
    )


class CreatorPrincipal(ResponseModel):
    type: Optional[str] = Field(
        None,
    )
    principal_id: Optional[str] = Field(
        None,
        alias="principalId",
    )
    display_name: Optional[str] = Field(
        None,
        alias="displayName",
    )


class Matter(ResponseModel):
    """A model representing a legal hold matter.

    **Fields**:

    * **matter_id**: `str`
    * **name**: `str`
    * **description**: `str`
    * **notes**: `str`
    * **active**: `bool`
    * **creation_date**: `datetime`
    * **policy_id**: `str`
    * **creator**: `CreatorUser`
    * **creator_principal**: `CreatorPrincipal`
    """

    matter_id: Optional[str] = Field(
        None,
        alias="matterId",
    )
    name: Optional[str] = Field(
        None,
    )
    description: Optional[str] = Field(
        None,
    )
    notes: Optional[str] = Field(
        None,
    )
    active: Optional[bool] = Field(
        None,
    )
    creation_date: Optional[datetime] = Field(
        None,
        alias="creationDate",
    )
    policy_id: Optional[str] = Field(
        None,
        alias="policyId",
    )
    creator: Optional[CreatorUser] = Field(
        None,
    )
    creator_principal: Optional[CreatorPrincipal] = Field(
        None,
        alias="creatorPrincipal",
    )


class MattersPage(ResponseModel):
    matters: Optional[List[Matter]] = Field(
        None,
    )


class CustodianMatter(ResponseModel):
    membership_active: Optional[bool] = Field(
        None,
        alias="membershipActive",
    )
    membership_creation_date: Optional[datetime] = Field(
        None,
        alias="membershipCreationDate",
    )
    matter_id: Optional[str] = Field(
        None,
        alias="matterId",
    )
    name: Optional[str] = Field(
        None,
    )


class CustodianMattersPage(ResponseModel):
    matters: Optional[List[CustodianMatter]] = Field(
        None,
    )


class Custodian(ResponseModel):
    membership_active: Optional[bool] = Field(
        None,
        alias="membershipActive",
    )
    membership_creation_date: Optional[datetime] = Field(
        None,
        alias="membershipCreationDate",
    )
    user_id: Optional[str] = Field(
        None,
        alias="userId",
    )
    name: Optional[str] = Field(
        None,
    )
    email: Optional[str] = Field(
        None,
    )


class CustodiansPage(ResponseModel):
    custodians: Optional[List[Custodian]] = Field(
        None,
    )


class AddCustodianResponseMatter(ResponseModel):
    matter_id: Optional[str] = Field(None, alias="matterId")
    name: Optional[str] = Field(
        None,
    )


class AddCustodianResponseCustodian(ResponseModel):
    user_id: Optional[str] = Field(None, alias="userId")
    username: Optional[str] = Field(
        None,
    )
    email: Optional[str] = Field(
        None,
    )


class AddCustodianResponse(ResponseModel):
    membership_active: Optional[bool] = Field(None, alias="membershipActive")
    membership_creation_date: Optional[datetime] = Field(
        None, alias="membershipCreationDate"
    )
    matter: Optional[AddCustodianResponseMatter] = Field(
        None,
    )
    custodian: Optional[AddCustodianResponseCustodian] = Field(
        None,
    )


class LegalHoldPolicy(ResponseModel):
    policy_id: Optional[str] = Field(None, alias="policyId")
    name: Optional[str] = Field(None)
    creation_date: Optional[datetime] = Field(None, alias="creationDate")
    modification_date: Optional[datetime] = Field(None, alias="modificationDate")
    creator_user: Optional[CreatorUser] = Field(None, alias="creatorUser")
    creator_principal: Optional[CreatorPrincipal] = Field(
        None,
        alias="creatorPrincipal",
    )


class LegalHoldPolicyPage(ResponseModel):
    policies: Optional[List[LegalHoldPolicy]]
