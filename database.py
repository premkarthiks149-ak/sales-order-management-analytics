import sqlite3
from datetime import date

DB_NAME = "sales_analytics.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


conn = get_connection()


def initialize_database():
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        city TEXT,
        signup_date TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT,
        status TEXT,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_date TEXT,
        amount REAL,
        payment_status TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """)
    conn.commit()


def seed_sample_data():
    customer_count = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    if customer_count != 0:
        return

    customers = [
        ("Rahul", "rahul@gmail.com", "Chennai", "2026-01-10"),
        ("Priya", "priya@gmail.com", "Bangalore", "2026-01-15"),
        ("Arun", "arun@gmail.com", "Chennai", "2026-02-05"),
        ("Divya", "divya@gmail.com", "Coimbatore", "2026-02-12")
    ]

    products = [
        ("Laptop", "Electronics", 50000, 20),
        ("Headphones", "Electronics", 2000, 50),
        ("Keyboard", "Accessories", 1500, 40),
        ("Mouse", "Accessories", 800, 60),
        ("Monitor", "Electronics", 12000, 15)
    ]

    conn.executemany(
        "INSERT INTO customers(name,email,city,signup_date) VALUES (?,?,?,?)",
        customers
    )
    conn.executemany(
        "INSERT INTO products(product_name,category,price,stock) VALUES (?,?,?,?)",
        products
    )

    sample_orders = [
        (1, "2026-01-20", "COMPLETED", 52000),
        (2, "2026-01-25", "COMPLETED", 3500),
        (1, "2026-02-10", "COMPLETED", 2800),
        (3, "2026-02-15", "COMPLETED", 50000)
    ]

    conn.executemany(
        "INSERT INTO orders(customer_id,order_date,status,total_amount) VALUES (?,?,?,?)",
        sample_orders
    )

    items = [
        (1, 1, 1, 50000),
        (1, 2, 1, 2000),
        (2, 2, 1, 2000),
        (2, 3, 1, 1500),
        (3, 2, 1, 2000),
        (3, 4, 1, 800),
        (4, 1, 1, 50000)
    ]

    conn.executemany(
        "INSERT INTO order_items(order_id,product_id,quantity,unit_price) VALUES (?,?,?,?)",
        items
    )

    payments = [
        (1, "2026-01-20", 52000, "PAID"),
        (2, "2026-01-25", 3500, "PAID"),
        (3, "2026-02-10", 2800, "PAID"),
        (4, "2026-02-15", 50000, "PAID")
    ]

    conn.executemany(
        "INSERT INTO payments(order_id,payment_date,amount,payment_status) VALUES (?,?,?,?,?)",
        []
    )
    conn.executemany(
        "INSERT INTO payments(order_id,payment_date,amount,payment_status) VALUES (?,?,?,?)",
        payments
    )

    for _, product_id, quantity, _ in items:
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE product_id = ?",
            (quantity, product_id)
        )

    conn.commit()


initialize_database()
seed_sample_data()
