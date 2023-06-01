from typing import Any, MutableMapping

import duckdb
from duckdb import DuckDBPyConnection

from query_stash.types import RowDict


def get_duckdb_connection(config: MutableMapping[str, Any]) -> DuckDBPyConnection:
    return duckdb.connect(database=config["path"])


class DuckDBDictCursor:
    """A hack because duckdb doesn't have a dict cursor"""

    def __init__(self, conn: DuckDBPyConnection):
        self.conn = conn

    def execute(self, query: str):
        self.conn.execute(query)

    def fetchall(self) -> list[RowDict]:
        result_df = self.conn.df()
        records = result_df.to_dict("records")
        return records

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def get_duckdb_dict_cursor(conn: DuckDBPyConnection):
    return DuckDBDictCursor(conn)
