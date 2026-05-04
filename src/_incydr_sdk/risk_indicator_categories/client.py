from _incydr_sdk.enums import SortDirection
from _incydr_sdk.risk_indicator_categories.models import (
    RiskIndicatorCategoriesResponsePage,
)
from _incydr_sdk.risk_indicator_categories.models import RiskIndicatorCategory
from _incydr_sdk.risk_indicator_categories.models import RiskIndicatorSubcategory


class RiskIndicatorCategories:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = RiskIndicatorCategoriesV1(self._parent)
        return self._v1


class RiskIndicatorCategoriesV1:
    """
    Client for `/v1/risk-indicator-categories` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.risk_indicators.v1.list_categories()
    """

    def __init__(self, parent):
        self._parent = parent

    def list_categories(
        self, active: bool = None, sort_direction: SortDirection = None
    ) -> RiskIndicatorCategoriesResponsePage:
        """
        Returns all risk indicator categories, including their subcategories and associated risk indicators.
        Filter results by passing the appropriate parameters:

        **Parameters**:

        * **active**: `bool` - When provided, returns only those risk indicators which match the provided value (true or false). When not provided, returns both.
        * **sort_direction**: `SortDirection` - The order in which to sort the returned list.

        **Returns**: A [`RiskIndicatorCategoriesResponsePage`][riskindicatorcategoriesresponsepage-model] object.
        """
        response = self._parent.session.get(
            "/v1/risk-indicator-categories",
            params={"isActive": active, "sort_direction": sort_direction},
        )
        return RiskIndicatorCategoriesResponsePage.parse_response(response)

    def get_category(self, id: str) -> RiskIndicatorCategory:
        """
        Returns a single risk indicator category, including its subcategories and associated risk indicators.

        **Parameters**:

        * **id**: `str` - The unique ID of the category you wish to retrieve.

        **Returns**: A [`RiskIndicatorCategory`][riskindicatorcategory-model] object.
        """
        response = self._parent.session.get(f"/v1/risk-indicator-categories/{id}")
        return RiskIndicatorCategory.parse_response(response)

    def get_subcategory(
        self, category_id: str, subcategory_id: str
    ) -> RiskIndicatorSubcategory:
        """
        Returns a single risk indicator category, including its subcategories and associated risk indicators.

        **Parameters**:

        * **category_id**: `str` - The unique ID of the category in which the subcategory lives.
        * **subcategory_id**: `str` - The unique ID of the subcategory you wish to retrieve.

        **Returns**: A [`RiskIndicatorSubcategory`][riskindicatorsubcategory-model] object.
        """
        response = self._parent.session.get(
            f"/v1/risk-indicator-categories/{category_id}/subcategories/{subcategory_id}"
        )
        return RiskIndicatorSubcategory.parse_response(response)
