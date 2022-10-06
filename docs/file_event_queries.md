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

## Saved Searches

You can convert a saved search response object into an `EventQuery` to be used for searching using the
`EventQuery.from_saved_search()` classmethod:

```python
import incydr

client = incydr.Client(**kwargs)

saved_search = client.file_events.v2.get_saved_search("<saved_search_id>")
query = incydr.EventQuery.from_saved_search(saved_search)

results = client.file_events.v2.search(query)
```

## Pagination

To facilitate paging when a search query results in more total file events found than the `.page_size` value of the query
(the maximum page size is `10,000` events), the [file events search endpoint](https://developer.code42.com/api/#tag/File-Events/operation/searchEventsUsingPOST_1)
accepts a "page token" parameter, which indicates which event ID the currently requested page should start at.

By default, an `EventQuery` sets the `.page_token` value to an empty string (`""`), which tells the file events
service that this is the initial query and that it should return the next page token value in the response.

!!! note

    If `.page_token` is set to `None`, then the response will _not_ contain a next page token value, and pagination will need to be done
    manually by incrementing the `.page_num` property of the query.

    Using page numbers will only result in a maximum of 10,000 events returned, so it is recommended to always use page tokens.

The `client.file_events.v2.search()` method will automatically update the query object it receives with the next page
token, so fetching multiple pages of results is as simple as re-running the `.search()` method with the same query
object until the server sends a `null` page token value (meaning there are no more results):

```python
import incydr
from datetime import timedelta

client = incydr.Client(**kwargs)
query = incydr.EventQuery(start_date=timedelta(days=10))

while query.page_token is not None:
    response = client.file_events.v2.search(query)
    for event in response.file_events:
        ... # process events here
```
