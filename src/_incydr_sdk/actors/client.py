from datetime import datetime
from itertools import count
from typing import Union

import requests

from ..exceptions import IncydrException
from .models import Actor
from .models import ActorFamily
from .models import ActorsPage
from .models import QueryActorsRequest
from _incydr_sdk.exceptions import DateParseError
from _incydr_sdk.queries.utils import DATE_STR_FORMAT


class ActorsV1:
    """
    Client for `/v1/actors` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.actors.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_page(
        self,
        active: bool = None,
        name_starts_with: str = None,
        name_ends_with: str = None,
        page_num: int = 1,
        page_size: int = 500,
        prefer_parent: bool = False,
    ) -> ActorsPage:
        """
        Get a page of actors.

        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **active**: `bool` - Find actors with the given active state. When `True`, returns only active actors. When `False` returns only inactive actors. Defaults to `None`, returning both.
        * **name_starts_with**: `str` - Find actors whose name (e.g. username/email) starts with this text, ignoring case.
        * **name_ends_with**: `str` - Find actors whose name (e.g. username/email) ends with this text, ignoring case.
        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return per page. Must be between 1 and 500. Defaults to 500.
        * **prefer_parent**: `bool` = Returns an actor's parent when applicable. Returns an actor themselves if they have no parent.

        **Returns**: An [`Actor`][actor-model] object representing the actor.
        """
        request_path = "/v1/actors/actor/search"

        if prefer_parent:
            request_path += "/parent"

        data = QueryActorsRequest(
            nameStartsWith=name_starts_with,
            nameEndsWith=name_ends_with,
            active=active,
            pageSize=page_size,
            page=page_num,
        )

        response = self._parent.session.get(request_path, params=data.dict())
        return ActorsPage.parse_response(response)

    def iter_all(
        self,
        active: bool = None,
        name_starts_with: str = None,
        name_ends_with: str = None,
        page_size: int = 500,
        prefer_parent: bool = False,
    ) -> ActorsPage:
        """
        Iterate over all actors.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Actor`][actor-model] objects.
        """
        for page_num in count(1):
            page = self.get_page(
                active=active,
                name_starts_with=name_starts_with,
                name_ends_with=name_ends_with,
                page_size=page_size,
                page_num=page_num,
                prefer_parent=prefer_parent,
            )
            yield from page.actors
            if len(page.actors) < page_size:
                break

    def get_actor_by_id(self, actor_id: str, prefer_parent: bool = False) -> Actor:
        """
        Get an actor by their actor ID.

        **Parameters**:

        * **actor_id**: `str` (required) - Unique ID for the actor.
        * **prefer_parent**: `str` - Returns an actor's parent when applicable. Returns an actor themselves if they have no parent.

        **Returns**: An [`Actor`][actor-model] object representing the actor.
        """
        request_path = f"/v1/actors/actor/id/{actor_id}"
        if prefer_parent:
            request_path += "/parent"

        try:
            response = self._parent.session.get(request_path)
            return Actor.parse_response(response)
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise ActorNotFoundError

    def get_actor_by_name(self, name: str, prefer_parent: bool = True) -> Actor:
        """
        Get an actor by their name.

        **Parameters**:

        * **name**: `str` (required) - The actor name.
        * **prefer_parent**: `str` - Returns an actor's parent when applicable. Returns an actor themselves if they have no parent. Defaults to True.

        **Returns**: An [`Actor`][actor-model] object representing the actor.
        """
        if prefer_parent:
            try:
                response = self._parent.session.get(
                    f"/v1/actors/actor/name/{name}/parent"
                )
                return Actor.parse_response(response)
            except requests.HTTPError as err:
                if err.response.status_code == 404:
                    raise ActorNotFoundError
        else:
            matches = self.get_page(name_starts_with=name)
            for actor in matches.actors:
                if actor.name == name:
                    actor_profile = self._parent.session.get(
                        f"/v1/actors/actor/id/{actor.actor_id}"
                    )
                    return Actor.parse_response(actor_profile)
            raise ActorNotFoundError(name)

    def get_family_by_member_id(self, actor_id: str) -> ActorFamily:
        """
        Get an actor family from the actor ID of any family member.

        **Parameters**:

        * **actor_id**: `str` (required) - Unique ID for an actor.

        **Returns**: An [`Actor Family`][actor-family-model] object representing the family of actors.
        """
        try:
            response = self._parent.session.get(
                f"/v1/actors/actor/id/{actor_id}/family"
            )
            return ActorFamily.parse_response(response)
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise ActorNotFoundError

    def get_family_by_member_name(self, name: str) -> ActorFamily:
        """
        Get an actor family from the name of any family member.

        **Parameters**:

        * **name**: `str` (required) - Name of an actor.

        **Returns**: An [`ActorFamily`][actor-family-model] object representing the family of actors.
        """
        try:
            response = self._parent.session.get(f"/v1/actors/actor/name/{name}/family")
            return ActorFamily.parse_response(response)
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise ActorNotFoundError(name)

    def update_actor(
        self,
        actor: Union[Actor, str],
        notes: str = None,
        start_date: Union[datetime, str] = None,
        end_date: Union[datetime, str] = None,
    ) -> Actor:
        """
        Update an actor.

        **Parameters**:

        Either:

        * **actor**: `str` (required) - Unique ID for an actor.
        * **notes**: `str` - Additional notes for the risk profile. Pass an empty string to clear the field.
        * **start_date**: `datetime` - The starting date for the user. Accepts a datetime object or a string in the format yyyy-MM-dd (UTC) format. Pass an empty string to clear the field.
        * **end_date**: `datetime` - The departure date for the user.  Accepts a datetime object or a string in the format yyyy-MM-dd (UTC) format.  Pass an empty string to clear the field.

        Or:

        * **actor**: An [`Actor`][actor-model] object representing the actor.

        **Returns**: An [`Actor`][actor-model] object representing the actor.
        """
        if isinstance(actor, Actor):
            return self._update_actor_from_actor(actor)
        elif notes is None and start_date is None and end_date is None:
            raise IncydrException(
                "Must provide at least one of notes or start_date or end_date arguments."
            )
        else:
            return self._update_actor_from_args(
                actor_id=actor, start_date=start_date, end_date=end_date, notes=notes
            )

    def _update_actor_from_actor(self, actor: Actor) -> Actor:
        try:
            response = self._parent.session.patch(
                f"/v1/actors/actor/id/{actor.actor_id}",
                json={
                    "notes": actor.notes,
                    "startDate": actor.start_date,
                    "endDate": actor.end_date,
                },
            )
            return Actor.parse_response(response)
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise ActorNotFoundError(actor.actor_id)

    def _update_actor_from_args(
        self,
        actor_id: str,
        notes: str = None,
        start_date: Union[datetime, str] = None,
        end_date: Union[datetime, str] = None,
    ) -> Actor:
        request_body = {}
        if notes is not None:
            request_body["notes"] = None if notes == "" else notes
        if start_date is not None:
            request_body["startDate"] = (
                None if start_date == "" else _create_date(start_date)
            )
        if end_date is not None:
            request_body["endDate"] = None if end_date == "" else _create_date(end_date)
        try:
            response = self._parent.session.patch(
                f"/v1/actors/actor/id/{actor_id}", json=request_body
            )
            return Actor.parse_response(response)
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise ActorNotFoundError(actor_id)


class ActorsClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = ActorsV1(self._parent)
        return self._v1


class ActorNotFoundError(IncydrException):
    """Raised when a watchlist with the matching type or title is not found."""

    def __init__(self, identifier=None):
        self.identifier = identifier
        self.message = (
            (f"Actor Not Found Error: No results for actors matching '{identifier}'.")
            if identifier
            else "Actor Not Found Error: No results for specified actor(s)."
        )
        super().__init__(self.message)


def _create_date(date: Union[datetime, str]):
    if not isinstance(date, datetime):
        try:
            date = datetime.strptime(date, DATE_STR_FORMAT)
        except ValueError:
            raise DateParseError(
                date,
                msg=f"DateParseError: Error parsing time data. Date '{date}' does not match format {DATE_STR_FORMAT}.",
            )
    return date.strftime(DATE_STR_FORMAT)
