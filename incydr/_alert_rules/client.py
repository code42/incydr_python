from itertools import count
from typing import Iterator
from typing import List
from typing import Union

from pydantic import parse_obj_as
from requests import Response

from incydr._alert_rules.models.request import GetRulesRequest
from incydr._alert_rules.models.request import UserRequest
from incydr._alert_rules.models.response import RuleDetails
from incydr._alert_rules.models.response import RuleUsersList


class AlertRulesClient:
    def __init__(self, parent):
        self._parent = parent
        self._v2 = None

    @property
    def v2(self):
        if self._v2 is None:
            self._v2 = AlertRulesV2(self._parent)
        return self._v2


class AlertRulesV2:
    """
    Client for `/v2/alert-rules` and `/v2/alerts/rules` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.alert_rules.v2.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    def get_page(
        self, page_num: int = 0, page_size: int = None, watchlist_id: str = None
    ) -> List[RuleDetails]:
        """
        Get a page of alert rules.

        **Parameters**:

        * **page_num**: `int` - Page number for results, starting at 0.
        * **page_size**: `int` - Max number of results to return for a page.
        * **watchlist_id**: `str` - Watchlist ID to filter for alert rules that are associated with this watchlist.

        **Returns**: A list of [`RuleDetails`][ruledetails-model] objects.
        """

        request = GetRulesRequest(
            PageNumber=page_num,
            PageSize=page_size or self._parent.settings.page_size,
            WatchlistId=watchlist_id,
        )
        response = self._parent.session.get("/v2/alert-rules", params=request.dict())
        return parse_obj_as(List[RuleDetails], response.json())

    def iter_all(
        self, page_size: int = None, watchlist_id: str = None
    ) -> Iterator[RuleDetails]:
        """
        Iterate over all alert rules.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`RuleDetails`][ruledetails-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(0):
            page = self.get_page(
                page_num=page_num, page_size=page_size, watchlist_id=watchlist_id
            )
            yield from page
            if len(page) < page_size:
                break

    def get_rule(self, rule_id: str) -> RuleDetails:
        """
        Get a single alert rule.

        **Parameters**:

        * **rule_id**: `str` (required) - A rule ID.

         **Returns**: A [`RuleDetails`][ruledetails-model] object that contains the details for an alert rule.
        """

        response = self._parent.session.get(f"/v2/alert-rules/{rule_id}")
        return RuleDetails.parse_response(response)

    def enable_rules(self, rule_ids: Union[str, List[str]]) -> Response:
        """
        Enable a single rule or a list of alert rules.

        **Parameters**:

        * **rule_ids**: `str`, `List[str]` (required) - A single rule ID or a list of rule IDs.

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(rule_ids, str):
            return self._parent.session.post(url=f"/v2/alert-rules/{rule_ids}/enable")
        else:
            return self._parent.session.post(
                url="/v2/alert-rules/enable", json=rule_ids
            )

    def disable_rules(self, rule_ids: Union[str, List[str]]) -> Response:
        """
        Disable a single rule or list of alert rules.

        **Parameters**:

        * **rule_ids**: `str`, `List[str]` (required) - A single rule ID or a list of rule IDs.

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(rule_ids, str):
            return self._parent.session.post(url=f"/v2/alert-rules/{rule_ids}/disable")
        else:
            return self._parent.session.post(
                url="/v2/alert-rules/disable", json=rule_ids
            )

    def add_users(
        self,
        rule_id: str,
        users: Union[str, List[str], List[List[str]]],
    ) -> Response:
        """
        Add users to an alert rule. Note that added users could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **users**: `List[str]`, `List[List[str]` (required) - A list of user IDs to add to the rule.  Use lists where the first element is the user ID to add user aliases associated with a given user. Ex: `users=['user-id-1', ['user-id-2', 'user-alias-2']]`

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(users, str):
            users = [users]

        users_list = []

        for user in users:
            if isinstance(user, str):
                users_list.append(
                    UserRequest(userIdFromAuthority=user, aliases=[]).dict()
                )
            else:
                users_list.append(
                    UserRequest(userIdFromAuthority=user[0], aliases=user[1:]).dict()
                )

        return self._parent.session.post(
            url=f"/v2/alert-rules/{rule_id}/users", json=users_list
        )

    def remove_users(self, rule_id: str, users: Union[str, List[str]]) -> Response:
        """
        Remove users from a rule. Note that removed users could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **users**: `str`, `List[str]` (required) - A list of user IDs to remove from the rule.  Will also remove all associated aliases.

        **Returns**: A `requests.Response` indicating success.
        """

        return self._parent.session.post(
            url=f"/v2/alert-rules/{rule_id}/remove-users",
            json=users if isinstance(users, List) else [users],
        )

    def remove_user_aliases(
        self, rule_id: str, user_aliases: Union[str, List[str]]
    ) -> Response:
        """
        Remove user aliases from a rule. Note that removed user aliases could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **user_aliases**: `List[List[str]]` (required) - A list of user IDs with the associated aliases to remove from the rule. Each list should be have the user ID as the first element and desired aliases as the following elements. Ex: `users=[['user-id-1', 'user-alias-1', 'user-alias-12'], ['user-id-2', 'user-alias-2']]`

        **Returns**: A `requests.Response` indicating success.
        """
        users = []

        for user in user_aliases:
            if not isinstance(user, List):
                raise ValueError(
                    "Each user list element should contain the user ID followed by the desired user aliases to remove from the rule."
                )
            users.append(
                UserRequest(userIdFromAuthority=user[0], aliases=user[1:]).dict()
            )

        return self._parent.session.post(
            url=f"/v2/alert-rules/{rule_id}/remove-user-aliases", json=users
        )

    def remove_all_users(self, rule_id: str) -> Response:
        """
        Remove all users from a rule.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.delete(url=f"/v2/alert-rules/{rule_id}/users")

    def get_users(self, rule_id: str) -> RuleUsersList:
        """
        Get all users assigned to a rule.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule.

        **Returns**: A [`RuleUsersList`][ruleuserslist-model] model.
        """
        response = self._parent.session.get(url=f"/v2/alert-rules/{rule_id}/users")
        return RuleUsersList.parse_response(response)
