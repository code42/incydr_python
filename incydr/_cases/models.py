from datetime import datetime
from enum import Enum
from typing import Optional, List, Tuple

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
    number: int = Field(allow_mutation=False)
    name: str
    created_at: datetime = Field(allow_mutation=False, alias="createdAt")
    updated_at: Optional[datetime] = Field(allow_mutation=False, alias="updatedAt")
    description: Optional[str]
    findings: Optional[str]
    subject: Optional[str]
    subject_username: Optional[str] = Field(alias="subjectUsername")
    status: Status
    assignee: Optional[str]
    assignee_username: Optional[str] = Field(
        allow_mutation=False, alias="assigneeUsername"
    )
    created_by_user_id: Optional[str] = Field(
        allow_mutation=False, alias="createdByUserUid"
    )
    created_by_username: Optional[str] = Field(
        allow_mutation=False, alias="createdByUsername"
    )
    last_modified_by_user_id: Optional[str] = Field(
        allow_mutation=False, alias="lastModifiedByUserUid"
    )
    last_modified_by_username: Optional[str] = Field(
        allow_mutation=False, alias="lastModifiedByUsername"
    )

    class Config:
        validate_assignment = True


class CasesPage(ResponseModel):
    cases: List[Case]
    total_count: int = Field(alias="totalCount")


class QueryCasesRequest(BaseModel):
    assignee: Optional[str]
    createdAt: Optional[Tuple[Optional[datetime], Optional[datetime]]]
    isAssigned: Optional[bool]
    lastModifiedBy: Optional[str]
    name: Optional[str]
    pgNum: Optional[int] = 1
    pgSize: Optional[int] = 100
    srtDir: SortDirection = SortDirection.ASC
    srtKey: SortKeys = SortKeys.NUMBER
    status: Optional[Status]


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


class FileAvailability(Enum):
    error = "ERROR"
    exact_file_available = "EXACT_FILE_AVAILABLE"
    no_file_available = "NO_FILE_AVAILABLE"
    pending = "PENDING"
    recent_file_available = "RECENT_FILE_AVAILABLE"


class RiskIndicator(BaseModel):
    name: str
    weight: int


class FileEvent(BaseModel):
    event_id: Optional[str] = Field(
        None,
        alias="eventId",
        description="The unique identifier for the event.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    event_timestamp: Optional[datetime] = Field(
        None,
        alias="eventTimestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the deviceâ€™s system clock and reported in Coordinated Universal Time (UTC).",
        example="2020-12-23T14:24:44.593Z",
    )
    exposure: Optional[List[str]] = Field(
        None,
        description="Lists indicators that the data may be exposed.",
        example=["OutsideTrustedDomains", "IsPublic"],
    )
    file_availability: Optional[FileAvailability] = Field(
        None,
        alias="fileAvailability",
        description="The download availability status of the file associated with the event.",
        example="EXACT_FILE_AVAILABLE",
    )
    file_name: Optional[str] = Field(
        None,
        alias="fileName",
        description="The name of the file, including the file extension.",
        example="example.docx",
    )
    file_path: Optional[str] = Field(
        None,
        alias="filePath",
        description="The file location on the user's device; a path forward or backslash should be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
        example="/Users/casey/Documents/",
    )
    risk_indicators: Optional[List[RiskIndicator]] = Field(
        None,
        alias="riskIndicators",
        description="List of risk indicators identified for this event. If more than one risk indicator applies to this event, the sum of all indicators determines the total risk score.",
    )
    risk_score: Optional[int] = Field(
        None,
        alias="riskScore",
        description="Sum of the weights for each risk indicator. This score is used to determine the overall risk severity of the event.",
        example=12,
    )
    risk_severity: Optional[str] = Field(
        None,
        alias="riskSeverity",
        description="The general risk assessment of the event, based on the numeric score.",
        example="CRITICAL",
    )


class CaseFileEventsResponse(ResponseModel):
    events: Optional[List[FileEvent]] = Field(
        None, description="List of events in the response."
    )
    total_count: Optional[int] = Field(
        None,
        alias="totalCount",
        description="Total number of events associated with the case.",
        example=42,
    )


class EventProblemResponse(BaseModel):
    problem: Optional[str] = Field(
        None, description="The type of problem that occured."
    )
