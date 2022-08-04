from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Union

from isodate import duration_isoformat
from isodate import parse_duration

from .enums import Category
from .enums import EventAction
from .enums import EventTerms
from .enums import FileCategory
from .enums import ReportType
from .enums import RiskIndicators
from .enums import RiskSeverity
from .enums import ShareType
from .enums import TrustReason
from incydr._queries._file_events.models import Filter
from incydr._queries._file_events.models import FilterGroup
from incydr._queries._file_events.models import Operator
from incydr._queries._file_events.models import Query
from incydr._queries.util import parse_timestamp
from incydr._queries.util import validate_numerical_value


class EventQuery:
    """
    Class to build a file event query.

    Args:
        start_date (int, float, str, datetime, timedelta): Start of the date range to query for events. Defaults to None.
        end_date (int, float, str, datetime): End of the date range to query for events.  Defaults to None.
    """

    def __init__(
        self,
        start_date: Union[datetime, timedelta, int, float, str] = None,
        end_date: Union[datetime, int, float, str] = None,
    ):
        self._query = Query(groups=[])
        self._query.groups.append(_create_date_range_filter_group(start_date, end_date))

    def __str__(self):
        return str(self._query)

    def dict(self):
        return self._query.dict()

    def is_equal_to(self, term, values: Union[str, List[str]]):
        self._query.groups.append(_create_is_filter_group(term, values))
        return self

    def is_not_equal_to(self, term, values: Union[str, List[str]]):
        self._query.groups.append(_create_is_filter_group(term, values, is_not=True))
        return self

    def exists(self, term):
        self._query.groups.append(
            FilterGroup(filters=[Filter(term=term, operator=Operator.EXISTS)])
        )
        return self

    def does_not_exist(self, term):
        self._query.groups.append(
            FilterGroup(filters=[Filter(term=term, operator=Operator.DOES_NOT_EXIST)])
        )
        return self

    def greater_than(self, term, value: Union[float, int]):
        value = validate_numerical_value(value)

        self._query.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.GREATER_THAN, value=value)]
            )
        )
        return self

    def less_than(self, term, value: Union[float, int]):
        value = validate_numerical_value(value)

        self._query.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.LESS_THAN, value=value)]
            )
        )
        return self

    def matches_any(self):
        """
        Sets operator to combine multiple filters to `OR`.
        Returns events that match at least one of the filters in the query.

        Default operator is `AND`, which returns events that match all filters in the query.
        """
        self._query.groupClause = "OR"
        return self


def _create_is_filter_group(term, values, is_not=False):
    if isinstance(values, str):
        values = [values]

    if len(values) < 1:
        raise ValueError("is_() and is_not() filters require at least one value.")

    # terms that consist of specific enum values
    term_enum_map = {
        "file.category": FileCategory,
        "event.action": EventAction,
        "source.category": Category,
        "destination.category": Category,
        "event.shareType": ShareType,
        "report.type": ReportType,
        "risk.indicators.name": RiskIndicators,
        "risk.severity": RiskSeverity,
        "risk.trustReason": TrustReason,
    }

    # check that the provided value(s) are valid for the given term
    if term in term_enum_map.keys():
        valid_enums = term_enum_map.get(term)
        for v in values:
            if v not in valid_enums:
                raise TypeError(
                    f"Values for search term: '{term}' must be in {[e.value for e in valid_enums]}"
                )

    group = FilterGroup(filters=[])
    group.filterClause = "OR" if len(values) > 1 else "AND"
    op = Operator.IS_NOT if is_not else Operator.IS
    for v in values:
        group.filters.append(Filter(term=term, operator=op, value=v))

    return group


def _create_date_range_filter_group(start_date, end_date):
    def _validate_duration_str(iso_duration_str):
        try:
            parse_duration(iso_duration_str)
        except Exception:
            return False
        return True

    filters = []

    if isinstance(start_date, timedelta) or _validate_duration_str(start_date):
        if isinstance(start_date, timedelta):
            start_date = duration_isoformat(start_date)
        filters.append(
            Filter(
                term=EventTerms.TIMESTAMP,
                operator=Operator.WITHIN_THE_LAST,
                value=start_date,
            )
        )
    else:
        if start_date:
            filters.append(
                Filter(
                    term=EventTerms.TIMESTAMP,
                    operator=Operator.ON_OR_AFTER,
                    value=parse_timestamp(start_date),
                )
            )

        if end_date:
            filters.append(
                Filter(
                    term=EventTerms.TIMESTAMP,
                    operator=Operator.ON_OR_BEFORE,
                    value=parse_timestamp(end_date),
                )
            )

    return FilterGroup(filters=filters)
