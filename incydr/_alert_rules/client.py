from datetime import datetime
from typing import List
from typing import Union

from incydr._alert_rules.models.request import GetRulesRequest
from incydr._alert_rules.models.request import UpdateRulesRequest
from incydr._alert_rules.models.request import UpdateUserIdsRequest
from incydr._alert_rules.models.request import UpdateUsersRequest
from incydr._alert_rules.models.request import UserRequest
from incydr._alert_rules.models.response import AssignedUser
from incydr._alert_rules.models.response import AssignedUsersList
from incydr._alert_rules.models.response import CloudSharePermissionsRuleDetailsList
from incydr._alert_rules.models.response import EndpointExfiltrationRuleDetailsList
from incydr._alert_rules.models.response import FileNameRuleDetailsList
from incydr._alert_rules.models.response import FileTypeMismatchRuleDetailsList
from incydr._queries.alert_rules import Filter
from incydr._queries.alert_rules import FilterGroup
from incydr._queries.alert_rules import Query
from incydr.enums import SortDirection


class AlertRulesClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = AlertRulesV1(self._parent)
        return self._v1


class AlertRulesV1:
    """
    Client for `/v1/alert-rules` and `/v1/alerts/rules` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.alert_rules.v1.get_page()
    """

    def __init__(self, parent):
        self._parent = parent

    # TODO - complete with the alerts client?
    def get_page(
        self,
        rule_type: str = None,
        name: str = None,
        description: str = None,
        is_enabled: bool = None,
        modified_at: datetime = None,
        modified_by: str = None,
        created_at: datetime = None,
        created_by: str = None,
        page_num: int = 0,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: str = "CreatedAt",
    ):
        """
        Get a page of alert rules.

        Filter results by passing appropriate parameters:

        **Parameters**:

        * rule_type**:
        * **rule_type**: `str` -
        * **name**: `str` -
        * **description**: `str` -
        * **is_enabled**: `bool` -
        * **modified_at**: `datetime` -
        * **modified_by**: `str` -
        * **created_at**: `datetime` -
        * **created_by**: `str` -
        * **page_num**: `int` - Page number for results, starting at 0.
        * **page_size**: `int` - Max number of results to return for a page.
        * **sort_dir**: `SortDirection` - The direction on which to sort the response, based on the corresponding key.
        * **sort_key**: `str` - One or more values on which the response will be sorted. Defaults to `'CreatedAt'`

        **Returns**:
        """
        query = Query(
            tenantId=self._parent.tenant_id,
            pgNum=page_num,
            pgSize=page_size or self._parent.settings.page_size,
            srtDirection=sort_dir,
            srtKey=sort_key,
            groups=[],
        )

        # create filters
        group = FilterGroup(filters=[])
        if rule_type:
            group.filters.append(Filter(term="Type", operator="IS", value=rule_type))
        if name:
            group.filters.append(Filter(term="Name", operator="IS", value=name))
        if description:
            group.filters.append(
                Filter(term="Description", operator="CONTAINS", value=description)
            )
        if is_enabled:
            group.filters.append(
                Filter(term="IsEnabled", operator="IS", value=is_enabled)
            )
        if modified_at:
            group.filters.append(
                Filter(term="ModifiedAt", operator="ON_OR_AFTER", value=modified_at)
            )
        if modified_by:
            group.filters.append(
                Filter(term="ModifiedBy", operator="IS", value=modified_by)
            )
        if created_at:
            group.filters.append(
                Filter(term="CreatedAt", operator="ON_OR_AFTER", value=created_at)
            )
        if created_by:
            group.filters.append(
                Filter(term="CreatedBy", operator="IS", value=created_by)
            )

        query.groups.append(group)

        return self._parent.session.post(
            url="/v1/alerts/rules/query-rule-metadata", json=query.dict()
        )

    # TODO - complete with the alerts client?
    def get_rule(self, rule_id: str):
        """
        Get a single rule.

        **Parameters**:

        * **rule_id**: `str` (required) - A rule ID.

         **Returns**:
        """

        # create filter
        query = Query(
            tenantId=self._parent.tenant_id,
            groups=[],
        )
        group = FilterGroup(filters=[])
        group.filters.append(
            Filter(term="RuleMetadataId", operator="IS", value=rule_id)
        )
        query.groups.append(group)

        return self._parent.session.post(
            url="/v1/alerts/rules/query-rule-metadata", json=query.dict()
        )

    def update_rules(self, rule_ids: Union[str, List[str]], enabled: bool):
        """
        Enable or disable a list of rules.

        **Parameters**:

        * **rule_ids**: `str`, `List[str]` (required) - A list of rule IDs.
        * **enabled**: `bool` (required) - What to set the rule's enabled field. `True` to enable a set of rules, `False` to disable a set of rules.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateRulesRequest(
            tenantId=self._parent.tenant_id,
            ruleIds=rule_ids if isinstance(rule_ids, List) else [rule_ids],
            isEnabled=enabled,
        )
        return self._parent.session.post(
            url="/v1/alert-rules/update-is-enabled", json=data.dict()
        )

    def add_users(
        self,
        rule_id: str,
        users: Union[str, List[str], List[List[str]]],
    ):
        """
        Add users to a rule. Note that added users could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **users**: `List[str]`, `List[List[str]` (required) - A list of user IDs to add to the rule.  Use lists where the first element is the user ID to add user aliases associated with a given user. Ex: `users=['user-id-1', ['user-id-2', 'user-alias-2']]`

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateUsersRequest(
            tenantId=self._parent.tenant_id, ruleId=rule_id, userList=[]
        )
        if not isinstance(users, List):  # handle users passing a single ID
            users = [users]

        for user in users:
            if isinstance(user, str):
                data.userList.append(
                    UserRequest(userIdFromAuthority=user, userAliasList=[])
                )
            else:
                data.userList.append(
                    UserRequest(userIdFromAuthority=user[0], userAliasList=user[1:])
                )

        return self._parent.session.post(
            url="/v1/alert-rules/add-users", json=data.dict()
        )

    def remove_users(self, rule_id: str, users: Union[str, List[str]]):
        """
        Remove users from a rule. Note that removed users could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **users**: `str`, `List[str]` (required) - A list of user IDs to remove from the rule.  Will also remove all associated aliases.

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateUserIdsRequest(
            tenantId=self._parent.tenant_id,
            ruleId=rule_id,
            userIdList=users if isinstance(users, List) else [users],
        )
        return self._parent.session.post(
            url="/v1/alert-rules/remove-users", json=data.dict()
        )

    def remove_user_aliases(self, rule_id: str, user_aliases: Union[str, List[str]]):
        """
        Remove user aliases from a rule. Note that removed user aliases could become either included included or excluded from the rule, depending on the rule's configuration.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.
        * **user_aliases**: `List[List[str]]` (required) - A list of user IDs with the associated aliases to remove from the rule. Each list should be have the user ID as the first element and desired aliases as the following elements. Ex: `users=[['user-id-1', 'user-alias-1', 'user-alias-12'], ['user-id-2', 'user-alias-2']]`

        **Returns**: A `requests.Response` indicating success.
        """
        data = UpdateUsersRequest(
            tenantId=self._parent.tenant_id,
            ruleId=rule_id,
            userList=[],
        )

        for user in user_aliases:
            if not isinstance(user, List):
                raise ValueError(
                    "Each user list element should contain the user ID followed by the desired user aliases to remove from the rule."
                )
            data.userList.append(
                UserRequest(userIdFromAuthority=user[0], userAliasList=user[1:])
            )

        return self._parent.session.post(
            url="/v1/alert-rules/remove-user-aliases", json=data.dict()
        )

    def remove_all_users(self, rule_id: str):
        """
        Remove all users from a rule.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule to update.

        **Returns**: A `requests.Response` indicating success.
        """
        data = {"tenantId": self._parent.tenant_id, "ruleId": rule_id}
        return self._parent.session.post(
            url="/v1/alert-rules/remove-all-users", json=data
        )

    def get_users(self, rule_id: str) -> AssignedUsersList:
        """
        Get all users assigned to a rule.

        **Parameters**:

        * **rule_id**: `str` (required) - The ID of the rule.

        **Returns**: An [`AssignedUsersList`][assigneduserslist-model] model.
        """
        data = {"tenantId": self._parent.tenant_id, "ruleId": rule_id}
        response = self._parent.session.post(
            url="/v1/alert-rules/query-users", json=data
        )
        return AssignedUsersList.parse_response(response)

    def get_details_cloud_share_permissions_rules(
        self, rule_ids: Union[str, List[str]]
    ) -> CloudSharePermissionsRuleDetailsList:
        """
        Get details about a set of Cloud Share Permissions rules.

        **Parameters**:

        * **rule_id**: `str` (required) - A list of rule IDs.

        **Returns**: A [`CloudSharePermissionsRuleDetailsList`][cloudsharepermissionsruledetailslist-model] model.
        """

        data = GetRulesRequest(
            tenantId=self._parent.tenant_id,
            ruleIds=rule_ids if isinstance(rule_ids, List) else [rule_ids],
        )
        response = self._parent.session.post(
            url="/v1/alert-rules/query-cloud-share-permissions-rule", json=data.dict()
        )
        return CloudSharePermissionsRuleDetailsList.parse_response(response)

    def get_details_endpoint_exfiltration_rules(
        self, rule_ids: Union[str, List[str]]
    ) -> EndpointExfiltrationRuleDetailsList:
        """
        Get details about a set of Endpoint Exfiltration rules.

        **Parameters**:

        * **rule_id**: `str` (required) - A list of rule IDs.

        **Returns**: An [`EndpointExfiltrationRuleDetailsList`][endpointexfiltrationruledetailslist-model] model.
        """

        data = GetRulesRequest(
            tenantId=self._parent.tenant_id,
            ruleIds=rule_ids if isinstance(rule_ids, List) else [rule_ids],
        )
        response = self._parent.session.post(
            url="/v1/alert-rules/query-endpoint-exfiltration-rule", json=data.dict()
        )
        return EndpointExfiltrationRuleDetailsList.parse_response(response)

    def get_details_file_type_mismatch_rules(
        self, rule_ids: Union[str, List[str]]
    ) -> FileTypeMismatchRuleDetailsList:
        """
        Get details about a set of File Type Mismatch rules.

        **Parameters**:

        * **rule_id**: `str` (required) - A list of rule IDs.

        **Returns**: A ][`FileTypeMismatchRuleDetailsList`][filetypemismatchruledetailslist-model] model.
        """

        data = GetRulesRequest(
            tenantId=self._parent.tenant_id,
            ruleIds=rule_ids if isinstance(rule_ids, List) else [rule_ids],
        )
        response = self._parent.session.post(
            url="v1/alert-rules/query-file-rule-type-mismatch-rule", json=data.dict()
        )
        return FileTypeMismatchRuleDetailsList.parse_response(response)

    def get_details_file_name_rules(
        self, rule_ids: Union[str, List[str]]
    ) -> FileNameRuleDetailsList:
        """
        Get details about a set of File Name rules.

        **Parameters**:

        * **rule_id**: `str` (required) - A list of rule IDs.

        **Returns**: A [`FileNameRuleDetailsList`][filenameruledetailslist-model] model.
        """

        data = GetRulesRequest(
            tenantId=self._parent.tenant_id,
            ruleIds=rule_ids if isinstance(rule_ids, List) else [rule_ids],
        )
        response = self._parent.session.post(
            url="/v1/alert-rules/query-file-name-rule", json=data.dict()
        )
        return FileNameRuleDetailsList.parse_response(response)
