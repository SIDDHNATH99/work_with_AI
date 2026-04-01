"""
Postgres MCP Server
Exposes tools to query a PostgreSQL database.

Env vars:
    PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE
"""

import json
import os
import re
import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("postgres")

def _get_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "postgres"),
        dbname=os.getenv("PG_DATABASE", "CMS"),
    )


@mcp.tool()
def pg_query(sql: str) -> str:
    """Run a read-only SELECT or WITH query against the connected PostgreSQL database."""
    trimmed = sql.strip().upper()
    if not (trimmed.startswith("SELECT") or trimmed.startswith("WITH")):
        return "Error: Only SELECT / WITH queries are allowed for safety."
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return json.dumps({"rows": rows, "rowCount": len(rows)}, indent=2, default=str)
    except Exception as e:
        return f"Query error: {e}"


@mcp.tool()
def pg_list_tables() -> str:
    """List all tables in the connected PostgreSQL database."""
    sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name
    """
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def pg_describe_table(table_name: str) -> str:
    """Get column names, types, and nullability for a specific table."""
    sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (table_name,))
                rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        if not rows:
            return f"Table '{table_name}' not found or has no columns."
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def pg_count_rows(table_name: str) -> str:
    """Get the row count of a specific table."""
    if not re.match(r'^[a-zA-Z0-9_.]+$', table_name):
        return "Error: Invalid table name."
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cur.fetchone()[0]
        conn.close()
        return f"Table '{table_name}' has {count} rows."
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
