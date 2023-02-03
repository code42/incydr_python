import logging

import pytest


@pytest.fixture()
def mock_log_record(mocker):
    mock_record = mocker.MagicMock(spec=logging.LogRecord)
    mock_record.msg = "test"
    mock_record.exc_info = None
    mock_record.exc_text = None
    mock_record.stack_info = None
    return mock_record
