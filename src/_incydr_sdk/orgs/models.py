from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field
from pydantic import validator

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.queries.utils import parse_str_to_dt


# V1 org endpoints are inconsistent in their date formatting, so we need
# to use a parse method here.
def parse_datetime_validator(cls, value):
    if value:
        return parse_str_to_dt(value)
    else:
        return None


class Org(ResponseModel):
    """
    A model representing an organization.

    **Fields**:

    * **org_guid**: `str` - The globally unique ID of this org.
    * **org_name**: `str` - The name of this org.
    * **org_ext_ref**: `str` - Optional external reference information, such as a serial number, asset tag, employee ID, or help desk issue ID.
    * **notes**: `str` - The notes for this org. Intended for optional additional descriptive information.
    * **parent_org_guid**: `str` - The globally unique ID of the parent org.
    * **active**: `bool` - Whether or not the org is currently active.
    * **creation_date**: `datetime` - Date and time this org was created.
    * **modification_date**: `datetime` - Date and time this org was last modified.
    * **deactivation_date**: `datetime` - Date and time this org was deactivated. Blank if org is active.
    * **registration_key**: `str` - The registration key for the org.
    * **user_count**: `int` - The count of users within this org.
    * **computer_count**: `int` - The count of computers within this org.
    * **org_count**: `int` - The count of child orgs for this org.
    """

    org_guid: Optional[str] = Field(
        None,
        alias="orgGuid",
        description="The globally unique ID of this org.",
    )
    org_name: Optional[str] = Field(
        None,
        alias="orgName",
        description="The name of this org.",
    )
    org_ext_ref: Optional[str] = Field(
        None,
        alias="orgExtRef",
        description="Optional external reference information, such as a serial number, asset tag, employee ID, or help desk issue ID.",
    )
    notes: Optional[str] = Field(
        None,
        alias="notes",
        description="The notes for this org. Intended for optional additional descriptive information.",
    )
    parent_org_guid: Optional[str] = Field(
        None,
        alias="parentOrgGuid",
        description="The globally unique ID of the parent org.",
    )
    active: Optional[bool] = Field(
        None,
        description="Whether or not the org is currently active.",
    )
    creation_date: Optional[datetime] = Field(
        None,
        alias="creationDate",
        description="Date and time this org was created.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        alias="modificationDate",
        description="Date and time this org was last modified.",
    )
    deactivation_date: Optional[datetime] = Field(
        None,
        alias="deactivationDate",
        description="Date and time this org was deactivated. Blank if org is active.",
    )
    registration_key: Optional[str] = Field(
        None,
        alias="registrationKey",
        description="The registration key for the org.",
    )
    user_count: Optional[int] = Field(
        None,
        alias="userCount",
        description="The count of users within this org.",
    )
    computer_count: Optional[int] = Field(
        None,
        alias="computerCount",
        description="The count of computers within this org.",
    )
    org_count: Optional[int] = Field(
        None,
        alias="orgCount",
        description="The count of child orgs for this org.",
    )
    _creation_date = validator("creation_date", allow_reuse=True, pre=True)(
        parse_datetime_validator
    )
    _modification_date = validator("modification_date", allow_reuse=True, pre=True)(
        parse_datetime_validator
    )
    _deactivation_date = validator("deactivation_date", allow_reuse=True, pre=True)(
        parse_datetime_validator
    )


class OrgsList(ResponseModel):
    """
    A model representing a list of `Org` objects.

    **Fields**:

    * **orgs**: `List[Org]` - The list of orgs retrieved from the query.
    * **total_count**: `int` - Total count of orgs found by query.
    """

    orgs: Optional[List[Org]] = Field(None, description="A list of orgs")
    total_count: Optional[int] = Field(
        None, alias="totalCount", description="The total number of orgs"
    )
