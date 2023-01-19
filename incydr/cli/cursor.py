import json
import os
from os import path

import click


class Cursor:
    def __init__(self, location):
        self._location = location
        self._name = path.basename(location)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        with open(self._location) as f:
            return f.read()


class CursorStore:
    """
    Cursor store for checkpoints.

    Properties:
        * dir_path - directory where files will be saved.
        * event_key - the string to be suffixed to the end of files which are storing events/event hashes for a checkpoint.

            Example:
                the file `chckpt_audit_events` is storing hashes of audit log events for the checkpoint called 'chcktpt'
    """

    def __init__(self, dir_path, event_key):
        self._dir_path = dir_path
        self._event_key = event_key

    def get(self, cursor_name):
        """Gets the last stored date observed timestamp."""
        try:
            location = path.join(self._dir_path, cursor_name)
            with open(location) as f:
                c = f.read()
                return c.strip() if c else None
        except FileNotFoundError:
            return None

    def replace(self, cursor_name, new_checkpoint):
        """Replaces the last stored date observed timestamp with the given one."""
        location = path.join(self._dir_path, cursor_name)
        with open(location, "w") as checkpoint:
            checkpoint.write(str(new_checkpoint))

    def delete(self, cursor_name):
        """Removes a single cursor from the store."""
        try:
            location = path.join(self._dir_path, cursor_name)
            os.remove(location)
        except FileNotFoundError:
            msg = f"No checkpoint named {cursor_name} found for this API client."
            raise click.BadOptionUsage("checkpoint", msg)

    def clean(self):
        """Removes all cursors from this store."""
        cursors = self.get_all_cursors()
        for cursor in cursors:
            self.delete(cursor.name)

    def get_all_cursors(self):
        """Returns a list of all cursors stored in this directory (which is typically scoped to a profile)."""
        dir_contents = os.listdir(self._dir_path)
        return [Cursor(f) for f in dir_contents if self._is_file(f)]

    def _is_file(self, node_name):
        return path.isfile(path.join(self._dir_path, node_name))

    def get_items(self, cursor_name):
        """
        Used with alerts and audit_log events to avoid duplicates
        """
        try:
            location = path.join(self._dir_path, cursor_name) + f"_{self._event_key}"
            with open(location) as checkpoint:
                return json.loads(checkpoint.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def replace_items(self, cursor_name, new_events):
        """
        Used with alerts and audit_log events to avoid duplicates
        """
        location = path.join(self._dir_path, cursor_name) + f"_{self._event_key}"
        with open(location, "w") as checkpoint:
            checkpoint.write(json.dumps(new_events))
