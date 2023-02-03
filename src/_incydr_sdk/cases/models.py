from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from rich.markdown import Markdown

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.cases import CaseStatus
from _incydr_sdk.enums.cases import FileAvailability
from _incydr_sdk.enums.cases import SortKeys
from _incydr_sdk.utils import list_as_panel
from _incydr_sdk.utils import model_as_card


class Case(ResponseModel, validate_assignment=True):
    """A model representing an Incydr Case.

    **Fields**:

    * **number**: `int` Unique numeric identifier for the case.
    * **name**: `str` Unique name given to the case.
    * **created_at**: `datetime` Time at which the case was created. json_alias=`createdAt`
    * **updated_at**: `datetime | None` Time at which the case was last updated. json_alias=`updatedAt`
    * **subject**: `str | None` The user UID of the subject being investigated in this case.
    * **subject_username**: `str | None` The username of the subject being investigated in this case. json_alias=`subjectUsername`
    * **status**: `CaseStatus` Indicates the status of the case. OPEN: The case is active and all aspects of the case are editable. CLOSED: The case is resolved. Closed cases cannot be re-opened or modified. Case data for closed cases is retained indefinitely.
    * **assignee**: `str | None` The user ID of the administrator assigned to investigate the case.
    * **assignee_username**: `str | None` The username of the administrator assigned to investigate the case. json_alias=`assigneeUsername`
    * **created_by_user_id**: `str | None` User UID of the user who created the case. json_alias=`createdByUserUid`
    * **created_by_username**: `str | None` Username of the user who created the case. json_alias=`createdByUsername`
    * **last_modified_by_user_id**: `str | None` User UID of the user who last modified the case. json_alias=`lastModifiedByUserUid`
    * **last_modified_by_username**: `str | None` Username of the user who last modified the case. json_alias=`lastModifiedByUsername`
    * **archival_time**: `datetime` Time at which the case will be archived.
    """

    number: Optional[int] = Field(
        allow_mutation=False, description="The identifier of the case."
    )
    name: Optional[str]
    created_at: Optional[datetime] = Field(allow_mutation=False, alias="createdAt")
    updated_at: Optional[datetime] = Field(allow_mutation=False, alias="updatedAt")
    subject: Optional[str]
    subject_username: Optional[str] = Field(alias="subjectUsername")
    status: CaseStatus
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
    archival_time: Optional[datetime] = Field(
        allow_mutation=False, alias="archivalTime"
    )


class CaseDetail(Case):
    """A model representing the full details of Incydr Case.

    **Fields**:

    **All the same fields as Case model, plus**:

    * **description**: `str | None` Brief description providing context for a case.
    * **findings**: `str | None` Markdown formatted text summarizing the findings for a case.
    """

    description: Optional[str]
    findings: Optional[str] = Field(table=lambda f: f if f is None else Markdown(f))


class CasesPage(ResponseModel):
    """
    A model representing a page of `Case` objects.

    **Fields**:

    * **cases**: `List[Case]` The list of `n` number of cases retrieved from the query, where `n=page_size`.
    * **total_count**: `int` Total count of cases found by the query.
    """

    cases: List[Case]
    total_count: int = Field(alias="totalCount")


class QueryCasesRequest(Model):
    assignee: Optional[str]
    createdAt: Optional[str]
    isAssigned: Optional[bool]
    lastModifiedBy: Optional[str]
    name: Optional[str]
    pgNum: Optional[int] = 1
    pgSize: Optional[int] = 100
    srtDir: SortDirection = SortDirection.ASC
    srtKey: SortKeys = SortKeys.NUMBER
    status: Optional[CaseStatus]


class CreateCaseRequest(Model):
    name: str = Field(max_length=50)
    assignee: Optional[str]
    description: Optional[str] = Field(max_length=250)
    findings: Optional[str] = Field(max_length=30_000)
    subject: Optional[str]


class UpdateCaseRequest(Model, extra=Extra.ignore):
    name: Optional[str] = Field(description="The name of the case.", max_length=50)
    assignee: Optional[str]
    description: Optional[str] = Field(max_length=250)
    findings: Optional[str] = Field(max_length=30_000)
    subject: Optional[str]
    status: Optional[CaseStatus]


class RiskIndicator(BaseModel):
    name: str
    weight: int


class FileEvent(Model):
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
        table=lambda _list: list_as_panel([model_as_card(m) for m in _list])
        if len(_list)
        else "None",
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


class CaseFileEvents(ResponseModel):
    """A model representing file events associated with a case.

    **Fields**:

    * **events**: `List[FileEvent]` - List of events in the response..
    * **total_count**: `int` - Total number of events associated with the case.
    """

    events: Optional[List[FileEvent]] = Field(
        None, description="List of events in the response."
    )
    total_count: Optional[int] = Field(
        None,
        alias="totalCount",
        description="Total number of events associated with the case.",
        example=42,
    )
