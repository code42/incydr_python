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
    """
    Client for `/v1/customer` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.customer.v1.get()
    """

    def __init__(self, session):
        self._session = session

    def get(self) -> Customer:
        """
        Get customer account information.

        Returns: A [`Customer`](../models/#customer) object representing account information.

        """
        response = self._session.get("/v1/customer")
        return Customer.parse_response(response)
