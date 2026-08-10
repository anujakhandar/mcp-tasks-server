"""
Task Insights MCP Server
Exposes read-only task analytics as MCP tools, plus schema introspection
as an MCP resource. This is the only file that talks to the MCP SDK -
db.py and tools.py stay plain Python so they're easy to test on their own.
"""
from mcp.server.fastmcp import FastMCP

import db
import tools

mcp = FastMCP("task-insights")


# --- Schema / discovery tools -----------------------------------------

@mcp.tool()
def list_tables() -> list[str]:
    """List all tables available in the tasks database."""
    return db.list_tables()


@mcp.tool()
def get_schema(table: str) -> list[dict]:
    """Get column names and types for a given table."""
    return db.get_schema(table)


# --- Analytics tools -----------------------------------------------------

@mcp.tool()
def task_completion_rate(assignee: str = None, period_days: int = 30) -> dict:
    """
    Get the percentage of tasks completed vs overdue over a given period.
    Optionally filter to a single assignee by name.
    """
    return tools.task_completion_rate(assignee, period_days)


@mcp.tool()
def avg_completion_time(assignee: str = None) -> dict:
    """Get the average number of days tasks take to complete, overall or per assignee."""
    return tools.avg_completion_time(assignee)


@mcp.tool()
def overdue_tasks(threshold_days: int = 3, limit: int = 20) -> list[dict]:
    """List currently overdue tasks past a given number of days, most overdue first."""
    return tools.overdue_tasks(threshold_days, limit)


@mcp.tool()
def workload_by_assignee() -> list[dict]:
    """Get the count of active (non-completed) tasks per assignee, descending."""
    return tools.workload_by_assignee()


@mcp.tool()
def productivity_trend(period: str = "week", weeks_back: int = 8) -> list[dict]:
    """Get task completions per period (week or day) over recent history, for trend analysis."""
    return tools.productivity_trend(period, weeks_back)


# --- Resources -------------------------------------------------------------

@mcp.resource("schema://tasks")
def tasks_schema() -> list[dict]:
    """The tasks table schema, so a client can inspect fields before querying."""
    return db.get_schema("tasks")


if __name__ == "__main__":
    mcp.run()