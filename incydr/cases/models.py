from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from incydr.core.models import ResponseModel


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
    number: int = Field(allow_mutation=False)
    status: Status
    assignee: Optional[str]
    assignee_username: Optional[str] = Field(alias="assigneeUsername")
    created_by_user_id: Optional[str] = Field(allow_mutation=False, alias="createdByUserID")
    created_by_username: Optional[str] = Field(allow_mutation=False, alias="createdByUsername")
    description: Optional[str]
    findings: Optional[str]
    last_modified_by_user_id: Optional[str] = Field(allow_mutation=False, alias="lastModifiedByUserId")
    last_modified_by_username: Optional[str] = Field(allow_mutation=False, alias="lastModifiedByUsername")
    subject: Optional[str]
    subject_username: Optional[str] = Field(alias="subjectUsername")
    updated_at: Optional[datetime] = Field(allow_mutation=False, alias="updatedAt")
    created_at: datetime = Field(allow_mutation=False, alias="createdAt")

    class Config:
        validate_assignment = True


class CasesPage(ResponseModel):
    cases: List[Case]
    total_count: int = Field(alias="totalCount")


class QueryCasesRequest(BaseModel):
    assignee: Optional[str] = None
    createdAt: Optional[tuple[Optional[datetime], Optional[datetime]]]
    isAssigned: Optional[bool]
    lastModifiedBy: Optional[str]
    name: Optional[str] = None
    pgNum: Optional[int]
    pgSize: Optional[int]
    srtDir: SortDirection = Field(lias="srtDir", default=SortDirection.ASC)
    srtKey: SortKeys = Field(alias="srtKey",default=SortKeys.NUMBER)
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
