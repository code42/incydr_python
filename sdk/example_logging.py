from pathlib import Path
from time import sleep

import incydr
from _incydr_sdk.core.settings import _incydr_console

print("Updating doc svg images...")

_incydr_console.width = 120
_incydr_console.record = True

client = incydr.Client(log_level="INFO")
client.cases.v1.get_case(21)
sleep(1)
client.settings.logger.warning("Logged warning message!")
sleep(1)
client.settings.log_level = "DEBUG"
client.cases.v1.get_case(21)

_incydr_console.save_svg(Path() / "docs" / "rich_logging.svg", title="Rich Logging")
