import sqlite3

DB_PATH = "data/tasks.db"

def get_connection():
    return sqlite3.connect(DB_PATH)


def list_tables():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def query(sql: str):
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed")
    conn = get_connection()
    cursor = conn.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return rows

def execute(sql: str, confirm: bool = False):
    forbidden = ("SELECT",)
    if sql.strip().upper().startswith(forbidden):
        raise ValueError("Use query() for SELECT statements")
    if not confirm:
        raise ValueError("Destructive operation requires confirm=True")
    conn = get_connection()
    cursor = conn.execute(sql)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return {"rows_affected": affected}