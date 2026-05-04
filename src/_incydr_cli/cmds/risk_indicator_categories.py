import itertools
from typing import Iterator
from typing import Optional

import click

from _incydr_cli import console
from _incydr_cli import logging_options
from _incydr_cli import render
from _incydr_cli.cmds.options.output_options import columns_option
from _incydr_cli.cmds.options.output_options import table_format_option
from _incydr_cli.cmds.options.output_options import TableFormat
from _incydr_cli.core import IncydrCommand
from _incydr_cli.core import IncydrGroup
from _incydr_sdk.core.client import Client
from _incydr_sdk.risk_indicator_categories.models import RiskIndicator


@click.group(cls=IncydrGroup)
@logging_options
def risk_indicator_categories():
    """View and manage risk indicators."""


@risk_indicator_categories.command("list", cls=IncydrCommand)
@table_format_option
@columns_option
@logging_options
def list_categories(
    format_: Optional[TableFormat] = None,
    columns: Optional[str] = None,
):
    """
    List Risk Indicators by category and subcategory.
    """
    client = Client()
    categories = client.risk_indicator_categories.v1.list_categories().categories

    if format_ == TableFormat.table:
        columns = columns or [
            "id",
            "name",
            "description",
            "category_name",
            "category_id",
            "subcategory_name",
            "subcategory_id",
            "type",
        ]
        render.table(
            RiskIndicatorTableEntry,
            iter_risk_indicator_table_entries(categories),
            columns=columns,
            flat=False,
        )
    elif format_ == TableFormat.csv:
        render.csv(
            RiskIndicatorTableEntry,
            iter_risk_indicator_table_entries(categories),
            columns=columns,
            flat=True,
        )
    else:
        printed = False
        for indicator in iter_risk_indicator_table_entries(categories):
            printed = True
            if format_ == TableFormat.json_pretty:
                console.print_json(indicator.json())
            else:
                click.echo(indicator.json())
        if not printed:
            console.print("No results found.")


class RiskIndicatorTableEntry(RiskIndicator):
    category_name: str
    category_id: str
    category_description: Optional[str]
    subcategory_name: str
    subcategory_id: str
    subcategory_description: Optional[str]
    type: str


def iter_risk_indicator_table_entries(categories) -> Iterator[RiskIndicatorTableEntry]:
    for category in categories:
        for subcategory in category.subcategories:
            for indicator, indicator_type in itertools.chain(
                ((i, "standard") for i in subcategory.standard_indicators),
                ((i, "custom") for i in subcategory.custom_indicators),
            ):
                yield RiskIndicatorTableEntry(
                    id=indicator.id,
                    name=indicator.name,
                    description=indicator.description,
                    category_name=category.name,
                    category_id=category.id,
                    category_description=category.description,
                    subcategory_name=subcategory.name,
                    subcategory_id=subcategory.id,
                    subcategory_description=subcategory.description,
                    type=indicator_type,
                )
