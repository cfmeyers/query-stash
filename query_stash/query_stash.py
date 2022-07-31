# -*- coding: utf-8 -*-

"""Main module."""

from typing import Optional

from query_stash.config import get_config, get_connection_from_config
from query_stash.connectors import Connector
from query_stash.render import RenderedTable, get_rendered_table
from query_stash.sqlite import QueryStasher


def connect_and_query_db(
    config_path: Optional[str], connection_name: Optional[str], query: str
) -> str:
    connector = Connector(config_path, connection_name)
    err, results = connector.get_results(query)
    if len(results) == 0 and err is None:
        return "Query returned no results!"
    if err is None:
        rendered_table = get_rendered_table(results)
        stasher = QueryStasher()
        tags = ""
        stasher.stash(
            query,
            rendered_table,
            tags,
            connector.connection_name,
            connector.connection_name,
        )
        return str(rendered_table)
    else:
        return err
