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
