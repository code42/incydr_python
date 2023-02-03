from itertools import count
from typing import Iterator
from typing import List
from typing import Union

from pydantic import parse_obj_as
from requests import HTTPError
from requests import Response

from _incydr_sdk.alert_rules.models.request import GetRulesRequest
from _incydr_sdk.alert_rules.models.response import RuleDetails
from _incydr_sdk.alert_rules.models.response import RuleUsersList
from _incydr_sdk.exceptions import IncydrException
from _incydr_sdk.user_risk_profiles.models import UserRiskProfile


class MissingUsernameCriterionError(IncydrException):
    """An error raised if an alert rule has no username filter."""

    def __init__(self, rule_id):
        super().__init__(
            f"Missing Username Criterion Error: Rule '{rule_id}' has no username filter."
        )


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

        Raises a `MissingUsernameCriterionError` if the rule doesn't have a username filter.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule.

        **Returns**: A [`RuleUsersList`][ruleuserslist-model] model.
        """
        try:
            response = self._parent.session.get(url=f"/v2/alert-rules/{rule_id}/users")
        except HTTPError as e:
            # This endpoint doesn't have query params or a request body, so it should
            # only return a 400 if there is not username filter for the rule.
            if e.response.status_code == 400:
                raise MissingUsernameCriterionError(rule_id)
            raise e
        return RuleUsersList.parse_response(response)

    def _get_user_aliases(self, user_id):
        response = self._parent.session.get(f"/v1/user-risk-profiles/{user_id}")
        profile = UserRiskProfile.parse_response(response)
        return profile.cloud_aliases
