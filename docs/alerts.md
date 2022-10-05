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

To create a query which filters alerts which have a state of `OPEN` or `PENDING` and were created in the past 3 days:
```python
query = AlertQuery(start_date=timedelta(days=3)).equals('State', ['OPEN', 'PENDING'])
```

All filter methods take a `term` string as their first argument, which indicates which field to filter on (ex: `'RiskSeverity'`),
and the second arg is the value (or list of values) to search for.

The following filter methods are available:
* `.equals(term, value)`
* `.not_equals(term, value)`
* `.contains(term, value)`
* `.does_not_contain(term, value)`

By default, all filters in a query will be combined in an `AND` group, meaning only results matching _all_ filters will
be returned. If you want to `OR` the filters, call the `.matches_any()` method on the query.

Pass the event constructed query object to the `client.alerts.v1.search()` method to get execute the search.

## Pagination

If a query results in more results than the configured page size of the query (max page size is 500), increment the 
`.page_num` value of the query and re-run the `.search()` method:

```python
from datetime import timedelta
import incydr
client = incydr.Client(**kwargs)

query = incydr.AlertQuery(start_date=timedelta(days=10))
first_page = client.alerts.v1.search(query)
if first_page.total_count > query.page_size:
    query.page_num += 1
second_page = client.alerts.v1.search(query)
... # continue until all alerts are retrieved
```

Alternately, the `client.alerts.v1.iter_all()` method will automatically request pages until all the results are complete
and will yield each Alert individually, so you don't need to think about paging at all:

```python
from datetime import timedelta
import incydr
client = incydr.Client(**kwargs)

query = incydr.AlertQuery(start_date=timedelta(days=10))
for alert in client.alerts.v1.iter_all(query):
    ... # process alert here
```