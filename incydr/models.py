from incydr._cases.models import Case
from incydr._cases.models import CasesPage
from incydr._customer.models import Customer
from incydr._devices.models import Device
from incydr._devices.models import DevicesPage
from incydr._file_events.models.event import FileEventV2
from incydr._file_events.models.response import FileEventsPage
from incydr._file_events.models.response import SavedSearch
from incydr._file_events.models.response import SavedSearchesPage

__all__ = [
    "Case",
    "CasesPage",
    "Customer",
    "Device",
    "DevicesPage",
    "SavedSearchesPage",
    "SavedSearch",
    "FileEventsPage",
    "FileEventV2",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr.models")  # noqa
