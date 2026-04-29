from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel


class RiskIndicator(Model):
    """
    A model representing a Risk Indicator.

    **Fields**:

    * **id**: `str` - The unique ID of the indicator.
    * **name**: `str` - The name of the indicator.
    * **description**: `Optional[str]` - The description of the indicator.
    """

    id: str
    name: str
    description: Optional[str] = None


class RiskIndicatorSubcategory(ResponseModel):
    """
    A model representing a Risk Indicator Subcategory.

    **Fields**:

    * **id**: `str` - The unique ID of the subcategory.
    * **name**: `str` - The name of the subcategory.
    * **description**: `Optional[str]` - The description of the subcategory.
    * **standard_indicators**: `List[RiskIndicator]` - A list of standard risk indicators.
    * **custom_indicators**: `List[RiskIndicator]` - A list of custom risk indicators.
    """

    id: str
    name: str
    description: Optional[str] = None
    standard_indicators: List[RiskIndicator] = Field([], alias="standardIndicators")
    custom_indicators: List[RiskIndicator] = Field([], alias="customIndicators")


class RiskIndicatorCategory(ResponseModel):
    """
    A model representing a Risk Indicator Category.

    **Fields**:

    * **id**: `str` - The unique ID of the category.
    * **name**: `str` - The name of the category.
    * **description**: `Optional[str]` - The description of the category.
    * **subcategories**: `List[RiskIndicatorSubcategory]` - A list of Risk Indicator Subcategories
    """

    id: str
    name: str
    description: Optional[str] = None
    subcategories: List[RiskIndicatorSubcategory]


class RiskIndicatorCategoriesResponsePage(ResponseModel):
    """
    A model representing a page of Risk Indicator Categories.

    **Fields**:

    * **categories**: `Optional[List[RiskIndicatorCategory]]` - A list of Risk Indicator Categories.
    """

    categories: Optional[List[RiskIndicatorCategory]] = Field(
        None, description="A list of Risk Indicator Categories."
    )
