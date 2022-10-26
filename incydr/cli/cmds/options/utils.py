from incydr.cli.cmds.utils import user_lookup


def user_lookup_callback(ctx, param, value):
    if not value:
        return
    # only call user_lookup if username to prevent unnecessary client inits with obj()
    if "@" in str(value):
        return user_lookup(ctx.obj(), value)
    return value
