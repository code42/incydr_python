import logging
import sys
from collections import deque

from requests_toolbelt import user_agent
from requests_toolbelt.sessions import BaseUrlSession
from requests_toolbelt.utils.dump import dump_response

from incydr.__about__ import __version__
from incydr._cases.client import CasesClient
from incydr._core.auth import APIClientAuth
from incydr._core.settings import IncydrSettings
from incydr._file_events.client import FileEventsClient

_base_user_agent = user_agent("incydr", __version__)


class Client:
    """
    The Incydr SDK Client class.

    If `None` is passed to any parameters they will be loaded from environment variables or a .env file in the cwd.

    :param url: The url of your Incydr API gateway. See the `getting started guide`_ to find your API domain based on
        your console login URL.
    :type url: str
    :param api_client_id: The ID of your `Incydr API Client`_.
    :type api_client_id: str
    :param api_client_secret: The Secret for your `Incydr API Client`_.
    :type api_client_secret: str

    .. _getting started guide:
        https://developer.code42.com/api/#section/User-Guides/Get-started
    .. _Incydr API Client:
        https://support.code42.com/Incydr/Admin/Code42_console_reference/API_clients
    """

    cases: CasesClient

    def __init__(
        self,
        url=None,
        api_client_id=None,
        api_client_secret=None,
        user_agent_prefix=None,
    ):
        logging.basicConfig()
        self.settings = IncydrSettings(
            url=url, api_client_id=api_client_id, api_client_secret=api_client_secret
        )
        if self.settings.use_rich and hasattr(sys, "ps1"):
            from rich import pretty

            pretty.install()

        self._request_history = deque(maxlen=self.settings.max_response_history)

        self.session = BaseUrlSession(base_url=self.settings.url)
        if user_agent_prefix:
            user_agent = f"{user_agent_prefix} {_base_user_agent}"
        else:
            user_agent = _base_user_agent
        self.session.headers["User-Agent"] = user_agent
        self.session.auth = APIClientAuth(
            session=self.session,
            api_client_id=self.settings.api_client_id,
            api_client_secret=self.settings.api_client_secret,
        )

        def response_hook(response, *args, **kwargs):
            self.settings.logger.debug(dump_response(response).decode("utf-8"))
            self._request_history.appendleft(response)
            response.raise_for_status()

        self.session.hooks["response"] = [response_hook]

        self.cases = CasesClient(self.session)
        self.file_events = FileEventsClient(self.session)

        self.session.auth.refresh()

    @property
    def request_history(self):
        """List of the last `n` :class:requests.Response objects received, where n=client.settings.max_response_history
        (default=5)
        """
        return list(self._request_history)
