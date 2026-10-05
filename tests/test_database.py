import importlib
import os
import sqlite3


def test_database_initializes(tmp_path, monkeypatch):
    db_path = tmp_path / "test_sales.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    import database
    importlib.reload(database)

    tables = {
        row[0]
        for row in database.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    expected = {"customers", "products", "orders", "order_items", "payments"}
    assert expected.issubset(tables)


def test_foreign_keys_are_enabled(tmp_path, monkeypatch):
    db_path = tmp_path / "foreign_keys.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    import database
    importlib.reload(database)

    enabled = database.conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert enabled == 1
