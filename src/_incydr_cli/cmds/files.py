import os
from pathlib import Path

import click

from _incydr_cli import logging_options
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client

path_option = click.option(
    "--path",
    help='The file path where to save the file. The path must include the file name (e.g. "/path/to/my_file.txt"). Defaults to a file named "downloaded_file" in the current directory.',
    default=str(Path(os.getcwd()) / "downloaded_file"),
)


@click.group(cls=IncydrGroup)
@logging_options
def files():
    """Download files by SHA256 hash."""


@files.command(cls=IncydrCommand)
@click.argument("SHA256")
@path_option
@logging_options
def download(sha256: str, path: str):
    """
    Download the file matching the given SHA256 hash to the target path.
    """
    client = Client()
    client.files.v1.download_file_by_sha256(sha256, path)
