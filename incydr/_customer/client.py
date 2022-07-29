from .models import Customer


class CustomerClient:
    def __init__(self, session):
        self._session = session
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = CustomerV1(self._session)
        return self._v1


class CustomerV1:
    """Customer V1 Client"""

    def __init__(self, session):
        self._session = session

    def get(self) -> Customer:
        """Get customer account information."""
        response = self._session.get("/v1/customer")
        return Customer(**response.json())
