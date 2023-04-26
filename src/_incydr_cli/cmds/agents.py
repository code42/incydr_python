from os import environ
from pathlib import Path
from typing import List

import click
import requests
from boltons.iterutils import chunked
from rich.panel import Panel
from rich.progress import track

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.models import AgentCSV
from _incydr_cli.cmds.models import AgentJSON
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import input_format_option
from _incydr_cli.cmds.options.output_options import single_format_option
from _incydr_cli.cmds.options.output_options import SingleFormat
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.agents.models import Agent
from _incydr_sdk.core.client import Client
from _incydr_sdk.utils import model_as_card


@click.group(cls=IncydrGroup)
@logging_options
def agents():
    """
    View and manage Incydr agents.

    Incydr agents run on the endpoints in your environment and monitor for insider risk activity.
    """


@agents.command("list", cls=IncydrCommand)
@click.option(
    "--active/--inactive",
    default=None,
    help="Filter by active or inactive agents. Defaults to returning both when when neither option is passed.",
)
@table_format_option
@columns_option
@logging_options
def list_(
    active: bool = None,
    format_: TableFormat = None,
    columns: str = None,
):
    """
    List agents.
    """
    client = Client()
    agents = client.agents.v1.iter_all(active=active)

    if format_ == TableFormat.table:
        render.table(Agent, agents, columns=columns, flat=False)
    elif format_ == TableFormat.csv:
        render.csv(Agent, agents, columns=columns, flat=True)
    elif format_ == TableFormat.json_pretty:
        for agent in agents:
            console.print_json(agent.json())
    else:
        for agent in agents:
            click.echo(agent.json())


@agents.command(cls=IncydrCommand)
@click.argument("agent_id")
@single_format_option
@logging_options
def show(
    agent_id: str,
    format_: SingleFormat,
):
    """
    Show details for a single agent.
    """
    client = Client()
    agent = client.agents.v1.get_agent(agent_id)

    if format_ == SingleFormat.rich and client.settings.use_rich:
        console.print(Panel.fit(model_as_card(agent), title=f"Agent {agent.agent_id}"))
    elif format_ == SingleFormat.json_pretty:
        console.print_json(agent.json())
    else:
        click.echo(agent.json())


@agents.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_activate(file: Path, format_: str):
    """
    Activate a group of agents from a file (CSV or JSON-LINES formatted).

    \b
    Use `-` as filename to read from stdin.

    Input files require a header (for CSV input) or JSON key for each object (for JSON-LINES input) to identify
    which agent ID to activate.

    Header and JSON key values that are accepted are: agent_id, agentId, or guid
    """
    chunk_size = (
        environ.get("incydr_batch_size") or environ.get("INCYDR_BATCH_SIZE") or 50
    )
    try:
        chunk_size = int(chunk_size)
    except ValueError:
        console.print(
            f"INCYDR_BATCH_SIZE environment variable must be an integer, found: '{chunk_size}'"
        )
        return

    # parse CSV or JSON input
    if format_ == "csv":
        models = AgentCSV.parse_csv(file)
    else:
        models = AgentJSON.parse_json_lines(file)
    try:
        agent_ids = [agent.agent_id for agent in models]
    except ValueError as err:
        console.print(err)
        return

    # validate we got at least one agent_id
    num_agents = len(agent_ids)
    if num_agents < 1:
        console.print(f"[red]No agent IDs found in {format_} input.")
        return

    client = Client()
    batches = chunked(agent_ids, size=chunk_size)
    for batch in track(batches, description="Activating agents...", console=console):
        process_batch(client, batch, activate=True)


@agents.command(cls=IncydrCommand)
@click.argument("file", type=click.File())
@input_format_option
@logging_options
def bulk_deactivate(file: Path, format_: str):
    """
    Deactivate a group of agents from a file (CSV or JSON-LINES formatted).

    \b
    Use `-` as filename to read from stdin.

    Input files require a header (for CSV input) or JSON key for each object (for JSON-LINES input) to identify
    which agent ID to deactivate.

    Header and JSON key values that are accepted are: agent_id, agentId, or guid
    """
    chunk_size = (
        environ.get("incydr_batch_size") or environ.get("INCYDR_BATCH_SIZE") or 50
    )
    try:
        chunk_size = int(chunk_size)
    except ValueError:
        console.print(
            f"INCYDR_BATCH_SIZE environment variable must be an integer, found: '{chunk_size}'"
        )
        return

    # parse CSV or JSON input
    if format_ == "csv":
        models = AgentCSV.parse_csv(file)
    else:
        models = AgentJSON.parse_json_lines(file)
    try:
        agent_ids = [agent.agent_id for agent in models]
    except ValueError as err:
        console.print(err)
        return

    # validate we got at least one agent_id
    num_agents = len(agent_ids)
    if num_agents < 1:
        console.print(f"[red]No agent IDs found in {format_} input.")
        return

    client = Client()
    batches = chunked(agent_ids, size=chunk_size)
    for batch in track(batches, description="Deactivating agents...", console=console):
        process_batch(client, batch, activate=False)


def process_batch(client: Client, batch: List[str], activate: bool):
    action = "activation" if activate else "deactivation"
    api_call = client.agents.v1.activate if activate else client.agents.v1.deactivate
    process_individually = False
    try:
        api_call(batch)
    except requests.HTTPError as err:
        if err.response.status_code == 404:
            invalid_agent_ids = err.response.json().get("agentsNotFound")
            if invalid_agent_ids is None:
                console.print(
                    f"[red]Unknown 404 error processing batch of {len(batch)} agent {action}s."
                )
                process_individually = True
            else:
                console.print(
                    f"[red]404 Error processing batch of {len(batch)} agent {action}s, agent_ids not found:[/red] {invalid_agent_ids}"
                )
                batch = list(set(batch) - set(invalid_agent_ids))
                if len(batch) > 0:
                    console.print("Removing invalid agent_ids and retrying...")
                    try:
                        api_call(batch)
                    except requests.HTTPError as err:
                        console.print(f"[red]Error retrying batch. {err.response.text}")
                        process_individually = True
        else:
            console.print(
                f"[red]Unknown error processing batch of {len(batch)} agent {action}s."
            )
            process_individually = True
    if process_individually and len(batch) > 1:
        console.print(f"Trying agent {action} for this batch individually.")
        for agent_id in batch:
            try:
                api_call(agent_id)
            except requests.HTTPError as err:
                msg = f"Failed to process {action} for {agent_id}: {err.response.text}"
                client.settings.logger.error(msg)
                console.print(msg)
