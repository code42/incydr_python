from _incydr_sdk.enums import _Enum


class SortKeys(_Enum):
    """Possible keys to sort cases list results by."""

    NAME = "name"
    NUMBER = "number"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    STATUS = "status"
    ASSIGNEE_USERNAME = "assigneeUsername"
    SUBJECT_USERNAME = "subjectUsername"


class CaseStatus(_Enum):
    """Possible statuses for a case."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    ARCHIVED = "ARCHIVED"


class FileAvailability(_Enum):
    """Possible states of file-event source file availability."""

    error = "ERROR"
    exact_file_available = "EXACT_FILE_AVAILABLE"
    no_file_available = "NO_FILE_AVAILABLE"
    pending = "PENDING"
    recent_file_available = "RECENT_FILE_AVAILABLE"
