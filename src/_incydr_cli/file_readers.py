import chardet
import click


class AutoDecodedFile(click.File):
    """Attempts to autodetect file's encoding prior to normal click.File processing."""

    def convert(self, value, param, ctx):
        try:
            with open(value, "rb") as file:
                self.encoding = chardet.detect(file.read())["encoding"]
        except Exception:
            pass  # we'll let click.File do its own exception handling for the filepath

        return super().convert(value, param, ctx)


class FileOrString(AutoDecodedFile):
    """Declares a parameter to be a file (if the argument begins with `@`), otherwise accepts it as
    a string.
    """

    def __init__(self):
        super().__init__("r")

    def convert(self, value, param, ctx):
        if value.startswith("@") or value == "-":
            value = value.lstrip("@")
            return super().convert(value, param, ctx)
        else:
            return value
