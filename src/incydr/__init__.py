# SPDX-FileCopyrightText: 2022-present Code42 Software <integrations@code42.com>
#
# SPDX-License-Identifier: MIT
from . import models
from _incydr_sdk.__version__ import __version__
from _incydr_sdk.core.client import Client
from _incydr_sdk.queries.alerts import AlertQuery
from _incydr_sdk.queries.file_events import EventQuery

__all__ = ["__version__", "Client", "AlertQuery", "EventQuery", "models"]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "incydr")  # noqa
