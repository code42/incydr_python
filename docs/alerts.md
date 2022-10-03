# Alerts

::: incydr._alerts.client.AlertsV1
    :docstring:
    :members:

# Querying Alerts

Use the `AlertQuery` class to create a query for searching and filtering Incydr alerts.  More details on how to use the `AlertQuery` class can be found in the [Query Building](#query-building) section below.

::: incydr._queries.alerts.AlertQuery
    :docstring:
    :members: equals not_equals contains does_not_contain matches_any

## Query Building

The `AlertQuery` class can be imported directly from the `incydr` module.

```python
# import the AlertQuery class
from incydr import AlertQuery
```

The `AlertQuery` class can be constructed with arguments to define the date range for the query. The `start_date` 
argument sets the beginning of the date range to query, it can accept the following:

- a Unix epoch timestamp as an `int` or `float`
- a string representation of the date in either `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d` formats.
- a `datetime.datetime` object
- a `datetime.timedelta` (converts to `datetime` relative to the current time when the query object was instantiated)

The `end_date` argument sets the (optional) end of the range to query, and accepts the same arguments as `start_date`.

The `on` argument tells the alerts service to retrieve all alerts created on the date given, it accepts:
- a `datetime.date` or `datetime.datetime` object (`date` value will be extracted from `datetime` and hour/minute/seconds
  data will be discarded)
- a string representation of a date in either `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d` formats (again if time data is supplied
  it will have no effect on the query)

```python
# to create a query which filters alerts which have a state of 'OPEN' or 'PENDING' and were created in the past 3 days:

query = AlertQuery(start_date=timedelta(days=3)).equals('State', ['OPEN', 'PENDING'])
```

All operator methods take a term string, which matches an alert field (ex: `'RiskSeverity'`), to filter on as their first arg. The second arg is the value(s) to compare.

The following operators are available for filtering:
* `equals`
* `not_equals`
* `contains`
* `does_not_contain`
* `matches_any`

Pass the event query object to the `alerts.v1.search()` method to get the results.
