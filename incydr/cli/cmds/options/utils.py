import click

from incydr.cli.cmds.utils import user_lookup

checkpoint_option = click.option(
    "--checkpoint",
    "checkpoint_name",
    default=None,
    help="Use a checkpoint with the given name to only get search results that were not previously retrieved. "
    "If a checkpoint for the search with the given name doesn't exist, it will be created on the first run. "
    "Subsequent CLI runs with this option and the same name will use the stored checkpoint to modify the search query and then update the stored checkpoint."
    "Checkpointing is most accurate with json outputs.  For table and csv formats, checkpointing will track the last returned event in the table.",
)


def user_lookup_callback(ctx, param, value):
    if not value:
        return
    # only call user_lookup if username to prevent unnecessary client inits with obj()
    if "@" in str(value):
        return user_lookup(ctx.obj(), value)
    return value
