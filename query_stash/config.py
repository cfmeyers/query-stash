import os
import sys
from os.path import expanduser
from pathlib import Path

import toml

from query_stash.types import ConfigDict

CONFIG_DIRECTORY = "~/.config/query-stash"
DEFAULT_CONFIG_PATH = f"{CONFIG_DIRECTORY}/query-stash.toml"


class ConfigException(Exception):
    pass


def get_config(config_path: str | None = None) -> ConfigDict:
    make_config_directory_if_not_exists()
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    try:
        with open(expanduser(config_path)) as conf_file:
            config = toml.loads(conf_file.read())
    except FileNotFoundError:
        print(f"Could not find config file {expanduser(config_path)}")
        print(
            """Make a toml config file at that location.  Example:
[connections]
    [connections.dbt-postgres]
    type = "postgres"
    host = "localhost"
    user = "postgres"
    password = "postgres"
    port = 5432
    dbname = "jaffle_shop"

    [connections.duckdb-jaffle]
    type = "duckdb"
    path = "~/src/github.com/dbt-labs/jaffle_shop_duckdb/jaffle_shop.duckdb" """
        )
        sys.exit(1)
    return config


def get_connection_from_config(config: ConfigDict, connection: str | None = None):
    if connection is not None:
        return config["connections"][connection]
    elif len(config["connections"].keys()) == 1:
        return list(config["connections"].values())[0]
    else:
        raise ConfigException("You need to specify a connection")


def config_directory_exists() -> bool:
    return os.path.isdir(expanduser(CONFIG_DIRECTORY))


def make_config_directory_if_not_exists():
    if not config_directory_exists():
        print("Query stash config directory does not yet exist.")
        print(f"Creating directory at {CONFIG_DIRECTORY}")
        Path(expanduser(CONFIG_DIRECTORY)).mkdir(parents=True, exist_ok=True)
