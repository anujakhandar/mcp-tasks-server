# Task Insight MCP Server

An MCP (Model Context Protocol) server that exposes a PostgreSQL `tasks` database as safe, structured tools and resources for LLM agents — so a model can answer natural-language questions about task data (completion rates, overdue work, workload distribution) without ever running unrestricted SQL.

Built on the official MCP Python SDK (FastMCP). Any MCP-compatible client — Claude Desktop, a custom LangChain agent, or the Anthropic SDK — can connect to this server and query the database through governed, typed tools instead of raw database access.

## Why this exists

Letting an LLM generate and run arbitrary SQL against a live database is a real risk: a bad prompt, an ambiguous question, or a deliberate injection attempt can produce a destructive query (`DROP`, `DELETE`, `UPDATE`) instead of a safe read. This project's core design decision is that **the model never writes free SQL against production data** — it can only call a fixed set of tested, typed tools, each with its own guardrails.

## Architecture

```
mcp-server/
  db.py            # connection handling, list_tables, get_schema, query, execute
  tools.py         # analytics functions built on top of query() — completion rate,
                    # overdue tasks, workload by assignee, productivity trend
  server.py        # FastMCP server: wires db.py + tools.py functions as @mcp.tool(),
                    # exposes schema as an MCP resource
  agent_client.py  # example client — connects to the server, takes a natural-language
                    # question, calls the right tool(s), summarizes the result
  dashboard.py      # Streamlit dashboard calling the same tools.py functions for charts
  .env.example      # required environment variables (no real credentials committed)
  README.md
```

## Guardrails

This project treats the database connection as untrusted-input-facing, since the calling agent (and by extension, whatever prompted it) is not a trusted human operator. Guardrails in place:

- **Read-only / mutation separation** — `query()` only executes `SELECT` statements. `execute()` is the sole path capable of `INSERT`/`UPDATE`/`DELETE`, and is never used by any analytics tool.
- **Parameterized queries throughout** — all values are passed as query parameters, never string-interpolated, preventing SQL injection.
- **Single-statement enforcement** — both `query()` and `execute()` reject inputs containing multiple statements (e.g. a `SELECT` followed by a stacked `DROP`), closing off statement-chaining attacks.
- **Confirmation required for mutations** — `execute()` requires an explicit `confirm=True` before running, so a mutation can never fire as an unintended side effect of a vague or misinterpreted request.
- **Least-privilege database user** — the Postgres role used by this server is granted only the permissions it needs (read access for analytics tools; no `DROP`/`ALTER`/`TRUNCATE` grants at the database level, regardless of what the application code calls).
- **Row limits on reads** — analytics queries cap the number of rows returned, preventing an unbounded query from exhausting resources.

These guardrails are enforced at the database-access layer (`db.py`), not the prompt layer — so they hold even if the LLM is manipulated into requesting something it shouldn't.

## Tools exposed

| Tool | Description |
|---|---|
| `list_tables()` | Lists all tables in the `public` schema |
| `get_schema(table)` | Returns column names and types for a given table |
| `task_completion_rate(assignee=None, period=None)` | % of tasks completed vs. overdue |
| `avg_completion_time(assignee=None)` | Average time-to-completion, overall or per assignee |
| `overdue_tasks(threshold_days=None)` | Currently overdue tasks past a given threshold |
| `workload_by_assignee()` | Task count distribution across assignees |
| `productivity_trend(period="week")` | Completions over time, for trend analysis |

## Resources exposed

- `schema://tasks` — the `tasks` table schema, so a client can inspect available fields before querying.

## Setup

```bash
git clone <repo-url>
cd mcp-server
pip install -r requirements.txt
cp .env.example .env   # fill in your Postgres credentials
```

`.env` requirements:
```
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

Run the server:
```bash
mcp run server.py
```

Connect it to Claude Desktop by adding it to your MCP client config, or run `agent_client.py` for a terminal demo.

## Example usage

```
> Which assignee has the most overdue tasks right now?
[calls overdue_tasks()] → "Priya has 6 tasks overdue by more than 3 days,
the most of any assignee this week."

> What's our task completion rate trending like over the last month?
[calls productivity_trend(period="week")] → generates a chart + summary of
week-over-week completion rate.
```

## Dashboard

`dashboard.py` runs a Streamlit app using the same analytics functions as the MCP tools, for a visual view of task completion trends and workload distribution — useful as a standalone report independent of any LLM client.

## Tech stack

Python · PostgreSQL · MCP Python SDK (FastMCP) · Streamlit · Plotly

## Future improvements

- Table/column allowlisting for an added layer of access control
- Query result caching for repeated questions
- Auth layer for multi-user deployments