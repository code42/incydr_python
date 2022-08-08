from typing import Optional

from pydantic import Field

from incydr._core.models import ResponseModel


class Customer(ResponseModel):
    name: Optional[str] = Field(
        allow_mutation=False, description="The customer's name."
    )
    registrationKey: Optional[str] = Field(
        allow_mutation=False, description="The customer's Code42 registration key."
    )
    tenantId: Optional[str] = Field(
        allow_mutation=False,
        description="The customer's unique ID identifying it within Code42.",
    )

    class Config:
        validate_assignment = True
