import pytest
from pytest_httpserver import HTTPServer
from requests.exceptions import HTTPError

from _incydr_cli.main import incydr
from incydr import Client


TEST_SHA256 = "38acb15d02d5ac0f2a2789602e9df950c380d2799b4bdb59394e4eeabdd3a662"
BAD_SHA256 = "asdf"
TEST_DATA = b"test data"


@pytest.fixture
def mock_file_download(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/files/get-file-by-sha256/{TEST_SHA256}"
    ).respond_with_data(response_data=TEST_DATA, status=200)
    return httpserver_auth


@pytest.fixture
def mock_bad_sha256(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/files/get-file-by-sha256/{BAD_SHA256}"
    ).respond_with_data(response_data="", status=400)
    return httpserver_auth


@pytest.fixture
def mock_file_not_found(httpserver_auth: HTTPServer):
    httpserver_auth.expect_request(
        f"/v1/files/get-file-by-sha256/{TEST_SHA256}"
    ).respond_with_data(response_data="", status=404)
    return httpserver_auth


def test_download_file_by_sha256_calls_with_correct_parameter(
    mock_file_download, tmp_path
):
    c = Client()
    p = tmp_path / "testfile.test"
    f = c.files.v1.download_file_by_sha256(TEST_SHA256, p)
    with open(f, "rb") as file:
        content = file.read()
    assert content == TEST_DATA
    mock_file_download.check()


def test_download_file_by_sha256_raises_error_when_invalid_sha256(mock_bad_sha256):
    c = Client()
    with pytest.raises(HTTPError) as error:
        c.files.v1.download_file_by_sha256(BAD_SHA256, "testpath.text")
    assert error.value.response.status_code == 400
    mock_bad_sha256.check()


def test_download_file_by_sha256_raises_error_when_file_not_found(mock_file_not_found):
    c = Client()
    with pytest.raises(HTTPError) as error:
        c.files.v1.download_file_by_sha256(TEST_SHA256, "testpath.text")
    assert error.value.response.status_code == 404
    mock_file_not_found.check()


def test_stream_file_by_sha256_streams_file(mock_file_download):
    c = Client()
    response = c.files.v1.stream_file_by_sha256(TEST_SHA256)
    content = b"".join([c for c in response.iter_content(chunk_size=128) if c])
    assert content == TEST_DATA


# ************************************************ CLI ************************************************


def test_cli_download_downloads_file(runner, mock_file_download, tmp_path):
    test_path = tmp_path / "testfile.test"
    result = runner.invoke(
        incydr,
        ["files", "download", TEST_SHA256, "--path", str(test_path)],
    )
    assert result.exit_code == 0
    with open(test_path, "rb") as file:
        content = file.read()
    assert content == TEST_DATA
    mock_file_download.check()
