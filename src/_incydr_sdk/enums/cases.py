from _incydr_sdk.enums import _Enum


class SortKeys(_Enum):
    NAME = "name"
    NUMBER = "number"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    STATUS = "status"
    ASSIGNEE_USERNAME = "assigneeUsername"
    SUBJECT_USERNAME = "subjectUsername"


class CaseStatus(_Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    ARCHIVED = "ARCHIVED"


class FileAvailability(_Enum):
    error = "ERROR"
    exact_file_available = "EXACT_FILE_AVAILABLE"
    no_file_available = "NO_FILE_AVAILABLE"
    pending = "PENDING"
    recent_file_available = "RECENT_FILE_AVAILABLE"
