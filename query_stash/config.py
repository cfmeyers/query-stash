from os.path import expanduser
from typing import Any, Optional

import toml

from query_stash.types import ConfigDict

DEFAULT_CONFIG_PATH = "~/.query-stash.toml"


class ConfigException(Exception):
    pass


def get_config(config_path: Optional[str] = None) -> ConfigDict:
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    with open(expanduser(config_path)) as conf_file:
        config = toml.loads(conf_file.read())
    return config


def get_connection_from_config(config: ConfigDict, connection: Optional[str] = None):
    if connection is not None:
        return config["connections"][connection]
    elif len(config["connections"].keys()) == 1:
        return list(config["connections"].values())[0]
    else:
        raise ConfigException("You need to specify a connection")
