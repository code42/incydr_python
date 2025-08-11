from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import StringConstraints
from typing_extensions import Annotated

from _incydr_sdk.enums.alerts import AlertState


class UpdateAlertStateRequest(BaseModel):
    tenant_id: Annotated[str, StringConstraints(max_length=40)] = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        examples=["MyExampleTenant"],
    )
    alert_ids: List[str] = Field(
        ...,
        alias="alertIds",
        description="The unique identifiers representing the alerts you want to act upon.",
        examples=[["ExampleAlertId1", "ExampleAlertId2"]],
        max_length=100,
    )
    state: AlertState = Field(
        ..., description="The state to update the given alerts to."
    )
    note: Optional[Annotated[str, StringConstraints(max_length=2000)]] = Field(
        None,
        description="An optional note to attach to the alert",
        examples=["This is an example note."],
    )


class AlertDetailsRequest(BaseModel):
    alert_ids: List[str] = Field(
        ...,
        alias="alertIds",
        description="The unique identifiers representing the alerts you want to act upon.",
        examples=[["ExampleAlertId1", "ExampleAlertId2"]],
        max_length=100,
    )


class AddNoteRequest(BaseModel):
    tenant_id: Annotated[str, StringConstraints(max_length=40)] = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        examples=["MyExampleTenant"],
    )
    alert_id: Annotated[str, StringConstraints(max_length=40)] = Field(
        ...,
        alias="alertId",
        description="The unique identifier representing the alert you want to act upon.",
        examples=["ExampleAlertId"],
    )
    note: Annotated[str, StringConstraints(max_length=2000)] = Field(
        ...,
        description="The note to attach to the alert.",
        examples=["This is an example note."],
    )
