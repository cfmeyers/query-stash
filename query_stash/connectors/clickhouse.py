from typing import Any, MutableMapping

from clickhouse_driver import connect
from clickhouse_driver.dbapi.connection import \
    Connection as ClickhouseConnection
from clickhouse_driver.dbapi.extras import DictCursor as ClickhouseDictCursor


def get_clickhouse_connection(config: MutableMapping[str, Any]) -> ClickhouseConnection:
    if config.get("password"):
        return connect(
            database=config["dbname"],
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
        )

    return connect(
        database=config["dbname"],
        host=config["host"],
        port=config["port"],
        user=config["user"],
    )


def get_clickhouse_dict_cursor(conn: ClickhouseConnection) -> ClickhouseDictCursor:
    return conn.cursor(cursor_factory=ClickhouseDictCursor)
