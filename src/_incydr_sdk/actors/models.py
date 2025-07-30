from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class QueryActorsRequest(BaseModel):
    nameStartsWith: Optional[str] = None
    nameEndsWith: Optional[str] = None
    active: Optional[bool] = None
    pageSize: Optional[int] = None
    page: Optional[int] = None


class Actor(ResponseModel):
    """
    A model representing an Actor.

    **Fields**:

    * **active**: `bool` Whether or not the actor is active.
    * **actor_id**: `str` The unique ID of the actor.
    * **alternate_names**: `List[str]` A list of other names the actor may have.
    * **country**: `str` The actor's country.
    * **department**: `str` The actor's department.
    * **division**: `str` The actor's division.
    * **employee_type**: `str` The actor's employment type, such as if they're a contractor.
    * **end_date**: `str` The actor's end date.
    * **first_name**: `str` The first (given) name of the actor.
    * **in_scope**: `str` The actor's scope state. An actor is considered "in scope" if their activity is monitored in at least one data source.
    * **last_name**: `str` The last (family) name of the actor.
    * **locality**: `str` - The actor's locality (city).
    * **manager_actor_id**: `str` The actor ID of the actor's manager.
    * **name**: `str` The actor's (eg. full username/email) name.
    * **notes**: `str` Notes about the actor.
    * **parentActorId**: `str` The actor ID of this actor's parent actor. (if the actor has a parent).
    * **region**: `str` The actor's region (state).
    * **start_date**: `str` The actor's start date.
    * **title**: `str` The actor's job title.
    """

    active: Optional[bool] = Field(
        None, description="Whether or not the actor is active.", examples=[True]
    )
    actor_id: Optional[str] = Field(
        None, alias="actorId", description="The actor ID.", examples=["112233445566"]
    )
    alternate_names: Optional[List[str]] = Field(
        None,
        alias="alternateNames",
        description="A list of other names the actor may have.",
        examples=[["johnsmith@gmail.com", "john-smith@company.com"]],
    )
    country: Optional[str] = Field(
        None, description="The actor's country", examples=["United States"]
    )
    department: Optional[str] = Field(
        None, description="The actor's department", examples=["Product"]
    )
    division: Optional[str] = Field(
        None, description="The actor's division", examples=["Engineering"]
    )
    employee_type: Optional[str] = Field(
        None,
        alias="employeeType",
        description="The actor's employment, such as if they're a contractor.",
        examples=["full-time"],
    )
    end_date: Optional[str] = Field(
        None,
        alias="endDate",
        description="The actor's end date.",
        examples=["2024-09-18"],
    )
    first_name: Optional[str] = Field(
        None,
        alias="firstName",
        description="The first name of the actor.",
        examples=["Smith"],
    )
    in_scope: Optional[bool] = Field(
        None,
        alias="inScope",
        description="The actor's scope state. An actor is considered 'in scope' if their activity is monitored in at least one data source.",
        examples=[True],
    )
    last_name: Optional[str] = Field(
        None,
        alias="lastName",
        description="The last name of the actor.",
        examples=["John"],
    )
    locality: Optional[str] = Field(
        None, description="The actor's locality (city).", examples=["Minneapolis"]
    )
    manager_actor_id: Optional[str] = Field(
        None,
        alias="managerActorId",
        description="The actor ID of the actor's manager",
        examples=["9988776655"],
    )
    name: Optional[str] = Field(
        None,
        description="The actor's (eg. full username/email) name.",
        examples=["john.smith@gmail.com"],
    )
    notes: Optional[str] = Field(
        None,
        alias="notes",
        description="Notes about the actor.",
        examples=["A super cool person."],
    )
    parent_actor_id: Optional[str] = Field(
        None,
        alias="parentActorId",
        description="The actor ID of this actor's parent actor. (if the actor has a parent).",
        examples=["442244224422"],
    )
    region: Optional[str] = Field(
        None, description="The actor's region.", examples=["Minnesota"]
    )
    start_date: Optional[str] = Field(
        None,
        alias="startDate",
        description="The actor's start date.",
        examples=["2024-09-18"],
    )
    title: Optional[str] = Field(
        None, description="The actor's job title", examples=["Software Engineer"]
    )


class ActorFamily(ResponseModel):
    """
    A model representing an actor family.

    An actor family consists of one or more child actors adopted by a single parent. If an actor is not associated with
    any other actors, the family consists of only the single actor.

    **Fields**:

    * **children**: `List[[Actor][actor-model]]` The list of child actors associated with the parent.
    * **parent**: `[Actor][actor-model]` The parent actor of the family.
    """

    children: List[Actor] = Field(description="The child actors in the family.")
    parent: Actor = Field(description="The parent actor of the family.")


class ActorsPage(ResponseModel):
    """
    A model representing a page of Actors

    **Fields**:

    * **actors**: `List[Actor]` The list of actors returned from the query.
    """

    actors: List[Actor]
