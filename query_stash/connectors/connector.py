from typing import List

from snowflake.connector.errors import ProgrammingError

from query_stash.config import get_config, get_connection_from_config
from query_stash.types import ConfigDict, RowDict

from .clickhouse import (
    ClickhouseConnection,
    ClickhouseDictCursor,
    get_clickhouse_connection,
    get_clickhouse_dict_cursor,
)
from .duckdb import (
    DuckDBDictCursor,
    DuckDBPyConnection,
    get_duckdb_connection,
    get_duckdb_dict_cursor,
)
from .mysql import MySQLConnection, get_mysql_connection, get_mysql_dict_cursor
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


class Connector:
    def __init__(self, config_path: str | None, connection_name: str):
        config = get_config(config_path)
        self.connection_config = get_connection_from_config(config, connection_name)
        self.connection_type = self.connection_config["type"]
        self.conn = self.get_connection(self.connection_config)
        self.connection_name = connection_name

    def get_connection(
        self, config: ConfigDict
    ) -> PostgresConnection | SnowflakeConnection | DuckDBPyConnection | MySQLConnection | ClickhouseConnection:
        if self.is_postgres:
            return get_postgres_connection(config)
        elif self.is_snowflake:
            return get_snowflake_connection(config)
        elif self.is_duckdb:
            return get_duckdb_connection(config)
        elif self.is_mysql:
            return get_mysql_connection(config)
        elif self.is_clickhouse:
            return get_clickhouse_connection(config)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_dict_cursor(
        self,
    ) -> PostgresDictCursor | SnowflakeDictCursor | DuckDBDictCursor | ClickhouseDictCursor:
        if self.is_postgres:
            return get_postgres_dict_cursor(self.conn)
        if self.is_snowflake:
            return get_snowflake_dict_cursor(self.conn)
        if self.is_duckdb:
            return get_duckdb_dict_cursor(self.conn)
        if self.is_mysql:
            return get_mysql_dict_cursor(self.conn)
        if self.is_clickhouse:
            return get_clickhouse_dict_cursor(self.conn)
        raise Exception(f"Unknown connection type: {self.connection_type}")

    def get_results(self, query: str) -> tuple[str | None, List[RowDict]]:
        with self.get_dict_cursor() as dict_cursor:
            try:
                dict_cursor.execute(query)
                results = [dict(r) for r in dict_cursor.fetchall()]
                return None, results
            except ProgrammingError as e:
                err = "\n".join([f"┆{x}┆" for x in str(e).split("\n")])
                return err, []

    @property
    def is_postgres(self) -> bool:
        return self.connection_type == "postgres"

    @property
    def is_snowflake(self) -> bool:
        return self.connection_type == "snowflake"

    @property
    def is_duckdb(self) -> bool:
        return self.connection_type == "duckdb"

    @property
    def is_mysql(self) -> bool:
        return self.connection_type == "mysql"

    @property
    def is_clickhouse(self) -> bool:
        return self.connection_type == "clickhouse"
