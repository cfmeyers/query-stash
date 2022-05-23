from typing import List, Optional, Union

from query_stash.config import get_config, get_connection_from_config
from query_stash.types import ConfigDict, RowDict

from .postgres import (
    PostgresConnection,
    PostgresDictCursor,
    get_postgres_connection,
    get_postgres_dict_cursor,
)
from .snowflake import (
    SnowflakeConnection,
    SnowflakeDictCursor,
    get_snowflake_connection,
    get_snowflake_dict_cursor,
)


def get_connection(config: ConfigDict):
    connection_type = config["type"]
    if connection_type == "postgres":
        return get_postgres_connection(config)
    elif connection_type == "snowflake":
        return get_snowflake_connection(config)
    raise Exception(f"Unknown connection type: {connection_type}")


class Connector:
    def __init__(self, config_path: Optional[str], connection_name: str):
        config = get_config(config_path)
        self.connection_config = get_connection_from_config(config, connection_name)
        self.connection_type = self.connection_config["type"]
        self.conn = self.get_connection(self.connection_config)
        self.connection_name = connection_name
        self.connection_type = self.connection_config["type"]

    def get_connection(
        self, config: ConfigDict
    ) -> Union[PostgresConnection, SnowflakeConnection]:
        if self.is_postgres:
            return get_postgres_connection(config)
        elif self.is_snowflake:
            return get_snowflake_connection(config)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_dict_cursor(self) -> Union[PostgresDictCursor, SnowflakeDictCursor]:
        if self.is_postgres:
            return get_postgres_dict_cursor(self.conn)
        if self.is_snowflake:
            return get_snowflake_dict_cursor(self.conn)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_results(self, query: str) -> List[RowDict]:
        with self.get_dict_cursor() as dict_cursor:
            dict_cursor.execute(query)
            results = [dict(r) for r in dict_cursor.fetchall()]
            return results

    @property
    def is_postgres(self) -> bool:
        return self.connection_type == "postgres"

    @property
    def is_snowflake(self) -> bool:
        return self.connection_type == "snowflake"
