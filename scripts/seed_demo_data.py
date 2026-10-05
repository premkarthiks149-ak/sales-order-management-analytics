from database import conn

print("Demo dataset is ready.")
for table in ["customers", "products", "orders", "order_items", "payments"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")
