import pytest

from incydr import AlertQuery
from incydr.enums.alerts import AlertTerm


def test_base_query():
    query = AlertQuery()
    assert query.dict() == {
        "tenantId": None,
        "groupClause": "AND",
        "groups": [],
        "pgNum": 0,
        "pgSize": 100,
        "srtDir": "DESC",
        "srtKey": "CreatedAt",
    }


@pytest.mark.parametrize(
    "term",
    [
        AlertTerm.ALERT_ID,
        AlertTerm.ACTOR,
        AlertTerm.ACTOR_ID,
        AlertTerm.DESCRIPTION,
        AlertTerm.NAME,
        AlertTerm.RULE_ID,
        AlertTerm.TARGET,
        AlertTerm.TYPE,
        AlertTerm.LAST_MODIFIED_BY,
        AlertTerm.STATE_LAST_MODIFIED_BY,
    ],
)
def test_query_non_enum_string_terms(term):
    term_str = str(term.value)

    # equals:
    query = AlertQuery().equals(term, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": term_str, "operator": "IS", "value": "x"}],
        }
    ]
    query = AlertQuery().equals(term_str, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": term_str, "operator": "IS", "value": "x"}],
        }
    ]
    query = AlertQuery().equals(term, ["x", "y"])
    assert query.dict()["groups"] == [
        {
            "filterClause": "OR",
            "filters": [
                {"term": term_str, "operator": "IS", "value": "x"},
                {"term": term_str, "operator": "IS", "value": "y"},
            ],
        }
    ]

    # not equals:
    query = AlertQuery().not_equals(term, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": term_str, "operator": "IS_NOT", "value": "x"}],
        }
    ]
    query = AlertQuery().not_equals(term_str, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": term_str, "operator": "IS_NOT", "value": "x"}],
        }
    ]
    query = AlertQuery().not_equals(term, ["x", "y"])
    assert query.dict()["groups"] == [
        {
            "filterClause": "OR",
            "filters": [
                {"term": term_str, "operator": "IS_NOT", "value": "x"},
                {"term": term_str, "operator": "IS_NOT", "value": "y"},
            ],
        }
    ]

    # contains:
    query = AlertQuery().contains(term, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": term_str, "operator": "CONTAINS", "value": "x"}],
        }
    ]

    # not contains:
    query = AlertQuery().does_not_contain(term, "x")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [
                {"term": term_str, "operator": "DOES_NOT_CONTAIN", "value": "x"}
            ],
        }
    ]


def test_query_alert_state():
    query = AlertQuery().equals("State", "OPEN")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": "State", "operator": "IS", "value": "OPEN"}],
        }
    ]
    query = AlertQuery().equals("State", ["OPEN", "PENDING"])
    assert query.dict()["groups"] == [
        {
            "filterClause": "OR",
            "filters": [
                {"term": "State", "operator": "IS", "value": "OPEN"},
                {"term": "State", "operator": "IS", "value": "PENDING"},
            ],
        }
    ]


def test_query_alert_severity():
    query = AlertQuery().equals("Severity", "HIGH")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": "Severity", "operator": "IS", "value": "HIGH"}],
        }
    ]
    query = AlertQuery().equals("Severity", ["HIGH", "MEDIUM"])
    assert query.dict()["groups"] == [
        {
            "filterClause": "OR",
            "filters": [
                {"term": "Severity", "operator": "IS", "value": "HIGH"},
                {"term": "Severity", "operator": "IS", "value": "MEDIUM"},
            ],
        }
    ]


def test_query_alert_risk_severity():
    query = AlertQuery().equals("RiskSeverity", "HIGH")
    assert query.dict()["groups"] == [
        {
            "filterClause": "AND",
            "filters": [{"term": "RiskSeverity", "operator": "IS", "value": "HIGH"}],
        }
    ]
    query = AlertQuery().equals("RiskSeverity", ["HIGH", "MODERATE"])
    assert query.dict()["groups"] == [
        {
            "filterClause": "OR",
            "filters": [
                {"term": "RiskSeverity", "operator": "IS", "value": "HIGH"},
                {"term": "RiskSeverity", "operator": "IS", "value": "MODERATE"},
            ],
        }
    ]
