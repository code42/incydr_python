from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import conint
from pydantic import Field
from pydantic import root_validator
from pydantic import StrictBool

from _incydr_sdk.core.models import Model
from _incydr_sdk.enums.alerts import AlertSeverity
from _incydr_sdk.enums.alerts import AlertState
from _incydr_sdk.enums.alerts import AlertTerm
from _incydr_sdk.enums.alerts import Operator
from _incydr_sdk.enums.alerts import RiskSeverity
from _incydr_sdk.queries.utils import parse_ts_to_ms_str


_term_enum_map = {
    AlertTerm.STATE: AlertState,
    AlertTerm.RISK_SEVERITY: RiskSeverity,
    AlertTerm.SEVERITY: AlertSeverity,
}


class Filter(BaseModel):
    term: AlertTerm
    operator: Operator
    value: Optional[Union[StrictBool, int, str]]

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

        enum = _term_enum_map.get(term)
        if enum:
            enum(value)

        if operator in (Operator.IS, Operator.IS_NOT):
            if not isinstance(value, (str, int)):
                raise ValueError(
                    f"`IS` and `IS_NOT` filters require a `str | int` value, got term={term}, operator={operator}, value={value}."
                )

        return values


class FilterGroup(BaseModel):
    filterClause: str = "AND"
    filters: Optional[List[Filter]]


class AlertQuery(Model):
    """
    Class to build an alert query. Use the class methods to attach additional filter operators.

    Usage examples:

    Construct a query that finds all alerts created in the past 10 days that are now marked `RESOLVED`:

        >>> import incydr
        >>> from datetime import timedelta
        >>> from incydr.enums.alerts import AlertState, AlertTerm
        >>> query = incydr.AlertQuery(start_date=timedelta(days=10)).equals(AlertTerm.STATE, AlertState.RESOLVED)

    Construct a query that finds alerts triggered by actor `user@example.com` with a risk severity of either `HIGH` or
    `CRITICAL`:

        >>> import incydr
        >>> query = incydr.AlertQuery().equals("Actor", "user@example.com").equals("RiskSeverity", ["HIGH", "CRITICAL"])

    **Parameters**:

     * **start_date**: `int | float | str | datetime | timedelta` - Start of the date range to query for alerts.
        Accepts `int|float` unix timestamp, string representation of the date (`%Y-%m-%d %H:%M:%S` or `%Y-%m-%d`
        formats), or `datetime` object for absolute dates, or if a `timedelta` is provided it will be relative to the
        current time when the query object was instantiated. Defaults to None.
     * **end_date**: `int | float | str | datetime` - End of the date range to query for alerts. Defaults to
        None.
     * **on**: `str | date | datetime` - Retrieve alerts that occurred on a specific date (incompatible with either
        `start_date` or `end_date` arguments).
    """

    tenant_id: str = Field(None, alias="tenantId")
    group_clause: str = Field("AND", alias="groupClause")
    groups: Optional[List[FilterGroup]]
    page_num: int = Field(0, alias="pgNum")
    page_size: conint(gt=0, le=500) = Field(100, alias="pgSize")
    sort_dir: str = Field("DESC", alias="srtDirection")
    sort_key: AlertTerm = Field("CreatedAt", alias="srtKey")

    def __init__(
        self,
        start_date: Union[datetime, timedelta, int, float, str] = None,
        end_date: Union[datetime, int, float, str] = None,
        on: Union[date, datetime, int, float, str] = None,
        **kwargs,
    ):
        groups = kwargs.get("groups") or []
        if on and any((start_date, end_date)):
            raise ValueError(
                "cannot use 'on' argument with 'start_date' or 'end_date' arguments."
            )
        if start_date or end_date or on:
            date_filter = _create_date_range_filter_group(start_date, end_date, on)
            groups.append(date_filter)
        kwargs["groups"] = groups
        super().__init__(**kwargs)

    def equals(self, term: str, values: Union[str, List[str]]):
        """
        Adds an `equals` filter to the query. The opposite of the `not_equals` filter.

        Causes the query to return alerts where the field corresponding to the term equals the indicated value(s).

        Example: `AlertQuery().equals('Status', 'PENDING')` will return all alerts with a status of 'PENDING'.

        **Parameters**:

        * **term**: `str` - The term which corresponds to an alert field. List of valid terms can be found in the
            [`incydr.enums.alerts.AlertTerm`][alert-terms] enum object.
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
        self.groups.append(filter_group)
        return self

    def not_equals(self, term: str, values: Union[str, List[str]]):
        """
        Adds an `not_equals` filter to the query. The opposite of the `equals` filter.

        When passed as part of a query, returns alerts where the field corresponding to the filter term does not equal
        the indicated value(s).

        Example:
            `AlertQuery().not_equals('State', 'RESOLVED')` creates a query which will return alerts that are not in a
            `RESOLVED` state.

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
        self.groups.append(filter_group)
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
        * **value**: `str` - The value for the term to match.
        """
        self.groups.append(
            FilterGroup(
                filters=[Filter(term=term, operator=Operator.CONTAINS, value=value)]
            )
        )
        return self

    def does_not_contain(self, term: str, value: str):
        """
        Adds a `does_not_contain` filter to the query. The opposite of the `contains` filter.

        When passed as part of a query, returns alerts where the field corresponding to the filter term does not contain
        the provided string value.

        Example:
            `AlertQuery().does_not_contain('Description', 'removable media')` creates a query which will return alerts
            where the alert rule description does not contain the string "removable media".

        **Parameters**:

        * **term**: `str` - The term which corresponds to an alert field.
        * **value**: `str` - The value for the term to not match.
        """
        self.groups.append(
            FilterGroup(
                filters=[
                    Filter(term=term, operator=Operator.DOES_NOT_CONTAIN, value=value)
                ]
            )
        )
        return self

    def matches_any(self):
        """
        Sets operator to combine multiple filters with `OR`.

        Returns alerts that match at least one of the filters in the query.

        Default operator is `AND`, which returns only alerts that match _all_ filters in the query.
        """
        self.group_clause = "OR"
        return self


def _create_date_range_filter_group(start_date, end_date, on):

    filters = []

    if isinstance(start_date, timedelta):
        start_date = datetime.utcnow() - start_date
    if on:
        filters.append(
            Filter(
                term=AlertTerm.CREATED_AT,
                operator=Operator.ON,
                value=parse_ts_to_ms_str(on),
            )
        )
        return FilterGroup(filters=filters)
    if start_date:
        filters.append(
            Filter(
                term=AlertTerm.CREATED_AT,
                operator=Operator.ON_OR_AFTER,
                value=parse_ts_to_ms_str(start_date),
            )
        )

    if end_date:
        filters.append(
            Filter(
                term=AlertTerm.CREATED_AT,
                operator=Operator.ON_OR_BEFORE,
                value=parse_ts_to_ms_str(end_date),
            )
        )
    return FilterGroup(filters=filters)
