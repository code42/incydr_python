from incydr._cases.models import Case
from incydr._cases.models import CasesPage
from incydr._customer.models import Customer
from incydr._devices.models import Device
from incydr._devices.models import DevicesPage
from incydr._trusted_activities.models import TrustedActivitiesPage
from incydr._trusted_activities.models import TrustedActivity


__all__ = [
    "Case",
    "CasesPage",
    "Customer",
    "DevicesPage",
    "Device",
    "TrustedActivity",
    "TrustedActivitiesPage",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr.models")  # noqa
