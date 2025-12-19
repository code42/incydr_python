from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.sessions import ContentInspectionStatuses
from _incydr_sdk.enums.sessions import SessionStates
from _incydr_sdk.enums.sessions import SortKeys


class ContentInspectionEvent(Model):
    event_id: Optional[str] = Field(None, alias="eventId")
    pii_type: Optional[List[str]] = Field(None, alias="piiType")
    status: Optional[str] = None


class ContentInspectionResult(Model):
    detected_on_alerts: List[str] = Field(
        None,
        alias="detectedOnAlerts",
        description="A list of content categories or types found on events which triggered alerts.",
    )


class Note(Model):
    content: Optional[str]
    id: Optional[str]
    source_timestamp: Optional[int] = Field(alias="sourceTimestamp")
    user_id: Optional[str] = Field(alias="userId")


class RiskIndicator(Model):
    event_count: Optional[int] = Field(None, alias="eventCount")
    id: Optional[str] = None
    name: Optional[str] = None
    weight: Optional[int] = None


class Score(Model):
    score: Optional[int] = None
    severity: Optional[int] = None
    source_timestamp: Optional[int] = Field(alias="sourceTimestamp")


class State(Model):
    source_timestamp: Optional[int] = Field(None, alias="sourceTimestamp")
    state: SessionStates = Field(None, description="Deprecated. Use state_v2 instead.")
    state_v2: str = Field(
        None,
        alias="stateV2",
        description="The state assigned to the session. The value is an item from the SessionStates enum. Clients should be tolerant of additional values that may be added in the future.",
    )
    user_id: Optional[str] = Field(
        None, alias="userId", description="A User ID. (Deprecated)"
    )


class Alert(Model):
    """ """

    alert_id: Optional[str] = Field(alias="alertId")
    lesson_id: Optional[str] = Field(alias="lessonId")
    rule_id: Optional[str] = Field(alias="ruleId")


class SessionsCriteriaRequest(BaseModel):
    actor_id: Optional[str] = None
    on_or_after: Optional[int] = None
    before: Optional[int] = None
    has_alerts: Optional[str] = None
    risk_indicators: Optional[List[str]] = None
    state: Optional[List[SessionStates]] = None
    severity: Optional[List[int]] = None
    rule_id: Optional[List[str]] = None
    watchlist_id: Optional[List[str]] = None
    content_inspection_status: Optional[ContentInspectionStatuses] = None
    model_config = ConfigDict(use_enum_values=True)


class SessionsQueryRequest(SessionsCriteriaRequest):
    order_by: Optional[SortKeys] = None
    sort_direction: Optional[SortDirection] = None
    page_number: Optional[int] = None
    page_size: Optional[int] = None


class SessionsChangeStateRequest(BaseModel):
    ids: Optional[List[str]] = None
    newState: Optional[str] = None
