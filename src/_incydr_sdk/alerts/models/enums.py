from __future__ import annotations

from _incydr_sdk.enums import _Enum


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
