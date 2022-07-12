import logging
from collections import deque

from requests_toolbelt.sessions import BaseUrlSession
from requests_toolbelt.utils.dump import dump_response

from incydr._cases.client import CasesClient
from incydr._core.auth import APIClientAuth
from incydr._core.settings import IncydrSettings
from incydr._file_events.client import FileEventsV1
from incydr._trusted_activities.client import TrustedActivitiesClient


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
    trusted_activities: TrustedActivitiesClient
    file_events: FileEventsV1

    def __init__(self, url=None, api_client_id=None, api_client_secret=None):
        logging.basicConfig()
        self.settings = IncydrSettings(
            url=url, api_client_id=api_client_id, api_client_secret=api_client_secret
        )
        self._request_history = deque(maxlen=self.settings.max_response_history)

        self.session = BaseUrlSession(base_url=self.settings.url)
        self.session.auth = APIClientAuth(
            session=self.session,
            api_client_id=self.settings.api_client_id,
            api_client_secret=self.settings.api_client_secret,
        )

        def response_hook(response, *args, **kwargs):
            self.settings.logger.debug(dump_response(response).decode("utf-8"))
            self._request_history.append(response)
            response.raise_for_status()

        self.session.hooks["response"] = [response_hook]

        self.cases = CasesClient(self.session)
        self.trusted_activities = TrustedActivitiesClient(self.session)
        self.file_events = FileEventsV1(self.session)

    @property
    def request_history(self):
        """List of the last `n` :class:requests.Response objects received, where n=client.settings.max_response_history
        (default=5)
        """
        return list(self._request_history)
