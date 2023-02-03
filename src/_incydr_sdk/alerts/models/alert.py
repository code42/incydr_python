from __future__ import annotations

import json
from datetime import datetime
from typing import List
from typing import Optional

import rich.box
from pydantic import constr
from pydantic import Field
from pydantic import validator
from rich.markdown import Markdown
from rich.panel import Panel

from _incydr_sdk.core.models import Model


class Observation(Model):
    id: Optional[str] = Field(
        None, description="Id of given observation.", example="uniqueObservationId"
    )
    observed_at: datetime = Field(
        ...,
        alias="observedAt",
        description="Timestamp when the activity was first observed.",
        example="2020-02-19T01:57:45.006683Z",
    )
    last_observed_at: Optional[datetime] = Field(
        None,
        alias="lastObservedAt",
        description="Timestamp when the activity was last observed.",
        example="2020-02-19T01:57:45.006683Z",
    )
    type: Optional[str] = Field(
        None,
        description="The type of observation data recorded.",
        example="FedCloudSharePermissions",
    )
    data: Optional[dict] = Field(
        None,
        description="The JSON formatted observation data rolled into one aggregation.",
        example='{"type$":"OBSERVED_CLOUD_SHARE_ACTIVITY","id":"exampleId","sources":["OneDrive"],"exposureTypes":["PublicLinkShare"],"firstActivityAt":"2020-02-19T01:50:00.0000000Z","lastActivityAt":"2020-02-19T01:55:00.0000000Z","fileCount":2,"totalFileSize":200,"fileCategories":[{"type$":"OBSERVED_FILE_CATEGORY","category":"Document","fileCount":2,"totalFileSize":53,"isSignificant":false}],"outsideTrustedDomainsEmailsCount":0,"outsideTrustedDomainsTotalDomainCount":0,"outsideTrustedDomainsTotalDomainCountTruncated":false}',
        table=lambda data: json.dumps(data, indent=2),
    )

    @validator("data", pre=True)
    def parse_data_json(cls, value):  # noqa
        return json.loads(value) if value else None


class Note(Model):
    id: Optional[str] = Field(
        None, description="Unique id of the note.", example="noteId"
    )
    last_modified_at: datetime = Field(
        ...,
        alias="lastModifiedAt",
        description="Timestamp of when the note was last modified.",
        example="2020-02-19T01:57:45.006683Z",
    )
    last_modified_by: Optional[str] = Field(
        None,
        alias="lastModifiedBy",
        description="User who last modified the note.",
        example="exampleUsername",
    )
    message: Optional[str] = Field(
        None,
        description="The note itself.",
        example="This is a note.",
        table=lambda note: Panel(Markdown(note), width=120, box=rich.box.MINIMAL)
        if note
        else note,
    )


class AuditInfo(Model):
    modified_by: Optional[str] = Field(
        None,
        alias="modifiedBy",
        description="Username of the individual who last modified the rule.",
        example="UserWhoMostRecentlyModifiedTheRule",
    )
    modified_at: datetime = Field(
        ...,
        alias="modifiedAt",
        description="Timestamp of when the rule was last modified.",
        example="2020-02-19T01:57:45.006683Z",
    )


class Watchlist(Model):
    id: Optional[str] = Field(
        None, description="Unique id of this watchlist.", example="guid"
    )
    name: Optional[str] = Field(
        None, description="Name of the watchlist.", example="Development Department"
    )
    type: Optional[str] = Field(
        ..., description="Type of watchlist.", example="DEPARTING_EMPLOYEE"
    )
    is_significant: bool = Field(
        ...,
        alias="isSignificant",
        description="Indicates whether the watchlist was part of the triggering rule's criteria.",
        example="true",
    )


class ObserverRuleMetadata(AuditInfo):
    name: Optional[str] = Field(
        None,
        description="The name of the rule.",
        example="My Removable Media Exfiltration Rule",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the rule.",
        example="Will generate alerts when files moved to USB.",
    )
    severity: Optional[str] = Field(
        None, description="The static severity of the rule (deprecated)."
    )
    is_system: Optional[bool] = Field(
        None,
        alias="isSystem",
        description="Boolean indicating if the rule was created from another Code42 Application.",
        example="FALSE",
    )
    is_enabled: bool = Field(
        ...,
        alias="isEnabled",
        description="Boolean indicating if the rule is enabled to trigger alerts.",
        example="TRUE",
    )
    rule_source: Optional[str] = Field(
        None,
        alias="ruleSource",
        description="The source of the rule.  Will be one of [DepartingEmployee, Alerting, HighRiskEmployee]",
        example="Alerting",
    )


class AlertSummary(Model):
    """
    A model representing an alert summary.

    **Fields**:

    * **tenant_id**: `str` The unique identifier representing the tenant.
    * **type**: `RuleType` Rule type that generated the alert.
    * **id**: `str` The unique id of the alert.
    * **created_at**: `datetime` The timestamp when the alert was created.
    * **state**: [`AlertState`][alert-state] The current state of the alert.
    * **state_last_modified_by**: `str` The actor who last modified the alert state.
    * **state_last_modified_at**: `datetime` The timestamp when the alert state was last modified.
    * **name**: `str` The name of the alert.  Same as the name of the rule that triggered it.
    * **description**: `str` The description of the alert.  Same as the description of the rule that triggered it.
    * **actor**: `str` The user who triggered the alert.
    * **actor_id**: `str` The user id who triggered the alert, if it is available.
    * **target**: `str` Unused legacy property.
    * **severity**: [`AlertSeverity`][alert-severity] Indicates static rule severity of the alert. (Deprecated)
    * **risk_severity**: [`RiskSeverity`][risk-severity] Indicates event risk severity of the alert.
    * **rule_id**: `str` The unique id corresponding to the rule which triggered the alert.
    * **watchlists**: `str` Watchlists the actor is on at the time of the alert (if any).
    """

    tenant_id: constr(max_length=40) = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    type: Optional[str] = Field(..., description="Rule type that generated the alert.")
    id: Optional[str] = Field(
        None, description="The unique id of the alert.", example="alertId"
    )
    created_at: datetime = Field(
        ...,
        alias="createdAt",
        description="The timestamp when the alert was created.",
        example="2020-02-19T01:57:45.006683Z",
    )
    state: Optional[str] = Field(..., description="The current state of the alert.")
    state_last_modified_by: Optional[str] = Field(None, alias="stateLastModifiedBy")
    state_last_modified_at: Optional[datetime] = Field(
        None, alias="stateLastModifiedAt"
    )
    name: Optional[str] = Field(
        None,
        description="The name of the alert.  Same as the name of the rule that triggered it.",
        example="Removable Media Exfiltration Rule",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the alert.  Same as the description of the rule that triggered it.",
        example="Alert me on all removable media exfiltration.",
    )
    actor: Optional[str] = Field(
        None,
        description="The user who triggered the alert.",
        example="exampleUser@mycompany.com",
    )
    actor_id: Optional[str] = Field(
        None,
        alias="actorId",
        description="The authority user id who triggered the alert, if it is available.",
        example="authorityUserId",
    )
    target: Optional[str] = None
    severity: Optional[str] = Field(
        None, description="Indicates static rule severity of the alert."
    )
    risk_severity: Optional[str] = Field(
        None,
        alias="riskSeverity",
        description="Indicates event risk severity of the alert.",
        example="MODERATE",
    )
    rule_id: Optional[str] = Field(
        None,
        alias="ruleId",
        description="The unique id corresponding to the rule which triggered the alert.",
        example="uniqueRuleId",
    )
    watchlists: Optional[List[Watchlist]] = Field(
        None,
        description="Watchlists the actor is on at the time of the alert.",
        example=[],
        table=lambda watchlists: "\n".join((w.name or w.type) for w in watchlists)
        if watchlists
        else watchlists,
        csv=lambda watchlists: "|".join((w.name or w.type) for w in watchlists)
        if watchlists
        else watchlists,
    )


class ObserverRuleMetadataEssentials(ObserverRuleMetadata):
    tenant_id: constr(max_length=40) = Field(
        ...,
        alias="tenantId",
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
    )
    observer_rule_id: Optional[str] = Field(
        None,
        alias="observerRuleId",
        description="Id of the rule in the observer.",
        example="UniqueRuleId",
    )
    type: Optional[str] = Field(..., description="Rule type of the rule.")


class AlertDetails(AlertSummary):
    """
    A model representing the full details of an alert. Includes all the fields from `AlertSummary` plus file event
    observations (the events that triggered the alert), and any notes that have been added to the alert.

    **Fields**:

    * **observations**: `List[Observation]` List of observed file events that triggered the alert.
    * **note**: `str` Most recent note added to the alert.
    """

    observations: Optional[List[Observation]]
    note: Optional[Note]
