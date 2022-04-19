import pytest
from pytest import fixture

from query_stash.config import (ConfigException, get_config,
                                get_connection_from_config)


class TestGetConfig:
    def test_it_can_take_an_optional_config_path(self):
        it = get_config(config_path="./tests/test-config.toml")
        assert it == {
            "connections": {
                "dbt-postgres": {
                    "type": "postgres",
                    "host": "localhost",
                    "user": "postgres",
                    "password": "postgres",
                    "port": 5432,
                    "dbname": "jaffle_shop",
                }
            }
        }


class TestGetConnectionFromConfig:
    @fixture
    def single_connection_config(self):
        return {
            "connections": {
                "dbt-postgres": {
                    "type": "postgres",
                    "host": "localhost",
                    "user": "postgres",
                    "password": "postgres",
                    "port": 5432,
                    "dbname": "jaffle_shop",
                }
            }
        }

    @fixture
    def two_connection_config(self):
        return {
            "connections": {
                "dbt-postgres": {
                    "type": "postgres",
                    "host": "localhost",
                    "user": "postgres",
                    "password": "postgres",
                    "port": 5432,
                    "dbname": "jaffle_shop",
                },
                "dbt-bigquery": {
                    "type": "bigquery",
                    "user": "bq",
                    "password": "bq",
                    "dbname": "jaffle_shop",
                },
            }
        }

    def test_it_gets_a_config_from_passed_connection(self, single_connection_config):
        it = get_connection_from_config(single_connection_config, "dbt-postgres")
        assert it == {
            "type": "postgres",
            "host": "localhost",
            "user": "postgres",
            "password": "postgres",
            "port": 5432,
            "dbname": "jaffle_shop",
        }

    def test_it_returns_a_connection_if_no_connection_specified(
        self, single_connection_config
    ):
        it = get_connection_from_config(single_connection_config)
        assert it == {
            "type": "postgres",
            "host": "localhost",
            "user": "postgres",
            "password": "postgres",
            "port": 5432,
            "dbname": "jaffle_shop",
        }

    def test_it_errors_if_no_connection_specified_and_multiple_connections_exist(
        self, two_connection_config
    ):
        with pytest.raises(ConfigException):
            it = get_connection_from_config(two_connection_config)
