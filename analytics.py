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

    inventory_value = conn.execute(
        "SELECT COALESCE(SUM(price * stock),0) FROM products"
    ).fetchone()[0]

    return (
        f"₹{total_revenue:,.2f}",
        str(total_orders),
        str(total_customers),
        str(total_products),
        f"₹{avg_order:,.2f}",
        f"₹{inventory_value:,.2f}"
    )


def monthly_revenue():
    query = """
    SELECT substr(order_date,1,7) AS month,
           ROUND(SUM(total_amount),2) AS revenue
    FROM orders
    WHERE status='COMPLETED'
    GROUP BY substr(order_date,1,7)
    ORDER BY month
    """
    return pd.read_sql_query(query, conn)


def daily_sales():
    query = """
    SELECT order_date AS date,
           COUNT(order_id) AS orders,
           ROUND(SUM(total_amount),2) AS revenue
    FROM orders
    WHERE status='COMPLETED'
    GROUP BY order_date
    ORDER BY order_date
    """
    return pd.read_sql_query(query, conn)


def category_revenue():
    query = """
    SELECT COALESCE(p.category, 'Uncategorized') AS category,
           SUM(oi.quantity) AS units_sold,
           ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status='COMPLETED'
    GROUP BY p.category
    ORDER BY revenue DESC
    """
    return pd.read_sql_query(query, conn)


def top_products():
    query = """
    SELECT p.product_name,
           SUM(oi.quantity) AS units_sold,
           ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status='COMPLETED'
    GROUP BY p.product_id, p.product_name
    ORDER BY revenue DESC
    LIMIT 10
    """
    return pd.read_sql_query(query, conn)


def customer_ranking():
    query = """
    SELECT c.name AS customer,
           COUNT(o.order_id) AS total_orders,
           ROUND(SUM(o.total_amount),2) AS revenue
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status='COMPLETED'
    GROUP BY c.customer_id, c.name
    ORDER BY revenue DESC
    """
    return pd.read_sql_query(query, conn)


def payment_status_analysis():
    query = """
    SELECT payment_status,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount),2) AS amount
    FROM payments
    GROUP BY payment_status
    ORDER BY amount DESC
    """
    return pd.read_sql_query(query, conn)


def order_status_analysis():
    query = """
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(COALESCE(SUM(total_amount),0),2) AS revenue
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC
    """
    return pd.read_sql_query(query, conn)


def inventory_analysis():
    query = """
    SELECT product_name,
           category,
           stock,
           price,
           ROUND(stock * price,2) AS inventory_value
    FROM products
    ORDER BY inventory_value DESC
    """
    return pd.read_sql_query(query, conn)


def low_stock_products(threshold=10):
    query = """
    SELECT product_id, product_name, category, stock, price
    FROM products
    WHERE stock <= ?
    ORDER BY stock ASC
    """
    return pd.read_sql_query(query, conn, params=(threshold,))


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


def category_chart():
    df = category_revenue()
    fig, ax = plt.subplots(figsize=(8, 4))

    if len(df) > 0:
        ax.bar(df["category"], df["revenue"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Revenue")
        ax.set_title("Revenue by Category")
        ax.tick_params(axis="x", rotation=30)
    else:
        ax.text(0.5, 0.5, "No category data", ha="center", va="center")

    plt.tight_layout()
    return fig
