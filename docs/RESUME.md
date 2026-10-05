# Resume-Ready Project Description

## Sales & Order Management Analytics System

**Tech:** Python, SQLite, SQL, Pandas, Matplotlib, Gradio, pytest, GitHub Actions, Docker

### Resume bullets

- Built a modular sales and order management application using Python, SQLite and Gradio to manage customers, products, orders, payments and inventory.
- Designed SQL-based analytics for revenue trends, category performance, top products, customer rankings, payment status and inventory insights using Pandas and Matplotlib.
- Implemented transaction-safe order processing with stock validation, automatic inventory updates, order cancellation, stock restoration and payment refund handling.
- Added search, filtering, order lifecycle management, low-stock monitoring, automated pytest checks, GitHub Actions CI and Docker deployment support.

### Interview explanation

**What problem does it solve?**

It simulates a small business sales system where users manage customers and products, create orders, track payments and analyze performance from one dashboard.

**Why SQLite?**

SQLite is lightweight and requires no separate database server, making it suitable for a student portfolio application. The database layer is isolated so it can later migrate to PostgreSQL or MySQL.

**Why transactions?**

An order changes multiple records. If order creation succeeds but a later database operation fails, the database could become inconsistent. A transaction ensures related changes succeed together or are rolled back.

**What would you improve next?**

For production, add authentication, role-based permissions, PostgreSQL, migrations, APIs, audit logs, monitoring and end-to-end tests.
