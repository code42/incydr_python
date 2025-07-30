from typing import Optional

from pydantic import ConfigDict
from pydantic import Field

from _incydr_sdk.core.models import ResponseModel


class Customer(ResponseModel):
    """
    A model providing details of an Incydr customer account.

    **Fields**:

    * **name**: `str` The Code42 account name.
    * **registration_key**: `str` The Code42 registration key (primarily for licensing purposes).
    * **tenant_id**: `str` The unique identifier for the account within Code42.
    """

    name: Optional[str] = Field(frozen=True)
    registration_key: Optional[str] = Field(frozen=True, alias="registrationKey")
    tenant_id: Optional[str] = Field(frozen=True, alias="tenantId")
    model_config = ConfigDict(validate_assignment=True)
