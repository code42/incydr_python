from enum import Enum


class GroupingOperator(Enum):
    AND = "AND"
    OR = "OR"


class Operator(Enum):
    IS = "IS"
    IS_NOT = "IS_NOT"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    ON = "ON"
    ON_OR_AFTER = "ON_OR_AFTER"
    ON_OR_BEFORE = "ON_OR_BEFORE"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"


class UsersToAlertOn(Enum):
    ALL_USERS = "ALL_USERS"
    ALL_USERS_NOT_SPECIFIED = "ALL_USERS_NOT_SPECIFIED"
    SPECIFIED_USERS = "SPECIFIED_USERS"


class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class NotificationType(Enum):
    EMAIL = "EMAIL"


class FileCategory(Enum):
    ARCHIVE = "ARCHIVE"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    EXECUTABLE = "EXECUTABLE"
    IMAGE = "IMAGE"
    PDF = "PDF"
    PRESENTATION = "PRESENTATION"
    SCRIPT = "SCRIPT"
    SOURCE_CODE = "SOURCE_CODE"
    SPREADSHEET = "SPREADSHEET"
    VIDEO = "VIDEO"
    VIRTUAL_DISK_IMAGE = "VIRTUAL_DISK_IMAGE"
