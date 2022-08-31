from incydr._cases.models import Case
from incydr._cases.models import CasesPage
from incydr._customer.models import Customer
from incydr._devices.models import Device
from incydr._devices.models import DevicesPage
from incydr._users.models import Role
from incydr._users.models import RolesPage
from incydr._users.models import User
from incydr._users.models import UsersPage

__all__ = [
    "Case",
    "CasesPage",
    "Customer",
    "DevicesPage",
    "Device",
    "User",
    "UsersPage",
    "Role",
    "RolesPage",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr.models")  # noqa
