import click
from rich.table import Table

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.enums.trusted_activities import ActivityType
from _incydr_sdk.trusted_activities.client import MissingActivityActionGroupsError
from _incydr_sdk.trusted_activities.models import TrustedActivity
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def trusted_activities():
    """View and manage trusted activities."""


@trusted_activities.command(cls=IncydrCommand)
@click.argument("activity_id")
@single_format_option
@logging_options
def show(
    activity_id: str,
    format_: SingleFormat,
):
    """
    Show details for a single trusted activity.

    Includes general info on the trusted activity, as well as any 'Activity Action Groups', which specify
    various trusted service configurations (if applicable). For example, a trusted domain may include an activity
    action group indicating `GMAIL` as a trusted email sharing service.
    """
    client = Client()
    trusted_activity = client.trusted_activities.v2.get_trusted_activity(activity_id)
    _output_trusted_activity(
        trusted_activity, format_, use_rich=client.settings.use_rich
    )


@trusted_activities.command("list", cls=IncydrCommand)
@click.option("--activity-type", type=ActivityType, default=None, help="")
@table_format_option
@columns_option
@logging_options
def list_(
    activity_type: ActivityType = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List all trusted activities.
    """
    client = Client()
    activities = client.trusted_activities.v2.iter_all(activity_type=activity_type)
    if format_ == TableFormat.table:
        columns = columns or [
            "activity_id",
            "type",
            "value",
            "description",
            "principal_type",
            "update_time",
            "updated_by_principal_id",
            "updated_by_principal_name",
        ]
        render.table(TrustedActivity, activities, columns=columns)
    elif format_ == TableFormat.csv:
        render.csv(TrustedActivity, activities, columns=columns)
    elif format_ == TableFormat.json_pretty:
        for activity in activities:
            console.print_json(activity.json())
    else:
        for activity in activities:
            click.echo(activity.json())


@trusted_activities.command(cls=IncydrCommand)
@click.argument("activity_id")
@click.option("--type", "type_", default=None)
@click.option("--value", default=None)
@click.option("--description", default=None)
@click.option("--high-value-source", type=bool, default=None)
@single_format_option
@logging_options
def update(
    activity_id: str,
    type_: str = None,
    value: str = None,
    description: str = None,
    high_value_source: bool = None,
    format_: SingleFormat = None,
):
    """
    Update a trusted activity.
    """
    if not any([type_, value, description, (high_value_source is not None)]):
        raise click.UsageError(
            "At least one command option must be provided to update a trusted activity.  Use `trusted-activities update --help` to see available options."
        )
    # left off updating activity-action-groups for now, they're very complex
    client = Client()
    trusted_activity = client.trusted_activities.v2.get_trusted_activity(activity_id)
    if type_:
        trusted_activity.type = type_
    if value:
        trusted_activity.value = value
    if description:
        trusted_activity.description = description
    if high_value_source is not None:
        trusted_activity.is_high_value_source = high_value_source
    updated_activity = client.trusted_activities.v2.update(trusted_activity)
    _output_trusted_activity(updated_activity, format_, client.settings.use_rich)


@trusted_activities.command(cls=IncydrCommand)
@click.argument("activity_id")
@logging_options
def delete(
    activity_id: str,
):
    """
    Delete a trusted activity.
    """
    client = Client()
    client.trusted_activities.v2.delete(activity_id)
    console.print(f"Successfully deleted trusted activity {activity_id}.")


@trusted_activities.group(cls=IncydrGroup)
@logging_options
def add():
    """Add a new trusted activity."""


@add.command("domain", cls=IncydrCommand)
@click.argument("domain")
@click.option("--description", default=None, help="Optional description.")
@click.option(
    "--file-upload",
    is_flag=True,
    default=False,
    help="Trust file upload events to where the tab URL or title includes this domain.",
)
@click.option(
    "--git-push",
    is_flag=True,
    default=False,
    help="Trust git push events to this domain.",
)
@click.option(
    "--cloud-sync",
    "cloud_sync_services",
    type=click.Choice(["BOX", "GOOGLE_DRIVE", "ICLOUD", "ONE_DRIVE"]),
    default=[],
    help="Specify which cloud sync service(s) to trust.",
    multiple=True,
)
@click.option(
    "--cloud-share",
    "cloud_share_services",
    type=click.Choice(["BOX", "GOOGLE_DRIVE", "ONE_DRIVE"]),
    default=[],
    help="Specify which cloud share service(s) to trust.",
    multiple=True,
)
@click.option(
    "--email-share",
    "email_share_services",
    type=click.Choice(["GMAIL", "MICROSOFT_365"]),
    default=[],
    help="Specify which email share service(s) to trust.",
    multiple=True,
)
@single_format_option
@logging_options
def domain_(
    domain: str,
    description: str = None,
    file_upload: bool = False,
    git_push: bool = False,
    cloud_sync_services: str = None,
    cloud_share_services: str = None,
    email_share_services: str = None,
    format_: SingleFormat = None,
):
    """
    Trust activity across an entire `DOMAIN` (ex: `my-domain.com`).

    The following activities can be configured:

    * `--file-upload` - Trust file uploads to this domain.  Defaults to false.
    * `--git-push` - Trust git push events to this domain.  Defaults to false.
    * `--cloud-sync-services` [`BOX|GOOGLE_DRIVE|ICLOUD|ONE_DRIVE`] - Trust cloud sync activity from the specified service(s) if the username signed into the sync app is on this domain.
        If you want to only trust activity for a specific corporate account, add a trusted account name instead.
    * `--cloud-share-services` [`BOX|GOOGLE_DRIVE|ONE_DRIVE`] - Trust cloud share activity from the specified service(s) if the user its shared with is on this domain.
        You must have a cloud connector configured for your tenant to support this trusted action.
    * `--email-share-services` [`GMAIL|MICROSOFT_365`] - Trust email share activity from the specified service(s) if the email recipient is on this domain.
        You must have an email connector configured for your tenant to support this trusted action.

    Multiple options can be supplied to specify cloud-share, cloud-sync, and email-share services.

    For example, the following command will create a trusted domain that trusts file-uploads to the domain and cloud sync events from `BOX` and `ICLOUD`.

        trusted-activities add domain --file-upload --cloud-sync-services BOX --cloud-sync-services ICLOUD

    """
    client = Client()
    try:
        activity = client.trusted_activities.v2.add_domain(
            domain,
            description=description,
            file_upload=file_upload,
            git_push=git_push,
            cloud_sync_services=cloud_sync_services,
            cloud_share_services=cloud_share_services,
            email_share_services=email_share_services,
        )
    except MissingActivityActionGroupsError:
        raise click.UsageError(
            "At least one activity must be trusted for this domain.  Use 'incydr trusted-activities add domain --help' to see available options for configuration."
        )
    _output_trusted_activity(activity, format_, client.settings.use_rich)


@add.command("url-path", cls=IncydrCommand)
@click.argument("url_path")
@click.option("--description", default=None, help="Optional description.")
@single_format_option
@logging_options
def url_path_(
    url_path: str,
    description: str = None,
    format_: SingleFormat = None,
):
    """
    Trust browser uploads to only part of a domain by trusting a specific `URL_PATH` (ex: `my-domain.com/path`).
    """
    client = Client()
    activity = client.trusted_activities.v2.add_url_path(url_path, description)
    _output_trusted_activity(activity, format_, client.settings.use_rich)


@add.command(cls=IncydrCommand)
@click.argument("workspace_name")
@click.option("--description", default=None, help="Optional description.")
@single_format_option
@logging_options
def slack_workspace(
    workspace_name: str,
    description: str = None,
    format_: SingleFormat = None,
):
    """
    Trust activity uploaded through a Slack workspace specified by `WORKSPACE_NAME`.
    """
    client = Client()
    activity = client.trusted_activities.v2.add_slack_workspace(
        workspace_name, description=description
    )
    _output_trusted_activity(activity, format_, client.settings.use_rich)


@add.command(cls=IncydrCommand)
@click.argument("account_name")
@click.option("--description", default=None, help="Optional description.")
@click.option(
    "--dropbox",
    is_flag=True,
    default=False,
    help="Trust Dropbox as a cloud sync service.",
)
@click.option(
    "--one-drive",
    is_flag=True,
    default=False,
    help="Trust OneDrive as a cloud sync service.",
)
@single_format_option
@logging_options
def account(
    account_name: str,
    description: str = None,
    dropbox: bool = False,
    one_drive: bool = False,
    format_: SingleFormat = None,
):
    """
    Trust activity for a specific corporate account specified by `ACCOUNT_NAME` for cloud sync apps installed on user devices.

    Use the `--dropbox` and/or `--one-drive` options to indicate trusted cloud sync services for this account.
    """
    client = Client()
    activity = client.trusted_activities.v2.add_account_name(
        account_name, description=description, dropbox=dropbox, one_drive=one_drive
    )
    _output_trusted_activity(activity, format_, client.settings.use_rich)


@add.command(cls=IncydrCommand)
@click.argument("git_uri")
@click.option("--description", default=None, help="Optional description.")
@single_format_option
@logging_options
def git_repo(
    git_uri: str,
    description: str = None,
    format_: SingleFormat = None,
):
    """
    Trust file upload activity to a git repository.  Requires a `GIT_URI` path (ex: `bitbucket.org:exampleent/myrepo`).
    """
    client = Client()
    activity = client.trusted_activities.v2.add_git_repository(
        git_uri, description=description
    )
    _output_trusted_activity(activity, format_, client.settings.use_rich)


def _output_trusted_activity(
    model: TrustedActivity, format_: SingleFormat, use_rich: bool = True
):
    if format_ == SingleFormat.rich and use_rich:
        t = Table(title=f"Trusted Activity {model.activity_id}")
        t.add_column("Info")
        t.add_column("Action Groups")

        # exclude activity action groups from the info panel
        include = list(TrustedActivity.__fields__.keys())
        include.remove("activity_action_groups")
        t.add_row(
            model_as_card(
                model,
                include=include,
            ),
            model_as_card(model, include=["activity_action_groups"]),
        )

        console.print(t)
    elif format_ == SingleFormat.json_pretty:
        console.print_json(model.json())
    else:
        click.echo(model.json())
