from __future__ import annotations

from incydr.enums import _Enum


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


class SeverityRating(_Enum):
    """
    Possible severity values for an alert.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Operator(_Enum):
    """
    The filter operator to use.
    """

    is_ = "IS"
    is_not = "IS_NOT"
    on_or_before = "ON_OR_BEFORE"
    on_or_after = "ON_OR_AFTER"
    on = "ON"
    contains = "CONTAINS"
    does_not_contain = "DOES_NOT_CONTAIN"
