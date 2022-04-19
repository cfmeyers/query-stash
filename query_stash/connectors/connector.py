from typing import List, Optional

from query_stash.config import get_config, get_connection_from_config
from query_stash.types import ConfigDict, RowDict

from .postgres import (
    PostgresConnection,
    PostgresDictCursor,
    get_postgres_connection,
    get_postgres_dict_cursor,
)


def get_connection(config: ConfigDict):
    connection_type = config["type"]
    if connection_type == "postgres":
        return get_postgres_connection(config)
    raise Exception(f"Unknown connection type: {connection_type}")


class Connector:
    def __init__(self, config_path: Optional[str], connection_name: str):
        config = get_config(config_path)
        self.connection_config = get_connection_from_config(config, connection_name)
        self.connection_type = self.connection_config["type"]
        self.conn = self.get_connection(self.connection_config)

    def get_connection(self, config: ConfigDict) -> PostgresConnection:
        if self.is_postgres:
            return get_postgres_connection(config)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_dict_cursor(self) -> PostgresDictCursor:
        if self.is_postgres:
            return get_postgres_dict_cursor(self.conn)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_results(self, query: str) -> List[RowDict]:
        with self.get_dict_cursor() as dict_cursor:
            dict_cursor.execute(query)
            results = dict_cursor.fetchall()
            return [dict(r) for r in results]

    @property
    def is_postgres(self) -> bool:
        return self.connection_type == "postgres"
