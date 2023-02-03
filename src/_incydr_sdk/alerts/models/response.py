from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.alerts.models.alert import AlertDetails  # noqa
from _incydr_sdk.alerts.models.alert import AlertSummary
from _incydr_sdk.alerts.models.enums import ProblemType
from _incydr_sdk.core.models import ResponseModel


class QueryProblem(BaseModel):
    bad_filter: Optional[str] = Field(
        None, alias="badFilter", description="The filter that caused the issue."
    )
    type: ProblemType = Field(..., description="The type of query problem.")


class AlertQueryPage(ResponseModel):
    """
    A model representing a page of `AlertSummary` objects resulting from an alert search query.

    **Fields**:

    * **alerts**: `List[AlertSummary]` List of alerts that found by query.
    * **total_count**: `int` The count of alerts found.
    * **problems**: `List[QueryProblem]` Potential issues that were hit while trying to run the query.
    """

    type: str = Field(alias="type$")
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
