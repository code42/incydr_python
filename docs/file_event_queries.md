# File Event Queries

## EventQuery Class

Use the `EventQuery` class to create a query for searching and filtering file events.  More details on how to use the `EventQuery` class can be found in the [Query Building](#query-building) section below.

::: incydr._queries.file_events.EventQuery
    :docstring:
    :members: equals not_equals exists does_not_exist greater_than less_than matches_any

## Query Building

The `EventQuery` class can be imported directly from the `incydr` module.

```python
# import the EventQuery class
from incydr import EventQuery
```

The `EventQuery(start_date=None, end_date=None)` class takes a start date and/or an end date in various forms, including a timestamp string, a datetime object, or a number (float, int).

The `start_date` param can also take a duration in the form of an ISO-duration string or a timedelta object (ex. Use `start_date=P7D` to filter for events which occurred in the last week).

```python
# to create a query which filters events which have the file category of 'Document' or 'Audio' from the past 1 day

query = EventQuery('P1D').equals('file.category', ['Document', 'Audio'])

# to create a query which filters events based on the following criteria:
#       - occurred from 10-10-2020 to 11-10-2020.
#       - 'event.action' is not equal to 'file-created'
#       - 'risk.score' is greater than 10

start_date = "2020-10-10 11:12:13"
end_date = "2020-11-10 11:12:13"
query = EventQuery(start_date, end_date).not_equals('event.action', 'file-created').greater_than('risk.score', 10)
```

All operator methods take a term(str), which matches a file event field (ex: `'risk.severity'`), to filter on as their first arg.  If applicable the second arg is the value(s) to compare.

The following operators are available for filtering:
* `equals`
* `not_equals`
* `exists`
* `does_not_exist`
* `greater_than`
* `less_than`

Pass the event query object to the `file_events.v2.search()` method to get the results.
