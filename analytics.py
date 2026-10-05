import pandas as pd
import matplotlib.pyplot as plt

from database import conn


def get_customers():
    return pd.read_sql_query(
        "SELECT * FROM customers ORDER BY customer_id", conn
    )


def get_products():
    return pd.read_sql_query(
        "SELECT * FROM products ORDER BY product_id", conn
    )


def get_orders():
    query = """
    SELECT o.order_id, c.name AS customer, o.order_date,
           o.status, o.total_amount
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    ORDER BY o.order_id DESC
    """
    return pd.read_sql_query(query, conn)


def get_payments():
    query = """
    SELECT p.payment_id, p.order_id, c.name AS customer,
           p.payment_date, p.amount, p.payment_status
    FROM payments p
    JOIN orders o ON o.order_id = p.order_id
    JOIN customers c ON c.customer_id = o.customer_id
    ORDER BY p.payment_id DESC
    """
    return pd.read_sql_query(query, conn)


def dashboard_metrics():
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='COMPLETED'"
    ).fetchone()[0]

    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    avg_order = conn.execute(
        "SELECT COALESCE(AVG(total_amount),0) FROM orders WHERE status='COMPLETED'"
    ).fetchone()[0]

    return (
        f"₹{total_revenue:,.2f}",
        str(total_orders),
        str(total_customers),
        str(total_products),
        f"₹{avg_order:,.2f}"
    )


def monthly_revenue():
    query = """
    SELECT substr(order_date,1,7) AS month,
           SUM(total_amount) AS revenue
    FROM orders
    WHERE status='COMPLETED'
    GROUP BY substr(order_date,1,7)
    ORDER BY month
    """
    return pd.read_sql_query(query, conn)


def top_products():
    query = """
    SELECT p.product_name,
           SUM(oi.quantity) AS units_sold,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY revenue DESC
    LIMIT 10
    """
    return pd.read_sql_query(query, conn)


def customer_ranking():
    query = """
    SELECT c.name AS customer,
           COUNT(o.order_id) AS total_orders,
           SUM(o.total_amount) AS revenue
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status='COMPLETED'
    GROUP BY c.customer_id, c.name
    ORDER BY revenue DESC
    """
    return pd.read_sql_query(query, conn)


def sales_chart():
    df = monthly_revenue()
    fig, ax = plt.subplots(figsize=(8, 4))

    if len(df) > 0:
        ax.bar(df["month"], df["revenue"])
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        ax.set_title("Monthly Revenue")
        ax.tick_params(axis="x", rotation=45)
    else:
        ax.text(0.5, 0.5, "No sales data", ha="center", va="center")

    plt.tight_layout()
    return fig
