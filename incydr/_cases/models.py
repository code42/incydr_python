from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from incydr._core.models import ResponseModel


class Status(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortKeys(str, Enum):
    NAME = "name"
    NUMBER = "number"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    STATUS = "status"
    ASSIGNEE_USERNAME = "assigneeUsername"
    SUBJECT_USERNAME = "subjectUsername"


class Case(ResponseModel):
    name: str
    status: Status
    assignee: Optional[str]
    subject: Optional[str]
    description: Optional[str]
    findings: Optional[str]
    number: int = Field(allow_mutation=False)
    last_modified_by_user_id: Optional[str] = Field(
        allow_mutation=False, alias="lastModifiedByUserId"
    )
    last_modified_by_username: Optional[str] = Field(
        allow_mutation=False, alias="lastModifiedByUsername"
    )
    assignee_username: Optional[str] = Field(
        allow_mutation=False, alias="assigneeUsername"
    )
    created_by_user_id: Optional[str] = Field(
        allow_mutation=False, alias="createdByUserID"
    )
    created_by_username: Optional[str] = Field(
        allow_mutation=False, alias="createdByUsername"
    )
    subject_username: Optional[str] = Field(alias="subjectUsername")
    updated_at: Optional[datetime] = Field(allow_mutation=False, alias="updatedAt")
    created_at: datetime = Field(allow_mutation=False, alias="createdAt")

    class Config:
        validate_assignment = True


class CasesPage(ResponseModel):
    cases: List[Case]
    total_count: int = Field(alias="totalCount")


class QueryCasesRequest(BaseModel):
    """Validator for GET requests to /v1/cases"""

    assignee: Optional[str] = Field(
        description="The userUid of the user the case is assigned to.", default=None
    )
    created_at: Optional[tuple[Optional[datetime], Optional[datetime]]] = Field(
        alias="createdAt",
        description="Retrieve cases created within the provided date range (represented as a tuple of datetimes).",
    )
    is_assigned: Optional[bool] = Field(alias="isAssigned")
    last_modified_by: Optional[str] = Field(
        alias="lastModifiedBy",
        description="Retrieve cases last modified by the provided userID.",
    )
    name: Optional[str] = None
    page_num: Optional[int] = Field(alias="pgNum")
    page_size: Optional[int] = Field(alias="pgSize")
    sort_dir: SortDirection = Field(alias="srtDir", default=SortDirection.ASC)
    sort_key: SortKeys = Field(alias="srtKey", default=SortKeys.NUMBER)
    status: Optional[Status] = None


class CreateCaseRequest(BaseModel):
    name: str = Field(max_length=50)
    assignee: Optional[str]
    description: Optional[str] = Field(max_length=250)
    findings: Optional[str] = Field(max_length=30_000)
    subject: Optional[str]


class UpdateCaseRequest(BaseModel):
    number: Optional[int] = Field(description="The case identifier.", doc_hide=True)
    name: Optional[str] = Field(description="The name of the case.", max_length=50)
    assignee: Optional[str]
    description: Optional[str] = Field(max_length=250)
    findings: Optional[str] = Field(max_length=30_000)
    subject: Optional[str]
    status: Optional[Status]
