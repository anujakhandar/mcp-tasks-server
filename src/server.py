import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )

def list_tables():
    conn = get_connection()
    cursor = conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_schema(table: str):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
        (table,),
    )
    columns = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
    conn.close()
    return columns

def query(sql: str, params: tuple = ()):
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed")
    if ";" in sql.strip().rstrip(";"):
        raise ValueError("Multiple statements are not allowed")
    conn = get_connection()
    cursor = conn.execute(sql, params)
    columns = [desc.name for desc in cursor.description]
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