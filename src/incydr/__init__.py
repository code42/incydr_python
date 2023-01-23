# SPDX-FileCopyrightText: 2022-present Code42 Software <integrations@code42.com>
#
# SPDX-License-Identifier: MIT
from _client.core.client import Client
from _client.models import *  # noqa
from _client.queries.alerts import AlertQuery
from _client.queries.file_events import EventQuery
from _client.utils import *  # noqa

__all__ = ["Client", "AlertQuery", "EventQuery"]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr")  # noqa
