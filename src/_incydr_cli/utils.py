import os
from os import path

PACKAGE_NAME = "incydr"


def get_user_project_path(*subdirs):
    """
    Converts all args to a consecutive list of subdirectories within the project path.
    If the path does not exist, creates the necessary directories.

    Returns the path on your user dir to /.incydr/[subdir].
    """
    user_project_path = path.join(path.expanduser("~"), f".{PACKAGE_NAME}")
    result_path = path.join(user_project_path, *subdirs)
    if not path.exists(result_path):
        os.makedirs(result_path)
    return result_path
