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

