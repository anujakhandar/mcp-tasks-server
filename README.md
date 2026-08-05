# sqlite-mcp-server

MCP server exposing a local SQLite `tasks` database as tools/resources for LLM agents.

## Status
Scaffolding only — server logic not yet implemented.

## Planned interface
- Resource: `list_tables`
- Tools:
  - `get_schema(table)`
  - `query(sql)` — read-only (SELECT)
  - `execute(sql)` — INSERT/UPDATE/DELETE

## Setup
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Data
`data/tasks.db` — seeded SQLite db with a `tasks` table (id, title, priority, status, due_date, created_at).
