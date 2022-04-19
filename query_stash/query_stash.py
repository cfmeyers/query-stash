# -*- coding: utf-8 -*-

"""Main module."""

from typing import Optional

from query_stash.config import get_config, get_connection_from_config
from query_stash.connectors import Connector
from query_stash.render import RenderedTable, get_rendered_table


def connect_and_query_db(
    config_path: Optional[str], connection_name: Optional[str], query: str
) -> RenderedTable:
    connector = Connector(config_path, connection_name)
    results = connector.get_results(query)
    rendered_table = get_rendered_table(results)
    return rendered_table
