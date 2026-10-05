import importlib

import database
import analytics


def _reload_with_demo_data(monkeypatch, tmp_path):
    db_path = tmp_path / "analytics_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    db = importlib.reload(database)
    analytics_module = importlib.reload(analytics)
    return db, analytics_module


def test_monthly_revenue(monkeypatch, tmp_path):
    _, a = _reload_with_demo_data(monkeypatch, tmp_path)
    df = a.monthly_revenue()
    assert list(df["month"]) == ["2026-01", "2026-02"]
    assert list(df["revenue"]) == [55500.0, 52800.0]


def test_category_revenue(monkeypatch, tmp_path):
    _, a = _reload_with_demo_data(monkeypatch, tmp_path)
    df = a.category_revenue()
    assert df.iloc[0]["category"] == "Electronics"
    assert df.iloc[0]["revenue"] == 106000.0
    assert df.iloc[1]["category"] == "Accessories"
    assert df.iloc[1]["revenue"] == 2300.0


def test_top_product(monkeypatch, tmp_path):
    _, a = _reload_with_demo_data(monkeypatch, tmp_path)
    df = a.top_products()
    assert df.iloc[0]["product_name"] == "Laptop"
    assert df.iloc[0]["revenue"] == 100000.0
    assert df.iloc[0]["units_sold"] == 2
