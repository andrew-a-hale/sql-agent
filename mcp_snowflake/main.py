import os

import snowflake.connector as sc
from mcp.server.fastmcp import FastMCP


key_file = os.getenv("SNOWFLAKE_PRIVATE_KEY_FILE")
assert key_file, "SNOWFLAKE_PRIVATE_KEY_FILE environment variable must be set"

conn = sc.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    private_key_file=key_file,
)
mcp = FastMCP("snowflake")


@mcp.tool()
def get_databases() -> list[dict[str, str]]:
    """Get List of Snowflake Databases"""
    cur = conn.cursor()
    res = cur.execute("""\
select *
from snowflake.information_schema.databases""").fetchall()

    return [
        {
            "name": row[0],
            "comment": row[3],
            "time_travel_retention_in_days": row[6],
            "created": row[4].strftime("%F"),
            "last_altered": row[5].strftime("%F"),
        }
        for row in res
    ]


@mcp.tool()
def get_schemas(database: str) -> list[dict[str, str]]:
    """Get List of Snowflake Schemas in a Database"""
    cur = conn.cursor()
    res = cur.execute(
        f"select * from {database}.information_schema.schemata where created is not null"
    ).fetchall()

    if len(res) == 0:
        return [{}]

    return [
        {
            "name": row[1],
            "comment": row[12],
            "time_travel_retention_in_days": row[5],
            "created": row[10].strftime("%F"),
            "last_altered": row[11].strftime("%F"),
        }
        for row in res
    ]


@mcp.tool()
def get_tables(database: str, db_schema: str) -> list[dict[str, str]]:
    """Get List of Snowflake Tables in a Database Schema"""
    cur = conn.cursor()
    res = cur.execute(
        f"""\
select *
from {database}.information_schema.tables
where table_schema = %s""",
        (db_schema,),
    ).fetchall()

    if len(res) == 0:
        return [{}]

    return [
        {
            "name": row[2],
            "comment": row[23],
            "is_dynamic": row[26],
            "time_travel_retention_in_days": row[9],
            "created": row[18].strftime("%F"),
            "last_altered": row[19].strftime("%F"),
        }
        for row in res
    ]


@mcp.tool()
def execute_ddl_statement(ddl: str) -> dict[str, str]:
    """Execute a DDL Statement to create objects in Snowflake"""
    cur = conn.cursor()
    cur.execute(ddl).fetchall()

    return {"status": "success"}


@mcp.tool()
def get_view_ddl() -> dict[str, str]:
    """Get DDL for a View in a Database Schema"""
    cur = conn.cursor()
    res = cur.execute(
        "select table_name, view_definition from snowflake.information_schema.views",
    ).fetchall()

    if len(res) == 0:
        return {}

    row = res[0]

    return {
        "name": row[0],
        "definition": row[1],
    }


@mcp.tool()
def get_procedure_ddl() -> dict[str, str]:
    """Get DDL for a Stored Procedure in a Database Schema"""
    cur = conn.cursor()
    res = cur.execute(
        "select table_name, _definition from snowflake.information_schema.procedures",
    ).fetchall()

    if len(res) == 0:
        return {}

    row = res[0]

    return {
        "name": row[0],
        "definition": row[1],
    }


if __name__ == "__main__":
    mcp.run()
