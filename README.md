# query-stash

Query databases and keep a record of your results

## Example TOML config file

```toml

[connections]

    [connections.dbt-postgres]
    type = "postgres"
    host = "localhost"
    user = "postgres"
    password = "postgres"
    port = 5432
    dbname = "jaffle_shop"

    [connections.dbt-snowflake]
    type = "snowflake"
    account = "sna80999.us-east-1"
    user = "CMEYERS"
    password = "<YOUR PASSWORD HERE>"
    role = "DATA_ENGINEER_ROLE"
    database = "DEV"
    warehouse = "DATA_ENGINEER_WH"

    [connections.duckdb-jaffle]
    type = "duckdb"
    path = "/Users/CMeyers/src/github.com/dbt-labs/jaffle_shop_duckdb/jaffle_shop.duckdb"
```
