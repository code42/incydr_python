from pathlib import Path


class FilesClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = FilesV1(self._parent)
        return self._v1


class FilesV1:
    """Client for `/v1/files` endpoints.

    Usage example:

        >>> import incydr
        >>>
        >>> client = incydr.Client(**kwargs)
        >>> client.files.v1.download_file_by_sha256("example_hash", "./testfile.test")
    """

    def __init__(self, parent):
        self._parent = parent

    def download_file_by_sha256(self, sha256: str, target_path: Path) -> Path:
        """Download a file that matches the given SHA256 hash.

        **Parameters:**

        * **sh256**: `str` (required) The SHA256 hash matching the file you wish to download.
        * **target_path**: `Path | str` a string or `pathlib.Path` object that represents the target file path and
            name to which the file will be saved to.

        **Returns**: A `pathlib.Path` object representing the location of the downloaded file.
        """
        target = Path(
            target_path
        )  # ensure that target is a path even if we're given a string
        response = self._parent.session.get(f"/v1/files/get-file-by-sha256/{sha256}")
        target.write_bytes(response.content)
        return target

    def stream_file_by_sha256(self, sha256: str):
        """Stream a file that matches the given SHA256 hash.

        **Example usage:**
        ```
        >>> with sdk.files.v1.stream_file_by_sha256("example_hash") as response:
        >>>     with open("./testfile.zip", "wb") as file:
        >>>         for chunk in response.iter_content(chunk_size=128):
        >>>             file.write(chunk)
        ```

        **Parameters:**

        * **sh256**: `str` (required) The SHA256 hash matching the file you wish to download.

        **Returns**: A `requests.Response` object with a stream of the requested file.
        """
        return self._parent.session.get(
            f"/v1/files/get-file-by-sha256/{sha256}", stream=True
        )
