from incydr.enums import _Enum


class ActivityType(_Enum):
    DOMAIN = "DOMAIN"
    ACCOUNT_NAME = "ACCOUNT_NAME"
    URL_PATH = "URL_PATH"
    SLACK = "SLACK"
    CLOUD_SHARE = "CLOUD_SHARE"
    CLOUD_SYNC = "CLOUD_SYNC"
    EMAIL = "EMAIL"
    FILE_UPLOAD = "FILE_UPLOAD"


class Name(_Enum):
    DEFAULT = "DEFAULT"
    BOX = "BOX"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    ICLOUD = "ICLOUD"
    ONE_DRIVE = "ONE_DRIVE"
    GMAIL = "GMAIL"
    OFFICE_365 = "OFFICE_365"


class PrincipalType(_Enum):
    USER = "USER"
    API_KEY = "API_KEY"
    DEVICE = "DEVICE"
    SERVICE = "SERVICE"


class SortKeys(_Enum):
    ACTIVITY_ID = "ACTIVITY_ID"
    DESCRIPTION = "DESCRIPTION"
    TYPE = "TYPE"
    UPDATED_BY_PRINCIPAL_NAME = "UPDATED_BY_PRINCIPAL_NAME"
    UPDATE_TIME = "UPDATE_TIME"
    VALUE = "VALUE"


class SortDirection(_Enum):
    ASC = "ASC"
    DESC = "DESC"
