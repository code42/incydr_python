import click

from _incydr_cli.cmds.options.utils import user_lookup_callback

manager_option = click.option(
    "--manager",
    default=None,
    help="Filter by manager.  Accepts a manager's user ID or username, performs an additional lookup if a username is passed.",
    callback=user_lookup_callback,
)
title_option = click.option("--title", default=None, help="Filter by job title.")
division_option = click.option("--division", default=None, help="Filter by division.")
department_option = click.option(
    "--department", default=None, help="Filter by department."
)
employment_type_option = click.option(
    "--employment-type", default=None, help="Filter by employment type."
)
country_option = click.option("--country", default=None, help="Filter by country.")
region_option = click.option("--region", default=None, help="Filter by region (state).")
locality_option = click.option(
    "--locality", default=None, help="Filter by locality (city)."
)
active_option = click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive users. Defaults to returning both when when neither option is passed.",
)
deleted_option = click.option(
    "--deleted/--non-deleted",
    default=None,
    help="Filter by deleted or non-deleted users. Defaults to returning both when when neither option is passed.",
)
support_user_option = click.option(
    "--support-user/--non-support-user",
    default=None,
    help="Filter by support users or non-support users. Defaults to returning both when when neither option is passed.",
)


def profile_filter_options(f):
    f = manager_option(f)
    f = title_option(f)
    f = division_option(f)
    f = department_option(f)
    f = employment_type_option(f)
    f = country_option(f)
    f = region_option(f)
    f = locality_option(f)
    f = active_option(f)
    f = deleted_option(f)
    f = support_user_option(f)
    return f
