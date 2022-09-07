from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Union

from isodate import duration_isoformat
from isodate import parse_duration
from pydantic import BaseModel
from pydantic import root_validator
from pydantic import validate_arguments

from incydr._queries.util import parse_timestamp
from incydr.enums.file_events import Category
from incydr.enums.file_events import EventAction
from incydr.enums.file_events import EventSearchTerm
from incydr.enums.file_events import FileCategory
from incydr.enums.file_events import Operator
from incydr.enums.file_events import ReportType
from incydr.enums.file_events import RiskIndicators
from incydr.enums.file_events import RiskSeverity
from incydr.enums.file_events import ShareType
from incydr.enums.file_events import TrustReason

_term_enum_map = {
    "file.category": FileCategory,
    "event.action": EventAction,
    "source.category": Category,
    "destination.category": Category,
    "event.shareType": ShareType,
    "report.rule_type": ReportType,
    "risk.indicators.name": RiskIndicators,
    "risk.severity": RiskSeverity,
    "risk.trustReason": TrustReason,
}

file_category_extension_map = {
    "AUDIO": FileCategory.AUDIO,
    "DOCUMENT": FileCategory.DOCUMENT,
    "EXECUTABLE": FileCategory.EXECUTABLE,
    "IMAGE": FileCategory.IMAGE,
    "PDF": FileCategory.PDF,
    "PRESENTATION": FileCategory.PRESENTATION,
    "SCRIPT": FileCategory.SCRIPT,
    "SOURCE_CODE": FileCategory.SOURCE_CODE,
    "SPREADSHEET": FileCategory.SPREADSHEET,
    "VIDEO": FileCategory.VIDEO,
    "VIRTUAL_DISK_IMAGE": FileCategory.VIRTUAL_DISK_IMAGE,
    "ARCHIVE": FileCategory.ZIP,
    "ZIP": FileCategory.ZIP,
    "Zip": FileCategory.ZIP,
}


class Filter(BaseModel):
    term: EventSearchTerm
    operator: Operator
    value: Optional[Union[int, str]]

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def _validate_enums(cls, values: dict):  # noqa `root_validator` is a classmethod
        term = values.get("term")
        operator = values.get("operator")
        value = values.get("value")

        # make sure `term` is valid enum value
        EventSearchTerm(term)

        if operator in (Operator.EXISTS, Operator.DOES_NOT_EXIST):
            values["value"] = None
            return values

        if operator in (Operator.IS, Operator.IS_NOT):
            if not isinstance(value, (str, int)):
                raise ValueError(
                    f"`IS` and `IS_NOT` filters require a `str | int` value, got term={term}, operator={operator}, value={value}."
                )

        # catch additional enum terms
        try:
            value = file_category_extension_map[value]
            values.update({"value": value})
        except KeyError:
            pass

        # check that value is a valid enum for that search term
        enum = _term_enum_map.get(term)
        if enum:
            enum(value)

        return values


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class Query(BaseModel):
    groupClause: str = "AND"
    groups: Optional[List[FilterGroup]]
    pgNum: int = 1
    pgSize: int = 100
    pgToken: Optional[str]
    srtDir: str = "asc"
    srtKey: EventSearchTerm = "event.id"

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}


class EventQuery:
    """
    Class to build a file event query. Use the class methods to attach additional filter operators.

    **Parameters**:

         * **start_date**: `int`, `float`, `str`, `datetime`, `timedelta` -  Start of the date range to query for events. Defaults to None.
         * **end_date**: `int`, `float`, `str`, `datetime` - End of the date range to query for events.  Defaults to None.
    """

    def __init__(
        self,
        start_date: Union[datetime, timedelta, int, float, str] = None,
        end_date: Union[datetime, int, float, str] = None,
    ):
        self._query = Query(groups=[])
        if start_date or end_date:
            self._query.groups.append(
                _create_date_range_filter_group(start_date, end_date)
            )

    def __str__(self):
        return str(self._query)

    def dict(self):
        """
        Returns the query object as a dictionary.
        """
        return self._query.dict()

    def equals(self, term: str, values: Union[str, List[str]]):
        """
        Adds an `equals` filter to the query. The opposite of the `not_equals` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term equals the indicated value(s).

        Example:
            `EventQuery(**kwargs).equals('file.category', 'Document')` creates a query which will return file events where the `file.category` field is equal to `Document`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `str`, `List[str]` - The value(s) for the term to match.
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
        self._query.groups.append(filter_group)
        return self

    def not_equals(self, term, values: Union[str, List[str]]):
        """
        Adds an `not_equals` filter to the query. The opposite of the `equals` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term does not equal the indicated value(s).

        Example:
            `EventQuery(**kwargs).not_equals('file.category', 'Document')` creates a query which will return file events where the `file.category` field is NOT equal to `Document`.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        * **values**: `str`, `List[str]` - The value(s) for the term to not match.
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
            filterClause="OR" if len(values) > 1 else "AND",
        )
        self._query.groups.append(filter_group)
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
        self._query.groups.append(
            FilterGroup(filters=[Filter(term=term, operator=Operator.EXISTS)])
        )
        return self

    def does_not_exist(self, term: str):
        """
        Adds a `does_not_exist` filter to the query. The opposite of the `exists` filter.

        When passed as part of a query, returns events when the field corresponding to the filter term is `null`.

        Example:
            `EventQuery(**kwargs).does_not_exist('risk.TrustReason')` creates a query which will return file events where the `risk.trustReason` field is null.

        **Parameters**:

        * **term**: `str` - The term which corresponds to a file event field.
        """
        self._query.groups.append(
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

        self._query.groups.append(
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
                term=EventSearchTerm.TIMESTAMP,
                operator=Operator.WITHIN_THE_LAST,
                value=start_date,
            )
        )
    else:
        if start_date:
            filters.append(
                Filter(
                    term=EventSearchTerm.TIMESTAMP,
                    operator=Operator.ON_OR_AFTER,
                    value=parse_timestamp(start_date),
                )
            )

        if end_date:
            filters.append(
                Filter(
                    term=EventSearchTerm.TIMESTAMP,
                    operator=Operator.ON_OR_BEFORE,
                    value=parse_timestamp(end_date),
                )
            )
    return FilterGroup(filters=filters)
