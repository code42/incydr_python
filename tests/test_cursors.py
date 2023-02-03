from os import path

import click
import pytest

from _incydr_cli import get_user_project_path
from _incydr_cli.cursor import CursorStore

CURSOR_NAME = "testcursor"
EVENT_KEY = "events"
CHECKPOINT_FOLDER_NAME = "alert_checkpoints"
PROFILE_NAME = "key-42"  # should be an api key
DIR_PATH = get_user_project_path(
    "checkpoints",
    PROFILE_NAME,
    CHECKPOINT_FOLDER_NAME,
)


_NAMESPACE = "_incydr_cli.cursor"


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("builtins.open", mocker.mock_open(read_data="123456789"))
    return mock


@pytest.fixture
def mock_empty_checkpoint(mocker):
    mock = mocker.patch("builtins.open", mocker.mock_open(read_data=""))
    return mock


@pytest.fixture(autouse=True)
def mock_makedirs(mocker):
    return mocker.patch("os.makedirs")


@pytest.fixture(autouse=True)
def mock_remove(mocker):
    return mocker.patch("os.remove")


@pytest.fixture(autouse=True)
def mock_listdir(mocker):
    return mocker.patch("os.listdir")


AUDIT_LOG_EVENT_HASH_1 = "bc8f70ff821cadcc3e717d534d14737d"
AUDIT_LOG_EVENT_HASH_2 = "66ad12c0a0dba2b41520fb69aeefd84d"


@pytest.fixture
def mock_open_events(mocker):
    mock = mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data=f'["{AUDIT_LOG_EVENT_HASH_1}", "{AUDIT_LOG_EVENT_HASH_2}"]'
        ),
    )
    return mock


@pytest.fixture
def mock_isfile(mocker):
    mock = mocker.patch(f"{_NAMESPACE}.os.path.isfile")
    mock.return_value = True
    return mock


class TestBaseCursorStore:
    def test_get_returns_expected_timestamp(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == "123456789"

    def test_get_when_profile_does_not_exist_returns_none(self, mocker):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        checkpoint = store.get(CURSOR_NAME)
        mock_open = mocker.patch(f"{_NAMESPACE}.open")
        mock_open.side_effect = FileNotFoundError
        assert checkpoint is None

    def test_get_reads_expected_file(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.get(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".incydr")
        expected_path = path.join(
            user_path, "checkpoints", PROFILE_NAME, CHECKPOINT_FOLDER_NAME, CURSOR_NAME
        )
        mock_open.assert_called_once_with(expected_path)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".incydr")
        expected_path = path.join(
            user_path,
            "checkpoints",
            PROFILE_NAME,
            CHECKPOINT_FOLDER_NAME,
            "checkpointname",
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".incydr")
        path.join(
            user_path,
            "checkpoints",
            PROFILE_NAME,
            CHECKPOINT_FOLDER_NAME,
            "checkpointname",
        )
        mock_open.return_value.write.assert_called_once_with("123")

    def test_delete_calls_remove_on_expected_file(self, mock_open, mock_remove):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.delete("deleteme")
        user_path = path.join(path.expanduser("~"), ".incydr")
        expected_path = path.join(
            user_path, "checkpoints", PROFILE_NAME, CHECKPOINT_FOLDER_NAME, "deleteme"
        )
        mock_remove.assert_called_once_with(expected_path)

    def test_delete_when_checkpoint_does_not_exist_raises_cli_error(
        self, mock_open, mock_remove
    ):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        mock_remove.side_effect = FileNotFoundError
        with pytest.raises(click.UsageError):
            store.delete("deleteme")

    def test_clean_calls_remove_on_each_checkpoint(
        self, mock_open, mock_remove, mock_listdir, mock_isfile
    ):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.clean()
        assert mock_remove.call_count == 3

    def test_get_all_cursors_returns_all_checkpoints(
        self, mock_open, mock_listdir, mock_isfile
    ):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = CursorStore(DIR_PATH, EVENT_KEY)
        cursors = store.get_all_cursors()
        assert len(cursors) == 3
        assert cursors[0].name == "fileone"
        assert cursors[1].name == "filetwo"
        assert cursors[2].name == "filethree"

    def test_get_items_returns_expected_list(self, mock_open_events):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        event_list = store.get_items(CURSOR_NAME)
        assert event_list == [AUDIT_LOG_EVENT_HASH_1, AUDIT_LOG_EVENT_HASH_2]

    def test_get_items_reads_expected_file(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.get_items(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".incydr")
        expected_filename = CURSOR_NAME + "_events"
        expected_path = path.join(
            user_path,
            "checkpoints",
            PROFILE_NAME,
            CHECKPOINT_FOLDER_NAME,
            expected_filename,
        )
        mock_open.assert_called_once_with(expected_path)

    def test_get_items_when_profile_does_not_exist_returns_empty_list(self, mocker):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        event_list = store.get_items(CURSOR_NAME)
        mock_open = mocker.patch(f"{_NAMESPACE}.open")
        mock_open.side_effect = FileNotFoundError
        assert event_list == []

    def test_get_items_when_checkpoint_not_valid_json_returns_empty_list(self, mocker):
        mocker.patch("builtins.open", mocker.mock_open(read_data="invalid_json"))
        store = CursorStore(DIR_PATH, EVENT_KEY)
        event_list = store.get_items(CURSOR_NAME)
        assert event_list == []

    def test_replace_items_writes_to_expected_file(self, mock_open):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.replace_items("checkpointname", ["hash1", "hash2"])
        user_path = path.join(path.expanduser("~"), ".incydr")
        expected_path = path.join(
            user_path,
            "checkpoints",
            PROFILE_NAME,
            CHECKPOINT_FOLDER_NAME,
            "checkpointname_events",
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_items_writes_expected_content(self, mock_open_events):
        store = CursorStore(DIR_PATH, EVENT_KEY)
        store.replace_items("checkpointname", ["hash1", "hash2"])
        user_path = path.join(path.expanduser("~"), ".incydr")
        path.join(
            user_path,
            "checkpoints",
            PROFILE_NAME,
            CHECKPOINT_FOLDER_NAME,
            "checkpointname_events",
        )
        mock_open_events.return_value.write.assert_called_once_with(
            '["hash1", "hash2"]'
        )
