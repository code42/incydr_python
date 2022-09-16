from __future__ import annotations

from incydr.enums import _Enum


class NotificationType(_Enum):
    """
    Type of notification.
    """

    EMAIL = "EMAIL"


class ProblemType(_Enum):
    """
    Potential issues when running a query on alerts.
    """

    ILLEGAL_VALUE = "IllegalValue"
    ILLEGAL_OPERATOR = "IllegalOperator"
    MUST_BE_EMAIL_ADDRESS = "MustBeEmailAddress"
    MAX_LENGTH_EXCEEDED = "MaxLengthExceeded"
    INVALID_PAGE_SIZE = "InvalidPageSize"
    INVALID_PAGE_NUMBER = "InvalidPageNumber"
    MISSING_VALUE = "MissingValue"
    MISSING_GROUPS = "MissingGroups"
    MISSING_FILTERS = "MissingFilters"
    MAX_FILTERS_EXCEEDED = "MaxFiltersExceeded"
    SEARCH_FAILED = "SearchFailed"


class SearchClause(_Enum):
    """
    The filter clause to use when combining the search filters.  Must be AND/OR.s
    """

    AND = "AND"
    OR = "OR"


class SortDirection(_Enum):
    """
    The sort direction applied to the returned page of alerts.
    """

    ASC = "ASC"
    DESC = "DESC"
