from typing import Union, List
from datetime import datetime
from .terms import FileCategory, Terms, TimeRange, EventAction, Category, ShareType, ReportType, RiskIndicators, \
    RiskSeverity, TrustReason, search_terms
from .models import _Filter, Query
from .models import FilterGroup
from .models import Operator
from .util import parse_timestamp
from numbers import Number


class TermFilter(object):
    def __init__(self, term):
        self.term = term

    def is_(self, values: Union[str, List[str]]):
        return _create_is_filter_group(self.term, values)

    def is_not(self, values: Union[str, List[str]]):
        return _create_is_filter_group(self.term, values, is_not=True)

    def exists(self):
        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.EXISTS.value)])

    def does_not_exist(self):
        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.DOES_NOT_EXIST.value)])

    def greater_than(self, value: Union[float, int]):
        if not isinstance(value, Number):
            raise Exception  # TODO

        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.GREATER_THAN.value, value=value)])

    def less_than(self, value: Union[float, int]):
        if not isinstance(value, Number):
            raise Exception  # TODO

        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.LESS_THAN.value, value=value)])


class TimestampFilter(object):
    def __init__(self):
        self.term = Terms.TIMESTAMP

    def on(self, date: Union[datetime, int, float, str]):
        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.ON.value, value=parse_timestamp(date))])

    def on_or_after(self, date: Union[datetime, int, float, str]):
        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.ON_OR_AFTER.value, value=parse_timestamp(date))])

    def on_or_before(self, date: Union[datetime, int, float, str]):
        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.ON_OR_BEFORE.value, value=parse_timestamp(date))])

    def within_the_last(self, value: TimeRange):
        if value not in TimeRange:
            raise TypeError(f'values for the `within_the_last()` operator method must be in {[e.value for e in TimeRange]}')

        return FilterGroup(filters=[_Filter(term=self.term, operator=Operator.WITHIN_THE_LAST.value, value=value)])

    def in_date_range(self, start_date: Union[datetime, int, float, str] = None, end_date: Union[datetime, int, float, str] = None):
        if not start_date and not end_date:
            raise Exception  # TODO, need at least one

        elif start_date and not end_date:
            return self.on_or_after(start_date)

        elif end_date and not start_date:
            return self.on_or_before(end_date)

        filters = [
            _Filter(term=self.term, operator=Operator.ON_OR_AFTER.value, value=parse_timestamp(start_date)),
            _Filter(term=self.term, operator=Operator.ON_OR_BEFORE.value, value=parse_timestamp(end_date))
        ]
        return FilterGroup(filters=[filters])
filter()

def Filter(term: Terms):

    if isinstance(term, Terms):
        term = term.value
    if term not in search_terms:
        raise TypeError(f'term must be one of {[e.value for e in Terms]}')

    if term == Terms.TIMESTAMP.value:
        return TimestampFilter()
    return TermFilter(term)

# class Filter(object):
#     def __init__(self, term: Terms):
#         if term.lower() == 'timestamp':
#             term = Terms.TIMESTAMP
#
#         if term not in Terms:
#             raise TypeError(f'term must be one of {[e.value for e in Terms]}')
#
#
#     def __new__(cls, *args, **kwargs):
#         return TimestampFilter.__new__()


# def _check_timestamp_term(term):
#     if term == '@timestamp':
#         raise TypeError(
#             "Construct the filter with the timestamp search term to use a time range filter operator. "
#             "Example: filter = Filter('@timestamp').within_the_last('30D')"
#         )

def _create_is_filter_group(term, values, is_not=False):
    if isinstance(values, str):
        values = [values]

    if len(values) < 1:
        raise Exception  # TODO - specify

    term_enum_map = {
        'file.category': FileCategory,
        'event.action': EventAction,
        'source.category': Category,
        'destination.category': Category,
        'event.shareType': ShareType,
        'report.type': ReportType,
        'risk.indicators.name': RiskIndicators,
        'risk.severity': RiskSeverity,
        'risk.trustReason': TrustReason
    }

    if term in term_enum_map.keys():
        valid_enums = term_enum_map.get(term)
        for v in values:
            if v not in valid_enums:
                raise TypeError(f"Values for search term: '{term}' must be in {[e.value for e in valid_enums]}")

    group = FilterGroup(filters=[])
    group.filterClause = 'OR' if len(values) > 1 else 'AND'
    op = Operator.IS_NOT.value if is_not else Operator.IS.value
    for v in values:
        group.filters.append(_Filter(term=term, operator=op, value=v))

    return group


def create_query(filters: Union[FilterGroup, List[FilterGroup]], or_query: bool = False):
    q = Query()
    q.groupClause = "AND" if not or_query else 'OR'

    if not isinstance(filters, List):
        filters = [filters]

    q.groups = filters

    return q

