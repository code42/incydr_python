import difflib
import re

import click
from requests import HTTPError

from incydr._core.client import Client
from incydr.exceptions import IncydrException
from incydr.exceptions import LoggedCLIError

_DIFFLIB_CUT_OFF = 0.6

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


class ExceptionHandlingGroup(IncydrGroup):
    """A `click.Group` subclass to add custom exception handling."""

    _original_args = None

    def make_context(self, info_name, args, parent=None, **extra):
        # grab the original command line arguments for logging purposes
        self._original_args = " ".join(args)

        return super().make_context(info_name, args, parent=parent, **extra)

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except click.UsageError as err:
            self._suggest_cmd(err)
        except LoggedCLIError:
            raise
        except click.exceptions.Exit:
            raise
        except IncydrException as err:
            # log error and raise custom error to print error message to console
            client = Client(skip_auth=True)
            client._log_error(err)
            raise IncydrException(err.args[0])
        except click.ClickException:
            raise
        except HTTPError as err:
            # log error with traceback and print error code with brief error message to console
            client = Client(skip_auth=True)
            client._log_verbose_error(self._original_args, err.request)
            raise LoggedCLIError(err.args[0])
        except OSError:
            raise
        except Exception:
            # log error with traceback and print message pointing user to logs
            client = Client(skip_auth=True)
            client._log_verbose_error()
            raise LoggedCLIError("Unknown problem occurred.")

    @staticmethod
    def _suggest_cmd(usage_err):
        """Handles fuzzy suggestion of commands that are close to the bad command entered."""
        if usage_err.message is not None:
            match = re.match("No such command '(.*)'.", usage_err.message)
            if match:
                bad_arg = match.groups()[0]
                available_commands = list(usage_err.ctx.command.commands.keys())
                suggested_commands = difflib.get_close_matches(
                    bad_arg, available_commands, cutoff=_DIFFLIB_CUT_OFF
                )
                if not suggested_commands:
                    raise usage_err
                usage_err.message = (
                    f"No such command '{bad_arg}'. "
                    f"Did you mean {' or '.join(suggested_commands)}?"
                )
        raise usage_err


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
