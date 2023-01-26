from datetime import datetime
from datetime import timedelta

import pytest
from _client.queries.file_events import Filter
from _client.queries.file_events import FilterGroup
from pydantic import ValidationError

from incydr import EventQuery

TEST_START_DATE = "P1D"
TEST_TIMESTAMP = "2020-09-10 11:12:13"


@pytest.mark.parametrize(
    "start_timestamp",
    [
        TEST_TIMESTAMP,
        1599736333.0,
        1599736333,
        datetime.strptime(TEST_TIMESTAMP, "%Y-%m-%d %H:%M:%S"),
    ],
)
def test_event_query_when_start_date_creates_on_or_after_filter_group(start_timestamp):
    q = EventQuery(start_date=start_timestamp)
    expected = FilterGroup(
        filters=[
            Filter(
                term="@timestamp",
                operator="ON_OR_AFTER",
                value="2020-09-10T11:12:13.000Z",
            )
        ]
    )
    assert q.groups.pop() == expected


@pytest.mark.parametrize(
    "end_timestamp",
    [
        TEST_TIMESTAMP,
        1599736333.0,
        1599736333,
        datetime.strptime(TEST_TIMESTAMP, "%Y-%m-%d %H:%M:%S"),
    ],
)
def test_event_query_when_end_date_creates_on_or_before_filter_group(end_timestamp):
    q = EventQuery(end_date=end_timestamp)
    expected = FilterGroup(
        filters=[
            Filter(
                term="@timestamp",
                operator="ON_OR_BEFORE",
                value="2020-09-10T11:12:13.000Z",
            )
        ]
    )
    assert q.groups.pop() == expected


@pytest.mark.parametrize(
    "duration",
    [timedelta(days=7), "P7D"],
)
def test_event_query_when_start_date_duration_creates_within_the_last_filter_group(
    duration,
):
    q = EventQuery(start_date=duration)
    expected = FilterGroup(
        filterClause="AND",
        filters=[Filter(term="@timestamp", operator="WITHIN_THE_LAST", value="P7D")],
    )
    assert q.groups.pop() == expected


def test_event_query_when_with_no_date_args_appends_no_groups():
    q = EventQuery()
    assert len(q.groups) == 0


def test_event_query_is_when_single_value_creates_expected_filter_group():
    q = EventQuery(TEST_START_DATE).equals("file.category", "Document")
    expected = FilterGroup(
        filterClause="AND",
        filters=[Filter(term="file.category", operator="IS", value="Document")],
    )
    assert q.groups.pop() == expected


def test_event_query_is_when_multiple_values_creates_expected_filter_group():
    q = EventQuery(TEST_START_DATE).equals(
        "file.category", ["Document", "Audio", "Executable"]
    )
    expected = FilterGroup(
        filterClause="OR",
        filters=[
            Filter(term="file.category", operator="IS", value="Document"),
            Filter(term="file.category", operator="IS", value="Audio"),
            Filter(term="file.category", operator="IS", value="Executable"),
        ],
    )
    assert q.groups.pop() == expected


def test_event_query_is_not_when_single_value_creates_expected_filter_group():
    q = EventQuery(TEST_START_DATE).not_equals("file.category", "Document")
    expected = FilterGroup(
        filterClause="AND",
        filters=[Filter(term="file.category", operator="IS_NOT", value="Document")],
    )
    assert q.groups.pop() == expected


def test_event_query_is_not_when_multiple_values_creates_expected_filter_group():
    q = EventQuery(TEST_START_DATE).not_equals(
        "file.category", ["Document", "Audio", "Executable"]
    )
    expected = FilterGroup(
        filterClause="AND",
        filters=[
            Filter(term="file.category", operator="IS_NOT", value="Document"),
            Filter(term="file.category", operator="IS_NOT", value="Audio"),
            Filter(term="file.category", operator="IS_NOT", value="Executable"),
        ],
    )
    assert q.groups.pop() == expected


def test_event_query_is_when_no_values_raises_error():
    with pytest.raises(ValueError) as e:
        EventQuery(TEST_START_DATE).equals("file.category", [])
    assert e.value.args[0] == "equals() requires at least one value."


def test_event_query_is_when_invalid_value_for_term_raises_type_error():
    with pytest.raises(ValueError) as e:

        EventQuery(TEST_START_DATE).equals(
            "file.category", ["Document", "Invalid-term"]
        )
    assert (
        "'Invalid-term' is not a valid FileCategory. Expected one of ['Audio', 'Document', 'Executable', 'Image', 'Pdf', 'Presentation', 'Script', 'SourceCode', 'Spreadsheet', 'Video', 'VirtualDiskImage', 'Archive']"
        in str(e.value)
    )


def test_event_query_exists_creates_expected_filter_group():
    q = EventQuery(start_date=TEST_START_DATE).exists("event.action")
    expected = FilterGroup(
        filters=[Filter(term="event.action", operator="EXISTS", value=None)]
    )
    assert q.groups.pop() == expected


def test_event_query_does_not_exist_creates_expected_filter_group():
    q = EventQuery(start_date=TEST_START_DATE).does_not_exist("event.action")
    expected = FilterGroup(
        filters=[Filter(term="event.action", operator="DOES_NOT_EXIST", value=None)]
    )
    assert q.groups.pop() == expected


@pytest.mark.parametrize("input,expected_value", [(10, 10), ("10", 10.0), (10.0, 10.0)])
def test_event_query_greater_than_creates_expected_filter_group(input, expected_value):
    q = EventQuery(start_date=TEST_START_DATE).greater_than("risk.score", input)
    expected = FilterGroup(
        filters=[
            Filter(term="risk.score", operator="GREATER_THAN", value=expected_value)
        ]
    )
    assert q.groups.pop() == expected


def test_event_query_greater_than_when_non_numerical_value_raises_error():
    with pytest.raises(ValidationError) as e:
        EventQuery(start_date=TEST_START_DATE).greater_than("risk.score", "a string")
    assert "value is not a valid integer" in str(e.value)


@pytest.mark.parametrize("input,expected_value", [(10, 10), ("10", 10.0), (10.0, 10.0)])
def test_event_query_less_than_creates_expected_filter_group(input, expected_value):
    q = EventQuery(start_date=TEST_START_DATE).less_than("risk.score", input)
    expected = FilterGroup(
        filters=[Filter(term="risk.score", operator="LESS_THAN", value=expected_value)]
    )
    assert q.groups.pop() == expected


def test_event_query_less_than_when_non_numerical_value_raises_error():
    with pytest.raises(ValidationError) as e:
        EventQuery(start_date=TEST_START_DATE).less_than("risk.score", "a string")
    assert "value is not a valid integer" in str(e.value)


def test_event_query_matches_any_sets_query_group_clause_to_or():
    q = EventQuery(start_date=TEST_START_DATE).matches_any()
    assert q.group_clause == "OR"
