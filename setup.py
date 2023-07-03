#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "Click>=6.0",
    "toml==0.9.0",
    "psycopg2-binary==2.9.3",
    "snowflake-connector-python==2.7.7",
    "duckdb==0.7.1",
    "pandas==2.0.2",
    "numpy==1.24.3",
    "mysql-connector-python==8.0.33",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest",
]

setup(
    author="Collin Meyers",
    author_email="cfmeyers@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description="Query databases and keep a record of your results",
    entry_points={
        "console_scripts": [
            "query-stash=query_stash.cli:cli",
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="query_stash",
    name="query_stash",
    packages=find_packages(include=["query_stash"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/cfmeyers/query-stash",
    version="0.1.0",
    zip_safe=False,
)
