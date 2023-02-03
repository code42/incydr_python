import base64
import json
import logging
import re
import traceback
from collections import deque
from textwrap import indent

from requests_toolbelt import user_agent
from requests_toolbelt.sessions import BaseUrlSession
from requests_toolbelt.utils.dump import dump_response

from _incydr_sdk.__version__ import __version__
from _incydr_sdk.alert_rules.client import AlertRulesClient
from _incydr_sdk.alerts.client import AlertsClient
from _incydr_sdk.audit_log.client import AuditLogClient
from _incydr_sdk.cases.client import CasesClient
from _incydr_sdk.core.auth import APIClientAuth
from _incydr_sdk.core.settings import IncydrSettings
from _incydr_sdk.customer.client import CustomerClient
from _incydr_sdk.departments.client import DepartmentsClient
from _incydr_sdk.devices.client import DevicesClient
from _incydr_sdk.directory_groups.client import DirectoryGroupsClient
from _incydr_sdk.file_events.client import FileEventsClient
from _incydr_sdk.trusted_activities.client import TrustedActivitiesClient
from _incydr_sdk.user_risk_profiles.client import UserRiskProfiles
from _incydr_sdk.users.client import UsersClient
from _incydr_sdk.watchlists.client import WatchlistsClient

_base_user_agent = user_agent("incydr", __version__)
_auth_header_regex = re.compile(r"Authorization: (Bearer|Basic) \S+")


class Client:
    """
    An HTTP client for interacting with the Code42 Incydr API.

    **Parameters**:

    * **url**: `str` The url of your Incydr API gateway. See the [developer getting started guide](https://developer.code42.com/api/#section/User-Guides/Get-started)
        to find your API domain based on your console login URL.
    * **api_client_id**: `str` The ID of your [Incydr API Client](https://support.code42.com/Incydr/Admin/Code42_console_reference/API_clients)
    * **api_client_secret**: `str` The Secret for your Incydr API Client.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(url="https://api.us.code42.com", api_client_id="<client_id>", api_client_secret="<client_secret>")

    """

    def __init__(
        self,
        url: str = None,
        api_client_id: str = None,
        api_client_secret: str = None,
        skip_auth: bool = False,
        **settings_kwargs,
    ):
        self._settings = IncydrSettings(
            url=url,
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            **settings_kwargs,
        )
        self._request_history = deque(maxlen=self._settings.max_response_history)

        self._session = BaseUrlSession(base_url=self._settings.url)
        self._session.headers["User-Agent"] = (
            self._settings.user_agent_prefix or "" + _base_user_agent
        )
        self._session.auth = APIClientAuth(
            session=self._session,
            api_client_id=self._settings.api_client_id,
            api_client_secret=self._settings.api_client_secret,
        )

        def response_hook(response, *args, **kwargs):
            level = self._settings.log_level
            if level == logging.INFO:
                self._log_response_info(response)
            if level == logging.DEBUG:
                self._log_response_debug(response)

            self._request_history.appendleft(response)
            response.raise_for_status()

        self._session.hooks["response"] = [response_hook]

        self._alerts = AlertsClient(self)
        self._alert_rules = AlertRulesClient(self)
        self._audit_log = AuditLogClient(self)
        self._cases = CasesClient(self)
        self._customer = CustomerClient(self)
        self._departments = DepartmentsClient(self)
        self._devices = DevicesClient(self)
        self._directory_groups = DirectoryGroupsClient(self)
        self._file_events = FileEventsClient(self)
        self._trusted_activities = TrustedActivitiesClient(self)
        self._users = UsersClient(self)
        self._user_risk_profiles = UserRiskProfiles(self)
        self._watchlists = WatchlistsClient(self)

        if not skip_auth:
            self._session.auth.refresh()

    @property
    def tenant_id(self):
        """Property returning the current tenant ID."""
        token = self.session.auth.token_response.access_token.get_secret_value()
        payload = token.encode("ascii").split(b".")[-2]
        extra = len(payload) % 4
        if extra > 0:
            payload += b"=" * (4 - extra)
        return json.loads(base64.urlsafe_b64decode(payload))["tenantUid"]

    @property
    def request_history(self):
        """
        Property returning a list of the last `n` number of [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response)
        objects received, where `n` equals the `client.settings.max_response_history` value (default=5).

        The most recent request is the first item in the list: `client.request_history[0]`
        """
        return list(self._request_history)

    @property
    def settings(self):
        """
        Property returning an [`IncydrSettings`](../settings) object that contains the configuration for this client.
        """
        return self._settings

    @property
    def session(self):
        """
        Property returning the core [`requests.Session`](https://requests.readthedocs.io/en/latest/api/#request-sessions) used to make all
        HTTP requests.

        Contains a hook that prepends the base url of the Code42 API gateway to each request url.

        Usage:

            >>> response = client.session.get("/v1/users")
            >>> response
            <Response [200]>
            >>> response.url
            'https://api.us.code42.com/v1/users'
        """
        return self._session

    @property
    def alerts(self):
        """
        Property returning an [`AlertsClient`](../alerts) for interacting with
        `/v*/alerts` API endpoints.
        Usage:
            >>> client.alerts.v1.get_page()
        """
        return self._alerts

    @property
    def alert_rules(self):
        """
        Property returning a [`AlertRules`](../alert_rules) for interacting with `/v*/alert-rules` and `/v*/alerts/rules* API endpoints.

        Usage:

            >>> client.alert_rules.v1.add_users(rule_id='test', users=['user-id-1', 'user-id-2'])

        """
        return self._alert_rules

    @property
    def audit_log(self):
        """
        Property returning an [`AuditLogClient`](../audit_log) for interacting with
        `/v*/audit` API endpoints.
        Usage:
            >>> client.audit_log.v1.get_page()
        """
        return self._audit_log

    @property
    def cases(self):
        """
        Property returning a [`CasesClient`](../cases) for interacting with `/v*/cases` API endpoints.

        Usage:

            >>> client.cases.v1.create(name="Test", description="My Description")

        """
        return self._cases

    @property
    def customer(self):
        """
        Property returning a [`CustomerClient`](../customer) for interacting with `/v*/customer` API endpoints.

        Usage:

            >>> client.customer.v1.get()

        """
        return self._customer

    @property
    def departments(self):
        """
        Property returning a [`DepartmentsClient`](../departments) for interacting with `/v*/departments` API endpoints.
        Usage:

            >>> client.departments.v1.get_page()

        """
        return self._departments

    @property
    def devices(self):
        """
        Property returning a [`DevicesClient`](../devices) for interacting with `/v*/devices` API endpoints.
        Usage:

            >>> client.devices.v1.get_page(active=True)

        """
        return self._devices

    @property
    def directory_groups(self):
        """
        Property returning a [`DirectoryGroupsClient`](../directory_groups) for interacting with `/v*/directory-groups` API endpoints.
        Usage:

            >>> client.directory_groups.v1.get_page()

        """
        return self._directory_groups

    @property
    def file_events(self):
        """
        Property returning a [`FileEventsClient`](../file_events) for interacting with `/v*/file-events` API endpoints.
        Usage:

            >>> from incydr import EventQuery
            >>> query = EventQuery(start_date='P30D').equals('file.category', 'Document')

            >>> client.file_events.v2.search(query)

        """
        return self._file_events

    @property
    def trusted_activities(self):
        """
        Property returning a [`TrustedActivitiesClient`](../trusted_activities) for interacting with
        `/v*/trusted-activities` API endpoints.

        Usage:

            >>> client.trusted_activities.v2.get_page()

        """
        return self._trusted_activities

    @property
    def users(self):
        """
        Property returning a [`UsersClient`](../users) for interacting with `/v*/users` API endpoints.
        Usage:

            >>> client.users.v1.get_page(active=True)

        """
        return self._users

    @property
    def user_risk_profiles(self):
        """
        Property returning a [`UserRiskProfilesClient`](../user_risk_profiles) for interacting with
        `/v*/user_risk_profiles` API endpoints.

        Usage:

            >>> client.user_risk_profiles.v1.get_user_risk_profile("23")

        """
        return self._user_risk_profiles

    @property
    def watchlists(self):
        """
        Property returning a [`WatchlistsClient`](../watchlists) for interacting with `/v*/watchlists` API endpoints.
        Usage:

            >>> client.watchlists.v1.get_page()
        """
        return self._watchlists

    def _log_response_info(self, response):
        self._settings.logger.info(
            f"{response.request.method} {response.request.url} status_code={response.status_code}"
        )

    def _log_response_debug(self, response):
        try:
            dumped = dump_response(
                response, request_prefix=b"", response_prefix=b""
            ).decode("utf-8")
            dumped = re.sub(
                _auth_header_regex,
                "Authorization: <token_redacted>",
                dumped,
            )
            if not self._settings.use_rich:
                dumped = indent(dumped, prefix="\t")
            self._settings.logger.debug(dumped)
        except Exception as err:
            self._settings.logger.debug(f"Error dumping request/response info: {err}")
            self._settings.logger.debug(response)

    def _log_error(self, err, invocation_str=None):
        message = str(err) if err else None
        if invocation_str:
            message = f"Exception occurred from input: '{invocation_str}'.\n" + message
        if message:
            self._settings.logger.error(message)

    def _log_verbose_error(self, invocation_str=None, http_request=None):
        """For logging traces, invocation strs, and request parameters during exceptions to the
        error log file."""
        prefix = (
            "Exception occurred."
            if not invocation_str
            else f"Exception occurred from input: '{invocation_str}'."
        )
        message = f"{prefix}. See error below."
        self._log_error(message)
        self._log_error(traceback.format_exc())
        if http_request:
            self._log_error(f"Request parameters: {http_request.body}")
