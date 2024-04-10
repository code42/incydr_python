from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class QueryActorsRequest(BaseModel):
    nameStartsWith: Optional[str]
    nameEndsWith: Optional[str]
    active: Optional[bool]
    pageSize: Optional[int]
    page: Optional[int]


class Actor(ResponseModel):
    """
    A model representing an Actor.

    **Fields**:

    * **active**: `bool` Whether or not the actor is active.
    * **actor_id**: `str` The unique ID of the actor.
    * **alternate_names**: `List[str]`
    * **country**: `str` The actor's country.
    * **department**: `str` The actor's department.
    * **division**: `str` The actor's division.
    * **employee_type**: `str` The actor's employment type.
    * **first_name**: `str` The first (given) name of the actor.
    * **in_scope**: `str` TODO
    * **last_name**: `str` The last (family) name of the actor.
    * **locality**: `str` - The actor's locality (city)
    * **manager_actor_id**: `str` The actor ID of the actor's manager.
    * **name**: `str` The actor's (eg. full username/email) name.
    * **parentActorId**: `str` The actor ID of this actor's parent actor. (if the actor has a parent).
    * **region**: `str` The actor's region (state).
    * **title**: `str` The actor's job title.
    """

    active: Optional[bool]
    actor_id: Optional[str] = Field(alias="actorId")
    alternate_names: Optional[List[str]] = Field(alias="alternateNames")
    country: Optional[str]
    department: Optional[str]
    division: Optional[str]
    employee_type: Optional[str] = Field(alias="employeeType")
    first_name: Optional[str] = Field(alias="firstName")
    in_scope: Optional[bool] = Field(alias="inScope")
    last_name: Optional[str] = Field(alias="lastName")
    locality: Optional[str]
    manager_actor_id: Optional[str] = Field(alias="managerActorId")
    name: Optional[str]
    parentActorId: Optional[str]
    region: Optional[str]
    title: Optional[str]


class ActorFamily(ResponseModel):
    """
    A model representing an actor family.

    An actor family consists of one or more child actors adopted by a single parent. If an actor is not associated with
    any other actors, the family consists of only the single actor.

    **Fields**:

    * **children**: `List[[Actor][actor-model]]` The list of child actors associated with the parent.
    * **parent**: `[Actor][actor-model]` The parent actor of the family.
    """

    children: List[Actor]
    parent: Actor


class ActorsPage(ResponseModel):
    """
    A model representing a page of Actors

    **Fields**:

    * **actors**: `List[str]` The list of actors returned from the query.
    """

    actors: List[Actor]


class ActorAdoption(ResponseModel):
    """
    A model representing the result of an actor adoption.

    **Fields**:

    * **child_actor_ids**: `List[str]`
    * **parent_actor_id**: `str`
    """

    child_actor_ids: List[str] = Field(alias="childActorIds")
    parent_actor_id: str = Field(alias="parentActorId")
