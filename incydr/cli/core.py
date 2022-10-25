import click

try:
    import rich

    from typer import rich_utils

except ImportError:  # pragma: nocover
    rich = None  # type: ignore


class IncydrCommand(click.Command):
    def __init__(self, *args, **kwargs):
        # self.rich_markup_mode should be one of ["markdown", "rich", None]
        self.rich_markup_mode = "rich"
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if not rich:
            return super().format_help(ctx, formatter)
        return rich_utils.rich_format_help(
            obj=self,
            ctx=ctx,
            markup_mode=self.rich_markup_mode,
        )


class IncydrGroup(click.Group):
    def __init__(self, *args, **kwargs):
        self.rich_markup_mode = "rich"
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if not rich:
            return super().format_help(ctx, formatter)
        return rich_utils.rich_format_help(
            obj=self,
            ctx=ctx,
            markup_mode=self.rich_markup_mode,
        )


def incompatible_with(incompatible_opts):
    """Factory for creating custom `click.Option` subclasses that enforce incompatibility with the
    option strings passed to this function.
    """

    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            # if None it means we're in autocomplete mode and don't want to validate
            if ctx.obj is not None:
                found_incompatible = ", ".join(
                    [
                        f"--{opt.replace('_', '-')}"
                        for opt in opts
                        if opt in incompatible_opts
                    ]
                )
                if self.name in opts and found_incompatible:
                    name = self.name.replace("_", "-")
                    raise click.BadOptionUsage(
                        option_name=self.name,
                        message=f"--{name} can't be used with: {found_incompatible}",
                    )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption