from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import constr
from pydantic import Field

from _incydr_sdk.enums.alerts import AlertState


class UpdateAlertStateRequest(BaseModel):
    tenant_id: constr(max_length=40) = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    alert_ids: List[str] = Field(
        ...,
        alias="alertIds",
        description="The unique identifiers representing the alerts you want to act upon.",
        example=["ExampleAlertId1", "ExampleAlertId2"],
        max_length=100,
    )
    state: AlertState = Field(
        ..., description="The state to update the given alerts to."
    )
    note: Optional[constr(max_length=2000)] = Field(
        None,
        description="An optional note to attach to the alert",
        example="This is an example note.",
    )


class AlertDetailsRequest(BaseModel):
    alert_ids: List[str] = Field(
        ...,
        alias="alertIds",
        description="The unique identifiers representing the alerts you want to act upon.",
        example=["ExampleAlertId1", "ExampleAlertId2"],
        max_length=100,
    )


class AddNoteRequest(BaseModel):
    tenant_id: constr(max_length=40) = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    alert_id: constr(max_length=40) = Field(
        ...,
        alias="alertId",
        description="The unique identifier representing the alert you want to act upon.",
        example="ExampleAlertId",
    )
    note: constr(max_length=2000) = Field(
        ...,
        description="The note to attach to the alert.",
        example="This is an example note.",
    )
