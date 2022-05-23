from typing import Any, MutableMapping

import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.connection import SnowflakeConnection

SnowflakeDictCursor = DictCursor


def get_snowflake_connection(config: MutableMapping[str, Any]) -> SnowflakeConnection:
    return snowflake.connector.connect(
        user=config["user"],
        password=config["password"],
        account=config["account"],
        database=config["database"],
        warehouse=config["warehouse"],
        role=config["role"],
        schema="INFORMATION_SCHEMA",
    )


def get_snowflake_dict_cursor(conn: SnowflakeConnection):
    return conn.cursor(DictCursor)


# conn = x
# y = conn.cursor(DictCursor)
# type(y)
