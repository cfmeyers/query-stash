import os
import sqlite3
from os.path import expanduser
from typing import List

from query_stash.config import CONFIG_DIRECTORY

SQLITE_DB_PATH = expanduser(f"{CONFIG_DIRECTORY}/query-stash.db")

CREATE_TABLE_QUERY = """\
CREATE VIRTUAL TABLE queries USING fts5(
    query_text
    , results_as_table_text
    , tags
    , queried_at
    , db_connection_type
    , db_connection_name
);"""

INSERT_ROW_QUERY = """\
INSERT INTO queries (
    query_text
    , results_as_table_text
    , tags
    , db_connection_type
    , db_connection_name
    , queried_at
)
    VALUES (
        ?
        , ?
        , ?
        , ?
        , ?
        , CURRENT_TIMESTAMP
    );
"""


class QueryStasher:
    def __init__(self, sqlite_db_path: str = SQLITE_DB_PATH):
        self.sqlite_db_path = sqlite_db_path
        if not self.db_exists():
            self.create_db_and_table()

    def db_exists(self) -> bool:
        return os.path.isfile(self.sqlite_db_path)

    def get_sqlite_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.sqlite_db_path)

    def create_db_and_table(self):
        print(f"Creating SQLite database at {self.sqlite_db_path}")
        with self.get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_TABLE_QUERY)

    def stash(
        self,
        query: str,
        results: str,
        tags: str,
        db_connection_name: str,
        db_connection_type: str,
    ):
        with self.get_sqlite_conn() as conn:
            cursor = conn.cursor()
            params = (
                query,
                str(results),
                tags,
                db_connection_name,
                db_connection_type,
            )
            cursor.execute(INSERT_ROW_QUERY, params)
