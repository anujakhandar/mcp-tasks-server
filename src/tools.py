"""
Analytics functions for the tasks table. Every function here is read-only
and built entirely on db.query() - none of these ever call db.execute().
This is the layer that turns a generic database connector into an
analytics tool: each function answers one real business question.
"""
from db import query


def task_completion_rate(assignee: str = None, period_days: int = 30):
    """
    Percentage of tasks completed vs. overdue in the last `period_days` days,
    optionally filtered to one assignee.
    """
    sql = """
        SELECT
            COUNT(*) FILTER (WHERE status = 'completed') AS completed,
            COUNT(*) FILTER (WHERE status = 'overdue') AS overdue,
            COUNT(*) AS total
        FROM tasks
        WHERE created_at >= NOW() - (%s || ' days')::interval
    """
    params = [period_days]
    if assignee:
        sql += " AND assignee = %s"
        params.append(assignee)

    row = query(sql, tuple(params))[0]
    total = row["total"] or 1
    return {
        "assignee": assignee or "all",
        "period_days": period_days,
        "completed": row["completed"],
        "overdue": row["overdue"],
        "completion_rate_pct": round(100 * row["completed"] / total, 1),
    }


def avg_completion_time(assignee: str = None):
    """Average days between task creation and completion, overall or per assignee."""
    sql = """
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400) AS avg_days
        FROM tasks
        WHERE status = 'completed'
    """
    params = []
    if assignee:
        sql += " AND assignee = %s"
        params.append(assignee)

    row = query(sql, tuple(params))[0]
    return {"assignee": assignee or "all", "avg_completion_days": round(row["avg_days"] or 0, 1)}


def overdue_tasks(threshold_days: int = 3, limit: int = 20):
    """List tasks overdue by more than `threshold_days`, most overdue first."""
    sql = """
        SELECT id, title, assignee, due_date,
               EXTRACT(DAY FROM NOW() - due_date) AS days_overdue
        FROM tasks
        WHERE status != 'completed' AND due_date < NOW() - (%s || ' days')::interval
        ORDER BY due_date ASC
        LIMIT %s
    """
    return query(sql, (threshold_days, limit))


def workload_by_assignee():
    """Count of active (non-completed) tasks per assignee, descending."""
    sql = """
        SELECT assignee, COUNT(*) AS active_tasks
        FROM tasks
        WHERE status != 'completed'
        GROUP BY assignee
        ORDER BY active_tasks DESC
    """
    return query(sql)


def productivity_trend(period: str = "week", weeks_back: int = 8):
    """Completions per period (week/day) over the last N periods, for trend charting."""
    bucket = "week" if period == "week" else "day"
    sql = f"""
        SELECT date_trunc('{bucket}', completed_at) AS period_start, COUNT(*) AS completed
        FROM tasks
        WHERE status = 'completed' AND completed_at >= NOW() - (%s || ' weeks')::interval
        GROUP BY period_start
        ORDER BY period_start
    """
    return query(sql, (weeks_back,))