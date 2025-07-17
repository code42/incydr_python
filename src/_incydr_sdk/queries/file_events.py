from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Union

from isodate import duration_isoformat
from isodate import parse_duration
from pydantic import BaseModel
from pydantic import conint
from pydantic import Field
from pydantic import root_validator
from pydantic import validate_arguments

from _incydr_sdk.core.models import Model
from _incydr_sdk.enums.file_events import Category
from _incydr_sdk.enums.file_events import EventAction
from _incydr_sdk.enums.file_events import EventSearchTerm
from _incydr_sdk.enums.file_events import FileCategory
from _incydr_sdk.enums.file_events import Operator
from _incydr_sdk.enums.file_events import ReportType
from _incydr_sdk.enums.file_events import RiskIndicators
from _incydr_sdk.enums.file_events import RiskSeverity
from _incydr_sdk.enums.file_events import ShareType
from _incydr_sdk.enums.file_events import TrustReason
from _incydr_sdk.file_events.models.response import SavedSearch
from _incydr_sdk.file_events.models.response import SearchFilterGroup
from _incydr_sdk.file_events.models.response import SearchFilterGroupV2
from _incydr_sdk.queries.utils import parse_ts_to_ms_str

_term_enum_map = {
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


class Filter(BaseModel):
    term: str
    operator: Union[Operator, str]
    value: Optional[Union[int, str, List[str]]]

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def _validate_enums(cls, values: dict):  # noqa `root_validator` is a classmethod
        term = values.get("term")
        operator = values.get("operator")
        value = values.get("value")

        # 11-13-2024 - Removing strict filter term requirements to avoid breaking on new fields
        # make sure `term` is valid enum value
        # EventSearchTerm(term)

        if operator in (Operator.EXISTS, Operator.DOES_NOT_EXIST):
            values["value"] = None
            return values

        if operator in (Operator.IS, Operator.IS_NOT):
            if not isinstance(value, (str, int)):
                raise ValueError(
                    f"`IS` and `IS_NOT` filters require a `str | int` value, got term={term}, operator={operator}, value={value}."
                )

        # 11-13-2024 - Removing strict filter term requirements to avoid breaking on new fields
        # check that value is a valid enum for that search term
        # enum = _term_enum_map.get(term)
        # if enum:
        #     try:
        #         values.update(
        #             {"value": enum[value.upper()]}
        #         )  # check if enum name is passed as a value
        #     except KeyError:
        #         enum(value)

        return values


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class FilterGroupV2(BaseModel):
    subgroupClause: str = "AND"
    subgroups: List[Union[FilterGroupV2, FilterGroup]]


class Query(Model):
    groupClause: str = "AND"
    groups: Optional[List[FilterGroup]]
    pgNum: int = 1
    pgSize: int = 100
    pgToken: Optional[str]
    srtDir: str = "asc"
    srtKey: EventSearchTerm = "event.id"


class EventQuery(Model):
    """
    Class to build a file event query. Use the class methods to attach additional filter operators.

    **Parameters**:

         * **start_date**: `int`, `float`, `str`, `datetime`, `timedelta` -  Start of the date range to query for events. Defaults to None.
         * **end_date**: `int`, `float`, `str`, `datetime` - End of the date range to query for events.  Defaults to None.
    """

    group_clause: str = Field("AND", alias="groupClause")
    groups: Optional[List[FilterGroup]]
    page_num: int = Field(1, alias="pgNum")
    page_size: conint(le=10000) = Field(100, alias="pgSize")
    page_token: Optional[str] = Field("", alias="pgToken")
    sort_dir: str = Field("asc", alias="srtDir")
    sort_key: EventSearchTerm = Field("event.id", alias="srtKey")

    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}

    def __init__(
        self,
        start_date: Union[datetime, timedelta, int, float, str] = None,
        end_date: Union[datetime, int, float, str] = None,
        **kwargs,
    ):
        groups = kwargs.get("groups") or []

        if start_date or end_date:
            groups.append(_create_date_range_filter_group(start_date, end_date))

        kwargs["groups"] = groups
        super().__init__(**kwargs)

    def equals(self, term: str, values: Union[str, List[str]]):
        """
        Adds an `equals` filter to the query.

        When passed as part of a query, returns events when the field corresponding to the filter term equals the
        indicated value(s).

        Example:
            `EventQuery(**kwargs).equals('file.category', 'Document')` creates a query which will return file events
            where the `file.category` field is equal to `Document`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `str | List[str]` - The value(s) for the term to match.
        """
        if isinstance(values, str):
            values = [values]
        if len(values) < 1:
            raise ValueError("equals() requires at least one value.")
        filters = [Filter(term=term, operator=Operator.IS, value=val) for val in values]
        filter_group = FilterGroup(
            filters=filters,
            filterClause="OR" if len(values) > 1 else "AND",
        )
        self.groups.append(filter_group)
        return self

    def not_equals(self, term, values: Union[str, List[str]]):
        """
        Adds an `not_equals` filter to the query. The opposite of the `equals` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term does not equal the indicated value(s).

        Example:
            `EventQuery(**kwargs).not_equals('file.category', 'Document')` creates a query which will return file events where the `file.category` field is NOT equal to `Document`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `str | List[str]` - The value(s) for the term to not match.
        """

        if isinstance(values, str):
            values = [values]
        if len(values) < 1:
            raise ValueError("not_equals() requires at least one value.")
        filters = [
            Filter(term=term, operator=Operator.IS_NOT, value=val) for val in values
        ]
        filter_group = FilterGroup(
            filters=filters,
            filterClause="AND",
        )
        self.groups.append(filter_group)
        return self

    def exists(self, term: str):
        """
        Adds an `exists` filter to the query. The opposite of the `does_not_exist` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term is not `null`.

        Example:
            `EventQuery(**kwargs).exists('risk.trustReason')` creates a query which will return file events where the `risk.trustReason` field is populated with any not null value.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        """
        self.groups.append(
            FilterGroup(filters=[Filter(term=term, operator=Operator.EXISTS)])
        )
        return self

    def does_not_exist(self, term: str):
        """
        Adds a `does_not_exist` filter to the query.

        When passed as part of a query, returns events when the field corresponding to the filter term is `null`.

        Example:
            `EventQuery(**kwargs).does_not_exist('risk.TrustReason')` creates a query which will return file events where the `risk.trustReason` field is null.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        """
        self.groups.append(
            FilterGroup(filters=[Filter(term=term, operator=Operator.DOES_NOT_EXIST)])
        )
        return self

    @validate_arguments
    def greater_than(self, term: str, value: int):
        """
        Adds a `greater_than` filter to the query. The opposite of the `less_than` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term is greater than the indicated value.

        Example:
            `EventQuery(**kwargs).greater_than('risk.score', 10)` creates a query which will return file events where the `risk.score` field is greater than `10`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `int` - The value for the term to be greater than.
        """

        self.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.GREATER_THAN, value=value)]
            )
        )
        return self

    @validate_arguments
    def less_than(self, term: str, value: int):
        """
        Adds a `less_thn` filter to the query. The opposite of the `greater_than` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term is less than the indicated value.

        Example:
            `EventQuery(**kwargs).less_than('risk.score', 10)` creates a query which will return file events where the `risk.score` field is less than `10`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `int` - The value for the term to be less than.
        """
        self.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.LESS_THAN, value=value)]
            )
        )
        return self

    @validate_arguments
    def is_any(self, term: str, values: List[str]):
        """
        Adds a `is_any` filter to the query. The opposite of the `is_none` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term matches any of the provided values.

        Example:
            `EventQuery(**kwargs).is_any("destination.category", ["AI Tools", "Cloud Storage"])` creates a query which will return file events where the destination category is either AI Tools or Cloud Storage.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `List[str]` - The values to match.
        """
        self.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.IS_ANY, value=values)]
            )
        )
        return self

    @validate_arguments
    def is_none(self, term: str, values: List[str]):
        """
        Adds a `is_none` filter to the query. The opposite of the `is_any` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term matches none of the provided values.

        Example:
            `EventQuery(**kwargs).is_any("destination.category", ["AI Tools", "Cloud Storage"])` creates a query which will return file events where the destination category is anything other than AI Tools or Cloud Storage.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `List[str]` - The values for the term to not match.
        """
        self.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.IS_NONE, value=values)]
            )
        )
        return self

    def date_range(self, term: str, start_date=None, end_date=None):
        """
        Adds a date-based filter for the specified term.

        When passed as part of a query, returns events within the specified date range, or all events before/after the specified date if only one of start_date or end_date is given.

        Example:
            `EventQuery(**kwargs).date_range(term="event.inserted", start_date="P1D")` creates a query that returns all events inserted into Forensic Search within the past day.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **start_date**: `int`, `float`, `str`, `datetime`, `timedelta` -  Start of the date range to query for events. Defaults to None.
        * **end_date**: `int`, `float`, `str`, `datetime` - End of the date range to query for events.  Defaults to None.
        """
        if start_date or end_date:
            self.groups.append(
                _create_date_range_filter_group(
                    start_date=start_date, end_date=end_date, term=term
                )
            )
        return self

    def matches_any(self):
        """
        Sets operator to combine multiple filters to `OR`.
        Returns events that match at least one of the filters in the query.

        Default operator is `AND`, which returns events that match all filters in the query.
        """
        self.group_clause = "OR"
        return self

    def subquery(self, subgroup_query: EventQuery):
        """
        Adds a subgroup to the query, with any filter groups or subgroups from the subgroup_query added to the present query.

        Example:
            `EventQuery().greater_than("risk.score", 1).subquery(EventQuery().matches_any().equals("destination.category", "AI Tools").equals("file.name", "example"))`

        This example creates a query which matches events having a risk score of 1 or greater and have a destination category equal to "AI Tools" or have a filename equal to "example"

        **Parameters**:

        * **subgroup_query**: `EventQuery` - An EventQuery object. The filter groups and subgroups will be added to the present query. The subgroup query's group clause will be used for the created subgroup.
        """
        self.groups.append(
            FilterGroupV2(
                subgroupClause=subgroup_query.group_clause,
                subgroups=subgroup_query.groups,
            )
        )
        return self

    @classmethod
    def from_saved_search(cls, saved_search: SavedSearch):
        """
        Create an `EventQuery` object from a `SavedSearch` response.
        """
        query = cls()
        if saved_search.group_clause:
            query.group_clause = saved_search.group_clause
        if saved_search.groups:
            for i in saved_search.groups:
                query.groups.append(_handle_filter_group_type(i))
        if saved_search.srt_dir:
            query.sort_dir = saved_search.srt_dir
        if saved_search.srt_key:
            query.sort_key = saved_search.srt_key
        return query


def _create_date_range_filter_group(start_date, end_date, term=None):
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
                term=term or EventSearchTerm.TIMESTAMP,
                operator=Operator.WITHIN_THE_LAST,
                value=start_date,
            )
        )
    else:
        if start_date:
            filters.append(
                Filter(
                    term=term or EventSearchTerm.TIMESTAMP,
                    operator=Operator.ON_OR_AFTER,
                    value=parse_ts_to_ms_str(start_date),
                )
            )

        if end_date:
            filters.append(
                Filter(
                    term=term or EventSearchTerm.TIMESTAMP,
                    operator=Operator.ON_OR_BEFORE,
                    value=parse_ts_to_ms_str(end_date),
                )
            )
    return FilterGroup(filters=filters)


def _create_filter_group(filter_group: SearchFilterGroup) -> FilterGroup:
    filters = [
        Filter.construct(value=f.value, operator=f.operator, term=f.term)
        for f in filter_group.filters
    ]
    return FilterGroup.construct(
        filterClause=filter_group.filter_clause, filters=filters
    )


def _create_filter_group_v2(filter_group_v2: SearchFilterGroupV2) -> FilterGroupV2:
    subgroups = []
    for subgroup in filter_group_v2.subgroups:
        subgroups.append(_handle_filter_group_type(subgroup))
    return FilterGroupV2.construct(
        subgroupClause=filter_group_v2.subgroup_clause, subgroups=subgroups
    )


def _handle_filter_group_type(
    filter_group: Union[SearchFilterGroup, SearchFilterGroupV2]
) -> Union[FilterGroup, FilterGroupV2]:
    if isinstance(filter_group, SearchFilterGroup):
        return _create_filter_group(filter_group)
    if isinstance(filter_group, SearchFilterGroupV2):
        return _create_filter_group_v2(filter_group)
    else:
        raise TypeError(
            "Query filter group must be one of: SearchFilterGroup, SearchFilterGroupV2"
        )
