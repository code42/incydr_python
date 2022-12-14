# SPDX-FileCopyrightText: 2022-present Code42 Software <integrations@code42.com>
#
# SPDX-License-Identifier: MIT
from incydr import utils
from incydr._core.client import Client
from incydr._queries.alerts import AlertQuery
from incydr._queries.file_events import EventQuery
from incydr.models import *  # noqa

__all__ = ["Client", "AlertQuery", "EventQuery"]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr")  # noqa
