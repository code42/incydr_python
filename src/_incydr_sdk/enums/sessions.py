from _incydr_sdk.enums import _Enum


class SessionStates(_Enum):
    """
    Enum indicating possible session states (includes alerts).
    """

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    CLOSED_TP = "CLOSED_TP"
    CLOSED_FP = "CLOSED_FP"
    OPEN_NEW_DATA = "OPEN_NEW_DATA"


class SessionSeverities(_Enum):
    """
    Enum indicating possible session severities.
    """

    NO_RISK = "NO_RISK"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContentInspectionStatuses(_Enum):
    """
    Enum indicating possible content inspection statuses.
    """

    PENDING = "PENDING"
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"


class SortKeys(_Enum):
    """
    Enum indicating possible fields by which to sort items results.
    """

    END_TIME = "end_time"
    SCORE = "score"
