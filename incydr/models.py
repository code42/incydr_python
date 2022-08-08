from incydr._cases.models import Case
from incydr._cases.models import CasesPage
from incydr._customer.models import Customer


__all__ = ["Case", "CasesPage", "Customer"]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr.models")  # noqa
