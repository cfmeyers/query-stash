#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `query_stash` package."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from query_stash import cli, query_stash
from query_stash.cli import query
from query_stash.render import get_rendered_table


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0


@pytest.fixture
def rendered_table():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return get_rendered_table([{"id": 1, "groups": 27596962761}])


@patch("query_stash.cli.connect_and_query_db")
def test_command_query(patched_connect_and_query_db, rendered_table):
    """Test the CLI."""
    patched_connect_and_query_db.return_value = rendered_table
    runner = CliRunner()
    result = runner.invoke(
        cli.query, ["select * from dbt_collin.raw_customers limit 8"]
    )
    assert result.output == str(rendered_table) + "\n"
    assert result.exit_code == 0
