import logging
from collections import deque

from requests_toolbelt import user_agent
from requests_toolbelt.sessions import BaseUrlSession
from requests_toolbelt.utils.dump import dump_response

from incydr.__about__ import __version__
from incydr._cases.client import CasesClient
from incydr._core.auth import APIClientAuth
from incydr._core.settings import IncydrSettings
from incydr._customer.client import CustomerClient
from incydr._devices.client import DevicesClient
from incydr._file_events.client import FileEventsClient
from incydr._watchlists.client import WatchlistsClient

_base_user_agent = user_agent("incydr", __version__)


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
    ):
        self._settings = IncydrSettings(
            url=url, api_client_id=api_client_id, api_client_secret=api_client_secret
        )
        if self._settings.use_rich:
            from rich import pretty

            pretty.install()

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
            if self._settings.log_level < logging.INFO:
                try:
                    dumped = dump_response(response).decode("utf-8")
                    self._settings.logger.debug(dumped)
                except Exception as err:
                    self._settings.logger.debug(
                        f"Error dumping request/response info: {err}"
                    )
                    self._settings.logger.debug(response)

            self._request_history.appendleft(response)
            response.raise_for_status()

        self._session.hooks["response"] = [response_hook]

        self._cases = CasesClient(self)
        self._customer = CustomerClient(self.session)
        self._file_events = FileEventsClient(self)
        self._devices = DevicesClient(self)
        self._watchlists = WatchlistsClient(self)

        self._session.auth.refresh()

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
    def devices(self):
        """
        Property returning a [`DevicesClient`](../devices) for interacting with `/v*/devices` API endpoints.
        Usage:

            >>> client.devices.v1.get_page(active=True)

        """
        return self._devices

    @property
    def watchlists(self):
        """
        Property returning a ['WatchlistsClient'](../watchlists) for interacting with `/v*/watchlists` API endpoints.
        Usage:

            >>> client.watchlists.v1.get_page()
        """
        return self._watchlists
