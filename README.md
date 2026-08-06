# postgres-mcp-server

MCP server exposing a PostgreSQL `tasks` database as tools/resources for LLM agents.

## Status
Core functions implemented: `get_connection`, `list_tables`, `get_schema`, `query`, `execute`.
Not yet wired up as MCP tools via the SDK — that's next.

## Functions

- `get_connection()` — connects to Postgres using credentials from `.env`
- `list_tables()` — returns all table names in the `public` schema
- `get_schema(table)` — returns column names and types for a given table
- `query(sql, params=())` — read-only SELECT, parameterized, rejects multiple statements
- `execute(sql, params=(), confirm=True)` — INSERT/UPDATE/DELETE, parameterized, requires confirmation, rejects multiple statements

## Setup
```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create a `.env` file (see `.env` example in repo docs — not committed) with your Postgres connection details.

## Next steps
- Create the `tasks` table in your Postgres database
- Wire functions up as MCP tools using the SDK's `@server.tool()` decorators
- Test with the MCP inspector