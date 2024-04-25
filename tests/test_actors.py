import json
from urllib.parse import urlencode

import pytest
from pytest_httpserver import HTTPServer

from _incydr_cli.main import incydr
from _incydr_sdk.actors.client import ActorNotFoundError
from _incydr_sdk.actors.models import Actor
from _incydr_sdk.actors.models import ActorFamily
from _incydr_sdk.actors.models import ActorsPage
from incydr import Client

CHILD_ACTOR_ID = "child-actor-id"
PARENT_ACTOR_ID = "parent-actor-id"
CHILD_ACTOR_NAME = "child@email.com"
PARENT_ACTOR_NAME = "parent@email.com"

CHILD_ACTOR = {
    "active": True,
    "actorId": CHILD_ACTOR_ID,
    "alternateNames": ["test-alt-name"],
    "country": "usa",
    "department": "product",
    "division": "engineering",
    "employeeType": "full-time",
    "firstName": "first",
    "inScope": True,
    "lastName": "last",
    "locality": "minneapolis",
    "managerActorId": "test-manager-id",
    "name": CHILD_ACTOR_NAME,
    "parentActorId": "parent-actor-id",
    "region": "midwest",
    "title": "software engineer",
}

PARENT_ACTOR = {
    "active": True,
    "actorId": PARENT_ACTOR_ID,
    "alternateNames": [],
    "country": "usa",
    "department": "product",
    "division": "engineering",
    "employeeType": "full-time",
    "firstName": "first",
    "inScope": True,
    "lastName": "last",
    "locality": "minneapolis",
    "managerActorId": "test-manager-id",
    "name": PARENT_ACTOR_NAME,
    "parentActorId": None,
    "region": "midwest",
    "title": "software engineer",
}

ACTOR_FAMILY = {"children": [CHILD_ACTOR], "parent": PARENT_ACTOR}


@pytest.fixture
def mock_get_actor_by_name(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode(
            {
                "nameStartsWith": CHILD_ACTOR_NAME,
                "pageSize": 500,
                "page": 1,
            }
        ),
    ).respond_with_json({"actors": [CHILD_ACTOR]})


@pytest.fixture
def mock_get_actor_by_name_prefer_parent(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/actors/actor/name/{CHILD_ACTOR_NAME}/parent", method="GET"
    ).respond_with_json(PARENT_ACTOR)


@pytest.fixture
def mock_get_actor_by_id(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/actors/actor/id/{CHILD_ACTOR_ID}", method="GET"
    ).respond_with_json(CHILD_ACTOR)


@pytest.fixture
def mock_get_actor_by_id_prefer_parent(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/actors/actor/id/{CHILD_ACTOR_ID}/parent", method="GET"
    ).respond_with_json(PARENT_ACTOR)


@pytest.fixture
def mock_get_family_by_member_id(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/actors/actor/id/{CHILD_ACTOR_ID}/family", method="GET"
    ).respond_with_json(ACTOR_FAMILY)


@pytest.fixture
def mock_get_family_by_member_name(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        uri=f"/v1/actors/actor/name/{CHILD_ACTOR_NAME}/family", method="GET"
    ).respond_with_json(ACTOR_FAMILY)


def test_get_page_with_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "pageSize": 500,
        "page": 1,
    }
    actors_page = {
        "actors": [PARENT_ACTOR, CHILD_ACTOR],
    }
    httpserver_auth.expect_request(
        "/v1/actors/actor/search", method="GET", query_string=urlencode(query)
    ).respond_with_json(actors_page)

    client = Client()
    page = client.actors.v1.get_page()
    assert isinstance(page, ActorsPage)
    assert page.actors[0].json() == json.dumps(PARENT_ACTOR)
    assert page.actors[1].json() == json.dumps(CHILD_ACTOR)
    assert len(page.actors) == 2


def test_get_page_when_custom_query_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    query = {
        "nameStartsWith": "child",
        "nameEndsWith": "email.com",
        "active": True,
        "pageSize": 100,
        "page": 2,
    }
    actors_page = {
        "actors": [CHILD_ACTOR],
    }
    httpserver_auth.expect_request(
        "/v1/actors/actor/search", method="GET", query_string=urlencode(query)
    ).respond_with_json(actors_page)

    client = Client()
    page = client.actors.v1.get_page(
        name_starts_with="child",
        name_ends_with="email.com",
        active=True,
        page_size=100,
        page_num=2,
    )
    assert isinstance(page, ActorsPage)
    assert page.actors[0].json() == json.dumps(CHILD_ACTOR)
    assert len(page.actors) == 1


def test_get_page_when_prefer_parent_returns_expected_data(httpserver_auth: HTTPServer):
    query = {
        "pageSize": 500,
        "page": 1,
    }
    actors_page = {
        "actors": [PARENT_ACTOR],
    }
    httpserver_auth.expect_request(
        "/v1/actors/actor/search/parent", method="GET", query_string=urlencode(query)
    ).respond_with_json(actors_page)

    client = Client()
    page = client.actors.v1.get_page(prefer_parent=True)
    assert isinstance(page, ActorsPage)
    assert page.actors[0].json() == json.dumps(PARENT_ACTOR)
    assert len(page.actors) == 1


def test_iter_all_with_default_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode({"pageSize": 2, "page": 1}),
    ).respond_with_json({"actors": [CHILD_ACTOR, PARENT_ACTOR]})

    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode({"pageSize": 2, "page": 2}),
    ).respond_with_json({"actors": []})

    client = Client()
    iterator = client.actors.v1.iter_all(page_size=2)
    expected_actors = [CHILD_ACTOR, PARENT_ACTOR]
    total_count = 0
    for item in iterator:
        total_count += 1
        assert isinstance(item, Actor)
        assert item.json() == json.dumps(expected_actors.pop(0))
    assert total_count == 2


def test_iter_all_when_custom_params_returns_expected_data(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode(
            {
                "nameStartsWith": "child",
                "nameEndsWith": "email.com",
                "active": True,
                "pageSize": 2,
                "page": 1,
            }
        ),
    ).respond_with_json({"actors": [CHILD_ACTOR, PARENT_ACTOR]})

    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode(
            {
                "nameStartsWith": "child",
                "nameEndsWith": "email.com",
                "active": True,
                "pageSize": 2,
                "page": 2,
            }
        ),
    ).respond_with_json({"actors": []})

    client = Client()
    iterator = client.actors.v1.iter_all(
        active=True, name_starts_with="child", name_ends_with="email.com", page_size=2
    )
    expected_actors = [CHILD_ACTOR, PARENT_ACTOR]
    total_count = 0
    for item in iterator:
        total_count += 1
        assert isinstance(item, Actor)
        assert item.json() == json.dumps(expected_actors.pop(0))
    assert total_count == 2


def test_iter_all_when_prefer_parent_returns_expected_data(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search/parent",
        method="GET",
        query_string=urlencode({"pageSize": 1, "page": 1}),
    ).respond_with_json({"actors": [CHILD_ACTOR]})

    httpserver_auth.expect_request(
        "/v1/actors/actor/search/parent",
        method="GET",
        query_string=urlencode({"pageSize": 1, "page": 2}),
    ).respond_with_json({"actors": [PARENT_ACTOR]})

    httpserver_auth.expect_request(
        "/v1/actors/actor/search/parent",
        method="GET",
        query_string=urlencode({"pageSize": 1, "page": 3}),
    ).respond_with_json({"actors": []})

    client = Client()
    iterator = client.actors.v1.iter_all(page_size=1, prefer_parent=True)
    expected_actors = [CHILD_ACTOR, PARENT_ACTOR]
    total_count = 0
    for item in iterator:
        total_count += 1
        assert isinstance(item, Actor)
        assert item.json() == json.dumps(expected_actors.pop(0))
    assert total_count == 2


def test_get_actor_by_id_returns_expected_data(mock_get_actor_by_id):
    client = Client()
    response = client.actors.v1.get_actor_by_id(CHILD_ACTOR_ID)
    assert isinstance(response, Actor)
    assert response.actor_id == CHILD_ACTOR_ID
    assert response.json() == json.dumps(CHILD_ACTOR)


def test_get_actor_by_id_with_prefer_parent_returns_expected_data(
    mock_get_actor_by_id_prefer_parent,
):
    client = Client()
    response = client.actors.v1.get_actor_by_id(CHILD_ACTOR_ID, prefer_parent=True)
    assert isinstance(response, Actor)
    assert response.actor_id == PARENT_ACTOR_ID
    assert response.json() == json.dumps(PARENT_ACTOR)


def test_get_actor_by_name_returns_expected_data(mock_get_actor_by_name):
    client = Client()
    response = client.actors.v1.get_actor_by_name(CHILD_ACTOR_NAME)
    assert isinstance(response, Actor)
    assert response.actor_id == CHILD_ACTOR_ID
    assert response.name == CHILD_ACTOR_NAME
    assert response.json() == json.dumps(CHILD_ACTOR)


def test_get_actor_by_name_when_prefer_parent_returns_expected_data(
    mock_get_actor_by_name_prefer_parent,
):
    client = Client()
    response = client.actors.v1.get_actor_by_name(CHILD_ACTOR_NAME, prefer_parent=True)
    assert isinstance(response, Actor)
    assert response.actor_id == PARENT_ACTOR_ID
    assert response.name == PARENT_ACTOR_NAME
    assert response.json() == json.dumps(PARENT_ACTOR)


def test_get_actor_by_name_when_actor_not_found_raises_error(
    httpserver_auth: HTTPServer,
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode(
            {"nameStartsWith": CHILD_ACTOR_NAME, "pageSize": 500, "page": 1}
        ),
    ).respond_with_json({"actors": []})

    client = Client()
    with pytest.raises(ActorNotFoundError) as e:
        client.actors.v1.get_actor_by_name(CHILD_ACTOR_NAME)
    assert "Actor Not Found Error" in str(e.value)


def test_get_family_by_member_id_returns_expected_data(mock_get_family_by_member_id):
    client = Client()
    response = client.actors.v1.get_family_by_member_id(CHILD_ACTOR_ID)
    assert isinstance(response, ActorFamily)
    assert isinstance(response.children[0], Actor)
    assert isinstance(response.parent, Actor)
    assert response.json() == json.dumps(ACTOR_FAMILY)


def test_get_family_by_member_name_returns_expected_data(
    mock_get_family_by_member_name,
):
    client = Client()
    response = client.actors.v1.get_family_by_member_name(CHILD_ACTOR_NAME)
    assert isinstance(response, ActorFamily)
    assert isinstance(response.children[0], Actor)
    assert isinstance(response.parent, Actor)
    assert response.json() == json.dumps(ACTOR_FAMILY)


# ************************************************ CLI ************************************************


def test_cli_list_when_default_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode({"pageSize": 500, "page": 1}),
    ).respond_with_json({"actors": [CHILD_ACTOR, PARENT_ACTOR]})

    result = runner.invoke(incydr, ["actors", "list"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_custom_params_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search",
        method="GET",
        query_string=urlencode(
            {
                "nameStartsWith": "child",
                "nameEndsWith": "email.com",
                "active": True,
                "pageSize": 500,
                "page": 1,
            }
        ),
    ).respond_with_json({"actors": [CHILD_ACTOR, PARENT_ACTOR]})

    result = runner.invoke(
        incydr,
        [
            "actors",
            "list",
            "--active",
            "--name-starts-with",
            "child",
            "--name-ends-with",
            "email.com",
        ],
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_list_when_prefer_parent_makes_expected_call(
    httpserver_auth: HTTPServer, runner
):
    httpserver_auth.expect_request(
        "/v1/actors/actor/search/parent",
        method="GET",
        query_string=urlencode({"pageSize": 500, "page": 1}),
    ).respond_with_json({"actors": [CHILD_ACTOR, PARENT_ACTOR]})

    result = runner.invoke(incydr, ["actors", "list", "--prefer-parent"])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_get_by_actor_id_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_actor_by_id
):
    result = runner.invoke(incydr, ["actors", "show", "--actor-id", CHILD_ACTOR_ID])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_get_by_actor_id_and_prefer_parent_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_actor_by_id_prefer_parent
):
    result = runner.invoke(
        incydr, ["actors", "show", "--actor-id", CHILD_ACTOR_ID, "--prefer-parent"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_get_by_name_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_actor_by_name
):
    result = runner.invoke(incydr, ["actors", "show", "--name", CHILD_ACTOR_NAME])
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_when_get_by_name_and_prefer_parent_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_actor_by_name_prefer_parent
):
    result = runner.invoke(
        incydr, ["actors", "show", "--name", CHILD_ACTOR_NAME, "--prefer-parent"]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_family_when_get_by_actor_id_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_family_by_member_id
):
    result = runner.invoke(
        incydr, ["actors", "show-family", "--actor-id", CHILD_ACTOR_ID]
    )
    httpserver_auth.check()
    assert result.exit_code == 0


def test_cli_show_family_when_get_by_name_makes_expected_call(
    httpserver_auth: HTTPServer, runner, mock_get_family_by_member_name
):
    result = runner.invoke(
        incydr, ["actors", "show-family", "--name", CHILD_ACTOR_NAME]
    )
    httpserver_auth.check()
    assert result.exit_code == 0
