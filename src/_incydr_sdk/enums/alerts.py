from __future__ import annotations

from _incydr_sdk.enums import _Enum
from _incydr_sdk.enums.file_events import RiskSeverity  # noqa


class AlertState(_Enum):
    """
    Enum indicating possible alert states.
    """

    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"


class RuleType(_Enum):
    """
    Rule type that generates alerts.
    """

    FED_ENDPOINT_EXFILTRATION = "FED_ENDPOINT_EXFILTRATION"
    FED_CLOUD_SHARE_PERMISSIONS = "FED_CLOUD_SHARE_PERMISSIONS"
    FED_FILE_TYPE_MISMATCH = "FED_FILE_TYPE_MISMATCH"
    FED_FILE_NAME_MATCH = "FED_FILE_NAME_MATCH"
    FED_COMPOSITE = "FED_COMPOSITE"


class AlertSeverity(_Enum):
    """
    Possible severity values for an alert.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Operator(_Enum):
    """
    The alert filter operators.
    """

    IS = "IS"
    IS_NOT = "IS_NOT"
    ON_OR_BEFORE = "ON_OR_BEFORE"
    ON_OR_AFTER = "ON_OR_AFTER"
    ON = "ON"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"


class AlertTerm(_Enum):
    ALERT_ID = "AlertId"
    TYPE = "Type"
    NAME = "Name"
    DESCRIPTION = "Description"
    ACTOR = "Actor"
    ACTOR_ID = "ActorId"
    TARGET = "Target"
    RISK_SEVERITY = "RiskSeverity"
    CREATED_AT = "CreatedAt"
    HAS_AUTH_SIGNIFICANT_WATCHLIST = "HasAuthSignificantWatchlist"
    STATE = "State"
    STATE_LAST_MODIFIED_AT = "StateLastModifiedAt"
    STATE_LAST_MODIFIED_BY = "StateLastModifiedBy"
    LAST_MODIFIED_TIME = "LastModifiedTime"
    LAST_MODIFIED_BY = "LastModifiedBy"
    RULE_ID = "RuleId"
    SEVERITY = "AlertSeverity"


class MessagingMethod(_Enum):
    """
    Instructor messaging method for an alert rule.

    Only part of alert rule responses as of 11/28/2022.
    """

    EMAIL = "Email"
    SLACK = "Slack"
