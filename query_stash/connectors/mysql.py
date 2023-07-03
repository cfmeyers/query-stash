from typing import Any, MutableMapping

from mysql.connector import MySQLConnection, connect


def get_mysql_connection(config: MutableMapping[str, Any]) -> MySQLConnection:
    conn = connect(
        database=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
    )
    return conn


def get_mysql_dict_cursor(conn: MySQLConnection):
    return conn.cursor(dictionary=True)
