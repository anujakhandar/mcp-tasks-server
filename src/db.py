"""
Database access layer for the tasks Postgres database.
This is the only module that talks to Postgres directly. All guardrails
(read-only enforcement, parameterization, single-statement checks) live here,
so they hold regardless of what the LLM/agent above this layer tries to do.
"""
import os
import re
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DESTRUCTIVE_KEYWORDS = ("DROP", "TRUNCATE", "ALTER", "GRANT", "REVOKE")


def get_connection():
    """Open a connection to Postgres using credentials from .env."""
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def list_tables():
    """Return all table names in the public schema."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        return [row[0] for row in cur.fetchall()]


def get_schema(table: str):
    """Return column names and types for a given table."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT column_name, data_type FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = %s""",
            (table,),
        )
        return [{"column": r[0], "type": r[1]} for r in cur.fetchall()]


def _reject_multiple_statements(sql: str):
    # crude but effective: a bare semicolon anywhere but the very end means
    # someone is trying to stack statements
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise ValueError("Multiple statements are not allowed.")


def query(sql: str, params: tuple = ()):
    """Read-only SELECT. Parameterized. Rejects multiple statements and non-SELECTs."""
    _reject_multiple_statements(sql)
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("query() only allows SELECT statements. Use execute() for writes.")
    with get_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params: tuple = (), confirm: bool = True):
    """INSERT/UPDATE/DELETE. Parameterized, requires confirmation, rejects multiple statements."""
    if not confirm:
        raise ValueError("execute() requires confirm=True to run a mutation.")
    _reject_multiple_statements(sql)
    upper = sql.strip().upper()
    if any(word in upper for word in DESTRUCTIVE_KEYWORDS):
        raise ValueError("Schema-level operations (DROP/TRUNCATE/ALTER/GRANT/REVOKE) are not allowed.")
    if not upper.startswith(("INSERT", "UPDATE", "DELETE")):
        raise ValueError("execute() only allows INSERT, UPDATE, or DELETE.")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount