from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.sessions import ContentInspectionStatuses
from _incydr_sdk.enums.sessions import SessionStates
from _incydr_sdk.enums.sessions import SortKeys


class ContentInspectionEvent(Model):
    event_id: str = Field(alias="eventId")
    pii_type: str = Field(alias="piiType")
    status: str


class ContentInspectionResult(Model):
    event_results: List[ContentInspectionEvent] = Field(
        alias="eventResults",
        description="List of all content inspection events that have occurred.",
    )
    status: str


class Note(Model):
    content: str
    id: str
    source_timestamp: int = Field(alias="sourceTimestamp")
    user_id: str = Field(alias="userId")


class RiskIndicator(Model):
    event_count: int = Field(alias="eventCount")
    id: str
    name: str
    weight: int


class Score(Model):
    score: int
    severity: int
    source_timestamp: int = Field(alias="sourceTimestamp")


class State(Model):
    source_timestamp: int = Field(alias="sourceTimestamp")
    state: SessionStates
    user_id: str = Field(alias="userId", description="A User ID. (Deprecated)")


class Alert(Model):
    """ """

    alert_id: str = Field(alias="alertId")
    lesson_id: str = Field(alias="lessonId")
    rule_id: str = Field(alias="ruleId")


class SessionsCriteriaRequest(BaseModel):
    actor_id: Optional[str]
    on_or_after: Optional[int]
    before: Optional[int]
    has_alerts: Optional[str]
    risk_indicators: Optional[List[str]]
    state: Optional[List[SessionStates]]
    severity: Optional[List[int]]
    rule_id: Optional[List[str]]
    watchlist_id: Optional[List[str]]
    content_inspection_status: Optional[ContentInspectionStatuses]

    class Config:
        use_enum_values = True


class SessionsQueryRequest(SessionsCriteriaRequest):
    order_by: Optional[SortKeys]
    sort_direction: Optional[SortDirection]
    page_number: Optional[int]
    page_size: Optional[int]


class SessionsChangeStateRequest(BaseModel):
    ids: List[str]
    newState: str
