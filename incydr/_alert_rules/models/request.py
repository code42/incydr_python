from typing import List

from pydantic import BaseModel
from pydantic import constr
from pydantic import Field

from incydr._core.models import ResponseModel


class UserRequest(BaseModel):
    userIdFromAuthority: str = Field(
        None, description="User ID from authority.", example="userIdFromAuthority"
    )
    userAliasList: List[str] = Field(
        None,
        description="List of user aliases corresponding to the user ID from the authority.",
        example=["userAlias1", "userAlias2"],
    )


class UpdateUserIdsRequest(BaseModel):
    tenantId: constr(max_length=100) = Field(
        None,
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    ruleId: constr(max_length=40) = Field(
        None,
        description="The unique identifier representing the rule you want to act upon.",
        example="ExampleRuleId",
    )
    userIdList: List[str] = Field(
        None,
        description="List of user ids (from authority) to remove from the rule.  Will remove all associated aliases",
        example=["userIdFromAuthority"],
    )


class GetRulesRequest(BaseModel):
    tenantId: constr(max_length=100) = Field(
        None,
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    ruleIds: List[str] = Field(
        None,
        description="The unique identifiers representing the rules you want to act upon.",
        example=["ExampleRuleId1", "ExampleRuleId2"],
        max_length=100,
    )


class UpdateRulesRequest(BaseModel):
    tenantId: constr(max_length=100) = Field(
        None,
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    ruleIds: List[str] = Field(
        None,
        description="The unique identifiers representing the rules you want to act upon.",
        example=["ExampleRuleId1", "ExampleRuleId2"],
        max_length=100,
    )
    isEnabled: bool = Field(
        None,
        description="What to set the rule's enabled activity to.  Either TRUE or FALSE.",
        example="TRUE",
    )


class UpdateUsersRequest(ResponseModel):
    tenantId: constr(max_length=100) = Field(
        None,
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    ruleId: constr(max_length=40) = Field(
        None,
        description="The unique identifier representing the rule you want to act upon.",
        example="ExampleRuleId",
    )
    userList: List[UserRequest] = Field(None, description="List of users.")
