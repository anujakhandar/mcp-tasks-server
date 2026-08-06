import sqlite3
import os

DB_PATH = "data/tasks.db"

def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def list_tables():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_schema(table: str):
    conn = get_connection()
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
    conn.close()
    return columns

def query(sql: str, params: tuple = ()):
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed")
    if ";" in sql.strip().rstrip(";"):
        raise ValueError("Multiple statements are not allowed")
    conn = get_connection()
    cursor = conn.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return rows

def execute(sql: str, params: tuple = (), confirm: bool = False):
    if sql.strip().upper().startswith("SELECT"):
        raise ValueError("Use query() for SELECT statements")
    if ";" in sql.strip().rstrip(";"):
        raise ValueError("Multiple statements are not allowed")
    if not confirm:
        raise ValueError("Destructive operation requires confirm=True")
    conn = get_connection()
    cursor = conn.execute(sql, params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return {"rows_affected": affected}