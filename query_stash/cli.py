# -*- coding: utf-8 -*-

"""Console script for query_stash."""
import sys
from typing import Optional

import click

from query_stash.query_stash import connect_and_query_db


@click.group()
def cli():
    pass


@cli.command()
@click.argument("query", type=str)
@click.option(
    "--config-path",
    default=None,
    help="Path to query-stash.toml config file",
    type=str,
)
@click.option(
    "--connection-name",
    help="Path to query-stash.toml config file",
    default=None,
    type=str,
)
def query(
    query: str, config_path: Optional[str] = None, connection_name: Optional[str] = None
):
    rendered_table = connect_and_query_db(
        config_path=config_path, connection_name=connection_name, query=query
    )
    print(rendered_table)
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
