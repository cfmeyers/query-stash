from typing import Any, MutableMapping

import psycopg2
from psycopg2.extensions import connection as PostgresConnection
from psycopg2.extras import DictCursor as PostgresDictCursor


def get_postgres_connection(config: MutableMapping[str, Any]) -> PostgresConnection:
    return psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
    )


def get_postgres_dict_cursor(conn: PostgresConnection):
    return conn.cursor(cursor_factory=PostgresDictCursor)
