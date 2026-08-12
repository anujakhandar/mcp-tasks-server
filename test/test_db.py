import pytest

from src.db import query, execute


def test_query_rejects_drop():
    """query() should reject DROP statements."""
    with pytest.raises(ValueError):
        query("DROP TABLE users;")


def test_query_rejects_delete():
    """query() should reject DELETE statements."""
    with pytest.raises(ValueError):
        query("DELETE FROM users;")


def test_query_rejects_update():
    """query() should reject UPDATE statements."""
    with pytest.raises(ValueError):
        query("UPDATE users SET name = 'test';")


def test_query_allows_select():
    """query() should allow read-only SELECT queries."""
    result = query("SELECT 1;")

    assert result is not None


def test_execute_requires_confirmation():
    """execute() should require explicit confirmation."""
    with pytest.raises(ValueError):
        execute("CREATE TABLE test_table (id INT);", confirm=False)


def test_execute_allows_confirmed_query():
    """execute() should run when confirmation is explicitly provided."""
    result = execute(
        "CREATE TEMP TABLE test_table (id INT);",
        confirm=True
    )

    assert result is not None