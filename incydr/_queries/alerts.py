from datetime import date
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
from incydr.enums import _Enum


class Operator(_Enum):
    # all valid filter operators for querying alerts
    IS = "IS"
    IS_NOT = "IS_NOT"
    EXISTS = "EXISTS"
    DOES_NOT_EXIST = "DOES_NOT_EXIST"
    ON = "ON"
    ON_OR_AFTER = "ON_OR_AFTER"
    ON_OR_BEFORE = "ON_OR_BEFORE"
    CONTAINS = "CONTAINS"


class AlertTerm(_Enum):
    AlertId = "AlertId"
    TenantId = "TenantId"
    Type = "Type"
    Name = "Name"
    Description = "Description"
    Actor = "Actor"
    ActorId = "ActorId"
    Target = "Target"
    RiskSeverity = "RiskSeverity"
    CreatedAt = "CreatedAt"
    HasAuthSignificantWatchlist = "HasAuthSignificantWatchlist"
    State = "State"
    StateLastModifiedAt = "StateLastModifiedAt"
    StateLastModifiedBy = "StateLastModifiedBy"
    LastModifiedTime = "LastModifiedTime"
    LastModifiedBy = "LastModifiedBy"
    RuleId = "RuleId"
    Severity = "Severity"


class Filter(BaseModel):
    term: AlertTerm
    operator: Operator
    value: Optional[Union[bool, int, str]]

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def _validate_enums(cls, values: dict):  # noqa `root_validator` is a classmethod
        term = values.get("term")
        operator = values.get("operator")
        value = values.get("value")

        # make sure `term` is valid enum value
        AlertTerm(term)
        if term == "HasAuthSignificantWatchlist" and not isinstance(value, bool):
            raise ValueError("HasAuthSignificantWatchlist requires a boolean value.")

        if operator in (Operator.EXISTS, Operator.DOES_NOT_EXIST):
            values["value"] = None
            return values

        if operator in (Operator.IS, Operator.IS_NOT):
            if not isinstance(value, (str, int)):
                raise ValueError(
                    f"`IS` and `IS_NOT` filters require a `str | int` value, got term={term}, operator={operator}, value={value}."
                )

        return values


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class Query(BaseModel):
    tenantId: str = None
    groupClause: str = "AND"
    groups: Optional[List[FilterGroup]]
    pgNum: int = 0
    pgSize: int = 100
    pgToken: Optional[str]
    srtDir: str = "DESC"
    srtKey: AlertTerm = "CreatedAt"

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}


class AlertQuery:
    """
    Class to build an alert query. Use the class methods to attach additional filter operators.

    **Parameters**:

         * **start_date**: `int | float | str | datetime | timedelta` -  Start of the date range to query for alerts.
            Defaults to None.
         * **end_date**: `int | float | str | datetime` - End of the date range to query for alerts. Defaults to
            None.
         * **on**: `date | datetime` - Retrieve alerts that occurred on a specific date (incompatible with either
            `start_date` or `end_date` arguments).
    """

    def __init__(
        self,
        start_date: Union[datetime, timedelta, int, float, str] = None,
        end_date: Union[datetime, int, float, str] = None,
        on: Union[date, datetime, int, float, str] = None,
    ):
        self._query = Query(groups=[])
        if on and any((start_date, end_date)):
            raise ValueError(
                "cannot use 'on' argument with 'start_date' or 'end_date' arguments."
            )
        if start_date or end_date or on:
            self._query.groups.append(
                _create_date_range_filter_group(start_date, end_date, on)
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

        When passed as part of a query, returns alerts where the field corresponding to the filter term equals the
        indicated value(s).

        Example:
            `AlertQuery().equals('Status', 'PENDING')` creates a query which will return all alerts with a status of
            'PENDING'.

        **Parameters**:

        * **term**: `str` - The term which corresponds to an alert field.
        * **values**: `str`, `List[str]` - The value(s) for the term to match.
        """
        if isinstance(values, (str, bool)):
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

        When passed as part of a query, returns alerts where the field corresponding to the filter term does not equal
        the indicated value(s).

        Example:
            `AlertQuery().not_equals('State', 'CLOSED')` creates a query which will return alerts that are not in a "CLOSED"
            state.

        **Parameters**:

        * **term**: `str` - The term which corresponds to an alert field.
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

    def contains(self, term: str, value: str):
        """
        Adds a `contains` filter to the query. The opposite of the `does_not_contain` filter.

        When passed as part of a query, returns alerts where the field corresponding to the filter term contains the
        provided string value.

        Example:
            `AlertQuery().contains('Description', 'removable media')` creates a query which will return alerts where the
            alert rule description contains the string "removable media".

        **Parameters**:

        * **term**: `str` - The term which corresponds to an alert field.
        * **values**: `str`, `List[str]` - The value(s) for the term to not match.
        """
        self._query.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.CONTAINS, value=value)]
            )
        )
        return self

    def matches_any(self):
        """
        Sets operator to combine multiple filters with `OR`.

        Returns alerts that match at least one of the filters in the query.

        Default operator is `AND`, which returns only alerts that match _all_ filters in the query.
        """
        self._query.groupClause = "OR"
        return self


def _create_date_range_filter_group(start_date, end_date, on):

    filters = []

    if isinstance(start_date, timedelta):
        start_date = datetime.utcnow() - start_date
    if on:
        filters.append(
            Filter(
                term=AlertTerm.CreatedAt,
                operator=Operator.ON,
                value=parse_timestamp(on),
            )
        )
        return FilterGroup(filters=filters)
    if start_date:
        filters.append(
            Filter(
                term=AlertTerm.CreatedAt,
                operator=Operator.ON_OR_AFTER,
                value=parse_timestamp(start_date),
            )
        )

    if end_date:
        filters.append(
            Filter(
                term=AlertTerm.CreatedAt,
                operator=Operator.ON_OR_BEFORE,
                value=parse_timestamp(end_date),
            )
        )
    return FilterGroup(filters=filters)
