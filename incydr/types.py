import click


# TODO: do we want this ?
# class AutoDecodedFile(click.File):
#     """Attempts to autodetect file's encoding prior to normal click.File processing."""
#
#     def convert(self, value, param, ctx):
#         try:
#             with open(value, "rb") as file:
#                 self.encoding = chardet.detect(file.read())["encoding"]
#             if self.encoding is None:
#                 # TODO: logging
#                 click.echo(f"Failed to detect encoding of file: {value}")
#         except Exception:
#             pass  # we'll let click.File do it's own exception handling for the filepath
#
#         return super().convert(value, param, ctx)


class FileOrString(click.Path):
    """Declares a parameter to be a file (if the argument begins with `@`), otherwise accepts it as
    a string.
    """

    def __init__(self):
        super().__init__()

    def convert(self, value, param, ctx):
        if value.startswith("@") or value == "-":
            value = value.lstrip("@")
            file = super().convert(value, param, ctx)
            return file
        else:
            return value


file_or_str_cls = FileOrString()
