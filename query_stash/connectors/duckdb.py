from typing import Any, MutableMapping

import duckdb
import pandas as pd
from duckdb import DuckDBPyConnection

from query_stash.types import RowDict


def get_duckdb_connection(config: MutableMapping[str, Any]) -> DuckDBPyConnection:
    return duckdb.connect(database=config["path"])


def datetime_series_should_be_date(series):
    series = series.copy().dropna()  # create a copy and drop NaT values
    return (
        (series.dt.hour == 0).all()
        and (series.dt.minute == 0).all()
        and (series.dt.second == 0).all()
    )


def force_dates_to_be_dates_in_dataframe(df):
    for col in df.columns:
        if df[col].dtype in ("datetime64[ns]", "datetime64[us]"):
            if datetime_series_should_be_date(df[col]):
                df[col] = df[col].dt.date
    return df


def all_vals_in_col_are_ints(series: pd.Series) -> bool:
    if series.dtype == float:
        return (series.fillna(0).astype(int) == series).all()
    else:
        return False


def force_ints_to_be_ints_in_dataframe(df):
    for col in df.columns:
        if all_vals_in_col_are_ints(df[col]):
            df[col] = df[col].astype(int)
    return df


class DuckDBDictCursor:
    """A hack because duckdb doesn't have a dict cursor"""

    def __init__(self, conn: DuckDBPyConnection):
        self.conn = conn

    def execute(self, query: str):
        self.conn.execute(query)

    def fetchall(self) -> list[RowDict]:
        result_df = self.conn.df()
        result_df = force_ints_to_be_ints_in_dataframe(result_df)
        result_df = force_dates_to_be_dates_in_dataframe(result_df)
        # get rid of NaNs which messes up guessing column datatypes
        result_df = result_df.where(result_df.notnull(), None)
        records = result_df.to_dict("records")
        return records

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def get_duckdb_dict_cursor(conn: DuckDBPyConnection):
    return DuckDBDictCursor(conn)


if __name__ == "__main__":
    query = "SELECT CURRENT_DATE AS today"
    conn = duckdb.connect(database="/Users/collin/explore/esg/esg.duckdb")
    conn.execute(query)
    df = conn.df()
    df
    raw_results = conn.fetchall()
    type(raw_results)
    print(raw_results[0])
    raw_results
    df.iloc[0]

    conn.close()
