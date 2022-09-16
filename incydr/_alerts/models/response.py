from __future__ import annotations

from typing import Optional, List

from pydantic import Field, BaseModel

from incydr._alerts.models.alert import AlertDetails
from incydr._alerts.models.alert import AlertSummary
from incydr._alerts.models.enums import ProblemType
from incydr._core.models import ResponseModel


class QueryProblem(BaseModel):
    bad_filter: Optional[str] = Field(
        None, alias="badFilter", description="The filter that caused the issue."
    )
    type: ProblemType = Field(..., description="The type of query problem.")


class AlertQueryResponse(ResponseModel):
    alerts: Optional[List[AlertSummary]] = Field(
        None, description="List of alerts that are returned."
    )
    total_count: int = Field(
        ...,
        alias="totalCount",
        description="The number of alerts that match the given query.",
        example="3",
    )
    problems: Optional[List[QueryProblem]] = Field(
        None,
        description="Potential issues that were hit while trying to run the query.",
        example=[],
    )


class AlertDetailsResponse(ResponseModel):
    alerts: Optional[List[AlertDetails]] = Field(
        None, description="The alerts returned by the details query."
    )
