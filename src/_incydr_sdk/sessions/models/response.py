from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.file_events.models.response import FileEventsPage
from _incydr_sdk.sessions.models.models import Alert
from _incydr_sdk.sessions.models.models import ContentInspectionResult
from _incydr_sdk.sessions.models.models import Note
from _incydr_sdk.sessions.models.models import RiskIndicator
from _incydr_sdk.sessions.models.models import Score
from _incydr_sdk.sessions.models.models import State


class Session(ResponseModel):
    """
    A model representing a session summary.

    **Fields**:

    * **actor_id**: `str` The ID of the actor that generated the session.
    * **begin_time**: `datetime` The date and time when this session began.
    * **content_inspection_results**: `List[ContentInspectionResult]` The results of content inspection.
    * **context_summary**: `str` An English summary of the contextual aspects of this session is any were identified.
    * **critical_events**: `int` The number of events in the session with a critical risk severity.
    * **end_time**: `datetime` The date and time when this session ended.
    * **exfiltration_summary**: `str` An English summary of the exfiltration (if any) in this session.
    * **first_observed**: `datetime` The date and time at which this session was first observed.
    * **high_events**: `int` The number of events in the session with a high risk severity.
    * **last_updated**: `datetime` The date and time at which this session was last updated.
    * **low_events**: `int` The number of events in the session with a low risk severity
    * **moderate_events**: `int` The number of events in the session with a moderate risk severity.
    * **no_risk_events**: `int` The number of events in the session with a no risk severity.
    * **notes**: `str` The set of notes associated with this session.
    * **risk_indicators**: `List[str]` The list of risk indicator/weight combinations observed in this session.
    * **scores**: `str` The history of all score assignments for this session.
    * **session_id**: `str` The session ID.
    * **states**: `str` The history of states this session has been in.
    * **tenant_id**: `str` The tenant ID.
    * **triggered_alerts**: `str` The list of all alerts that were triggered by activity in this session.
    """

    actor_id: Optional[str] = Field(alias="actorId")
    begin_time: Optional[int] = Field(alias="beginTime")
    content_inspection_results: Optional[ContentInspectionResult] = Field(
        alias="contentInspectionResults"
    )
    context_summary: Optional[str] = Field(alias="contextSummary")
    critical_events: Optional[int] = Field(alias="criticalEvents")
    end_time: Optional[int] = Field(alias="endTime")
    exfiltration_summary: Optional[str] = Field(alias="exfiltrationSummary")
    first_observed: Optional[int] = Field(alias="firstObserved")
    high_events: Optional[int] = Field(alias="highEvents")
    last_updated: Optional[int] = Field(alias="lastUpdated")
    low_events: Optional[int] = Field(alias="lowEvents")
    moderate_events: Optional[int] = Field(alias="moderateEvents")
    no_risk_events: Optional[int] = Field(alias="noRiskEvents")
    notes: Optional[List[Note]]
    risk_indicators: Optional[List[RiskIndicator]] = Field(alias="riskIndicators")
    scores: Optional[List[Score]]
    session_id: Optional[str] = Field(alias="sessionId")
    states: Optional[List[State]]
    tenant_id: Optional[str] = Field(alias="tenantId")
    triggered_alerts: Optional[List[Alert]] = Field(alias="triggeredAlerts")
    user_id: Optional[str] = Field(None, alias="userId")


class SessionsPage(ResponseModel):
    """
    A model representing a page of sessions.

    **Fields**:

    * **items**: `List[Session]` The list of sessions returned by the query.
    * **total_count**: `int` The total count of sessions returned by the query.
    """

    items: List[Session] = Field(None)
    total_count: int = Field(None, alias="totalCount")


class SessionEvents(ResponseModel):
    """
    The wrapped file event search response returned when retrieving the events attached to a session.
    """

    query_result: FileEventsPage = Field(alias="queryResult")
