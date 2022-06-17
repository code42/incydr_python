from requests import Session


class TrustedActivitiesClient:
    default_page_size = 100

    def __init__(self, session: Session):
        self._session = session

