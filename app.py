import sqlite3
from datetime import date

import gradio as gr

from database import conn
from analytics import (
    get_customers, get_products, get_orders, get_payments,
    dashboard_metrics, monthly_revenue, daily_sales, category_revenue,
    top_products, customer_ranking, payment_status_analysis,
    order_status_analysis, inventory_analysis, low_stock_products,
    sales_chart, category_chart, order_details
)


def add_customer(name, email, city):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    city = (city or "").strip()

    if not name:
        return "Please enter customer name.", get_customers()

    if not email or "@" not in email:
        return "Please enter a valid email.", get_customers()

    try:
        conn.execute(
            """INSERT INTO customers(name,email,city,signup_date)
               VALUES (?,?,?,?)""",
            (name, email, city, str(date.today()))
        )
        conn.commit()
        return "Customer added successfully!", get_customers()
    except sqlite3.IntegrityError:
        return "Email already exists.", get_customers()


def add_product(product_name, category, price, stock):
    product_name = (product_name or "").strip()
    category = (category or "").strip()

    if not product_name:
        return "Please enter product name.", get_products()

    try:
        price = float(price)
        stock = int(stock)

        if price <= 0 or stock < 0:
            return "Price must be greater than 0 and stock cannot be negative.", get_products()

        conn.execute(
            """INSERT INTO products(product_name,category,price,stock)
               VALUES (?,?,?,?)""",
            (product_name, category, price, stock)
        )
        conn.commit()
        return "Product added successfully!", get_products()
    except (ValueError, TypeError):
        return "Enter valid price and stock values.", get_products()


def customer_choices():
    df = get_customers()
    return [f"{r.customer_id} - {r.name}" for _, r in df.iterrows()]


def product_choices():
    df = get_products()
    return [
        f"{r.product_id} - {r.product_name} (Stock: {r.stock})"
        for _, r in df.iterrows()
    ]


def refresh_choices():
    return (
        gr.update(choices=customer_choices()),
        gr.update(choices=product_choices())
    )


def place_order(customer_value, product_value, quantity):
    if not customer_value or not product_value:
        return "Select customer and product.", get_orders(), get_products()

    try:
        customer_id = int(customer_value.split(" - ")[0])
        product_id = int(product_value.split(" - ")[0])

        if quantity is None:
            return "Enter a quantity.", get_orders(), get_products()

        quantity = int(quantity)

        customer = conn.execute(
            "SELECT customer_id FROM customers WHERE customer_id=?",
            (customer_id,)
        ).fetchone()

        if customer is None:
            return "Customer not found.", get_orders(), get_products()

        if quantity <= 0:
            return "Quantity must be greater than 0.", get_orders(), get_products()

        product = conn.execute(
            "SELECT product_name, price, stock FROM products WHERE product_id=?",
            (product_id,)
        ).fetchone()

        if product is None:
            return "Product not found.", get_orders(), get_products()

        product_name, price, stock = product

        if quantity > stock:
            return f"Only {stock} units available.", get_orders(), get_products()

        total_amount = price * quantity
        today = str(date.today())

        conn.execute("BEGIN")

        conn.execute(
            """INSERT INTO orders(customer_id,order_date,status,total_amount)
               VALUES (?,?,?,?)""",
            (customer_id, today, "PROCESSING", total_amount)
        )
        order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """INSERT INTO order_items(order_id,product_id,quantity,unit_price)
               VALUES (?,?,?,?)""",
            (order_id, product_id, quantity, price)
        )

        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE product_id = ?",
            (quantity, product_id)
        )

        conn.execute(
            """INSERT INTO payments(order_id,payment_date,amount,payment_status)
               VALUES (?,?,?,?)""",
            (order_id, today, total_amount, "PAID")
        )

        conn.commit()

        message = (
            f"Order #{order_id} placed successfully! Status: PROCESSING. "
            f"{product_name} x {quantity} = ₹{total_amount:,.2f}"
        )
        return message, get_orders(), get_products()

    except (ValueError, TypeError):
        conn.rollback()
        return "Enter valid order details.", get_orders(), get_products()
    except sqlite3.Error as error:
        conn.rollback()
        return f"Database error: {error}", get_orders(), get_products()


def update_order_status(order_id, new_status):
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        return "Enter a valid order ID.", get_orders()

    allowed = {"PROCESSING", "SHIPPED", "COMPLETED"}
    if new_status not in allowed:
        return "Invalid order status.", get_orders()

    row = conn.execute(
        "SELECT status FROM orders WHERE order_id=?",
        (order_id,)
    ).fetchone()

    if row is None:
        return "Order not found.", get_orders()

    if row[0] == "CANCELLED":
        return "Cancelled orders cannot be reopened.", get_orders()

    try:
        conn.execute(
            "UPDATE orders SET status=? WHERE order_id=?",
            (new_status, order_id)
        )
        conn.commit()
        return f"Order #{order_id} status updated to {new_status}.", get_orders()
    except sqlite3.Error as error:
        conn.rollback()
        return f"Database error: {error}", get_orders()


def cancel_order(order_id):
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        return "Enter a valid order ID.", get_orders(), get_products(), get_payments()

    order = conn.execute(
        "SELECT status, total_amount FROM orders WHERE order_id=?",
        (order_id,)
    ).fetchone()

    if order is None:
        return "Order not found.", get_orders(), get_products(), get_payments()

    status, total_amount = order

    if status == "CANCELLED":
        return "Order is already cancelled.", get_orders(), get_products(), get_payments()

    items = conn.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id=?",
        (order_id,)
    ).fetchall()

    try:
        conn.execute("BEGIN")

        for product_id, quantity in items:
            conn.execute(
                "UPDATE products SET stock = stock + ? WHERE product_id=?",
                (quantity, product_id)
            )

        conn.execute(
            "UPDATE orders SET status='CANCELLED' WHERE order_id=?",
            (order_id,)
        )

        conn.execute(
            """UPDATE payments
               SET payment_status='REFUNDED'
               WHERE order_id=? AND payment_status='PAID'""",
            (order_id,)
        )

        conn.commit()

        return (
            f"Order #{order_id} cancelled. Stock restored and payment marked REFUNDED.",
            get_orders(),
            get_products(),
            get_payments()
        )
    except sqlite3.Error as error:
        conn.rollback()
        return (
            f"Database error: {error}",
            get_orders(),
            get_products(),
            get_payments()
        )


def restock_product(product_id, quantity):
    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return "Enter valid product ID and quantity.", get_products()

    if quantity <= 0:
        return "Restock quantity must be greater than 0.", get_products()

    product = conn.execute(
        "SELECT product_name FROM products WHERE product_id=?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found.", get_products()

    try:
        conn.execute(
            "UPDATE products SET stock = stock + ? WHERE product_id=?",
            (quantity, product_id)
        )
        conn.commit()
        return (
            f"{product[0]} restocked with {quantity} units.",
            get_products()
        )
    except sqlite3.Error as error:
        conn.rollback()
        return f"Database error: {error}", get_products()


def refresh_dashboard():
    revenue, orders, customers, products, avg, inventory, low_stock = dashboard_metrics()
    return (
        revenue, orders, customers, products, avg, inventory, low_stock,
        monthly_revenue(), daily_sales(), category_revenue(),
        top_products(), customer_ranking(), payment_status_analysis(),
        order_status_analysis(), inventory_analysis(), low_stock_products(),
        sales_chart(), category_chart()
    )


def refresh_customer_table(search):
    return get_customers(search)


def refresh_product_table(search):
    return get_products(search)


def refresh_order_table(search):
    return get_orders(search)


def refresh_payment_table(search):
    return get_payments(search)


with gr.Blocks(title="Sales Analytics System") as app:
    gr.Markdown("# 🛒 Sales & Order Management Analytics System")
    gr.Markdown(
        "### Business dashboard for sales, orders, customers, payments and inventory"
    )

    with gr.Tab("📊 Dashboard"):
        refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")

        with gr.Row():
            revenue_box = gr.Textbox(label="💰 Total Revenue", interactive=False)
            orders_box = gr.Textbox(label="🧾 Total Orders", interactive=False)
            customers_box = gr.Textbox(label="👥 Customers", interactive=False)
            products_box = gr.Textbox(label="📦 Products", interactive=False)

        with gr.Row():
            avg_box = gr.Textbox(label="🛒 Average Order Value", interactive=False)
            inventory_box = gr.Textbox(label="🏭 Inventory Value", interactive=False)
            low_stock_box = gr.Textbox(label="⚠️ Low Stock Items", interactive=False)

        gr.Markdown("## 📈 Sales Overview")
        with gr.Row():
            revenue_plot = gr.Plot(label="Monthly Revenue")
            category_plot = gr.Plot(label="Revenue by Category")

        with gr.Accordion("📊 Detailed Analytics", open=True):
            gr.Markdown("### 📅 Monthly Revenue")
            monthly_table = gr.Dataframe(value=monthly_revenue(), interactive=False)

            gr.Markdown("### 📆 Daily Sales")
            daily_table = gr.Dataframe(value=daily_sales(), interactive=False)

            gr.Markdown("### 🏷️ Category Performance")
            category_table = gr.Dataframe(value=category_revenue(), interactive=False)

            gr.Markdown("### 🏆 Top Products")
            top_table = gr.Dataframe(value=top_products(), interactive=False)

            gr.Markdown("### 👑 Customer Ranking")
            ranking_table = gr.Dataframe(value=customer_ranking(), interactive=False)

            gr.Markdown("### 💳 Payment Status")
            payment_status_table = gr.Dataframe(
                value=payment_status_analysis(), interactive=False
            )

            gr.Markdown("### 📦 Order Status")
            order_status_table = gr.Dataframe(
                value=order_status_analysis(), interactive=False
            )

            gr.Markdown("### 💰 Inventory Value by Product")
            inventory_table = gr.Dataframe(
                value=inventory_analysis(), interactive=False
            )

            gr.Markdown("### ⚠️ Low Stock Products")
            low_stock_table = gr.Dataframe(
                value=low_stock_products(), interactive=False
            )

        refresh_btn.click(
            refresh_dashboard,
            outputs=[
                revenue_box, orders_box, customers_box, products_box,
                avg_box, inventory_box, low_stock_box, monthly_table,
                daily_table, category_table, top_table, ranking_table,
                payment_status_table, order_status_table, inventory_table,
                low_stock_table, revenue_plot, category_plot
            ]
        )

    with gr.Tab("👤 Customers"):
        gr.Markdown("### Customer Management")
        with gr.Row():
            customer_search = gr.Textbox(
                label="🔎 Search Customers",
                placeholder="Search by name, email or city..."
            )
            customer_search_btn = gr.Button("Search")

        customer_msg = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            customer_name = gr.Textbox(label="Name")
            customer_email = gr.Textbox(label="Email")
            customer_city = gr.Textbox(label="City")

        add_customer_btn = gr.Button("➕ Add Customer", variant="primary")
        customers_table = gr.Dataframe(value=get_customers(), interactive=False)

        add_customer_btn.click(
            add_customer,
            inputs=[customer_name, customer_email, customer_city],
            outputs=[customer_msg, customers_table]
        )
        customer_search_btn.click(
            refresh_customer_table,
            inputs=customer_search,
            outputs=customers_table
        )

    with gr.Tab("📦 Products"):
        gr.Markdown("### Product & Inventory Management")
        with gr.Row():
            product_search = gr.Textbox(
                label="🔎 Search Products",
                placeholder="Search by product name or category..."
            )
            product_search_btn = gr.Button("Search")

        product_msg = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            product_name = gr.Textbox(label="Product Name")
            product_category = gr.Textbox(label="Category")
            product_price = gr.Number(label="Price")
            product_stock = gr.Number(label="Stock", precision=0)

        add_product_btn = gr.Button("➕ Add Product", variant="primary")
        products_table = gr.Dataframe(value=get_products(), interactive=False)

        add_product_btn.click(
            add_product,
            inputs=[product_name, product_category, product_price, product_stock],
            outputs=[product_msg, products_table]
        )
        product_search_btn.click(
            refresh_product_table,
            inputs=product_search,
            outputs=products_table
        )

    with gr.Tab("📦 Inventory"):
        gr.Markdown("### Inventory Restock")
        with gr.Row():
            restock_product_id = gr.Number(label="Product ID", precision=0)
            restock_quantity = gr.Number(label="Quantity", precision=0)

        restock_btn = gr.Button("➕ Restock Product", variant="primary")
        restock_msg = gr.Textbox(label="Inventory Status", interactive=False)
        restock_table = gr.Dataframe(value=get_products(), interactive=False)

        restock_btn.click(
            restock_product,
            inputs=[restock_product_id, restock_quantity],
            outputs=[restock_msg, restock_table]
        )

    with gr.Tab("🛍️ Place Order"):
        gr.Markdown("### Create a New Order")
        load_choices_btn = gr.Button("🔄 Load / Refresh Customer & Product Lists")

        with gr.Row():
            customer_dropdown = gr.Dropdown(
                choices=customer_choices(), label="Customer"
            )
            product_dropdown = gr.Dropdown(
                choices=product_choices(), label="Product"
            )

        order_quantity = gr.Number(label="Quantity", value=1, precision=0)
        place_order_btn = gr.Button("🛒 Place Order", variant="primary")
        order_msg = gr.Textbox(label="Order Status", interactive=False)
        orders_table = gr.Dataframe(value=get_orders(), interactive=False)
        order_products_table = gr.Dataframe(value=get_products(), interactive=False)

        load_choices_btn.click(
            refresh_choices,
            outputs=[customer_dropdown, product_dropdown]
        )
        place_order_btn.click(
            place_order,
            inputs=[customer_dropdown, product_dropdown, order_quantity],
            outputs=[order_msg, orders_table, order_products_table]
        )

    with gr.Tab("📋 Order Management"):
        gr.Markdown("### Order Lifecycle Management")

        with gr.Row():
            order_id_input = gr.Number(label="Order ID", precision=0)
            order_status_dropdown = gr.Dropdown(
                choices=["PROCESSING", "SHIPPED", "COMPLETED"],
                label="New Status"
            )

        with gr.Row():
            update_status_btn = gr.Button("🔄 Update Status", variant="primary")
            cancel_order_btn = gr.Button("❌ Cancel Order")

        order_management_msg = gr.Textbox(label="Order Status", interactive=False)
        order_management_table = gr.Dataframe(
            value=get_orders(), interactive=False
        )
        cancel_products_table = gr.Dataframe(
            value=get_products(), interactive=False
        )
        cancel_payment_table = gr.Dataframe(
            value=get_payments(), interactive=False
        )

        update_status_btn.click(
            update_order_status,
            inputs=[order_id_input, order_status_dropdown],
            outputs=[order_management_msg, order_management_table]
        )

        cancel_order_btn.click(
            cancel_order,
            inputs=order_id_input,
            outputs=[
                order_management_msg,
                order_management_table,
                cancel_products_table,
                cancel_payment_table
            ]
        )

        gr.Markdown("### 🔍 View Order Details")
        view_order_id = gr.Number(label="Order ID", precision=0)
        view_order_btn = gr.Button("View Details")
        order_detail_table = gr.Dataframe(
            headers=["order_id", "customer", "order_date", "status",
                     "total_amount", "product_name", "quantity", "unit_price"],
            interactive=False
        )

        view_order_btn.click(
            lambda order_id: order_details(int(order_id)),
            inputs=view_order_id,
            outputs=order_detail_table
        )

    with gr.Tab("💳 Payments"):
        gr.Markdown("### Payment Records")
        with gr.Row():
            payment_search = gr.Textbox(
                label="🔎 Search Payments",
                placeholder="Search by payment ID, order ID, customer or status..."
            )
            payment_search_btn = gr.Button("Search")

        payment_refresh = gr.Button("🔄 Refresh Payments")
        payment_table = gr.Dataframe(value=get_payments(), interactive=False)

        payment_refresh.click(get_payments, outputs=payment_table)
        payment_search_btn.click(
            refresh_payment_table,
            inputs=payment_search,
            outputs=payment_table
        )

    with gr.Tab("📈 SQL Analytics"):
        gr.Markdown("### Query-Based Business Analytics")
        analytics_refresh = gr.Button("🔄 Refresh Analytics", variant="primary")

        analytic_monthly = gr.Dataframe(value=monthly_revenue(), interactive=False)
        analytic_daily = gr.Dataframe(value=daily_sales(), interactive=False)
        analytic_category = gr.Dataframe(value=category_revenue(), interactive=False)
        analytic_products = gr.Dataframe(value=top_products(), interactive=False)
        analytic_customers = gr.Dataframe(value=customer_ranking(), interactive=False)
        analytic_payments = gr.Dataframe(
            value=payment_status_analysis(), interactive=False
        )

        analytics_refresh.click(
            lambda: (
                monthly_revenue(),
                daily_sales(),
                category_revenue(),
                top_products(),
                customer_ranking(),
                payment_status_analysis()
            ),
            outputs=[
                analytic_monthly, analytic_daily, analytic_category,
                analytic_products, analytic_customers, analytic_payments
            ]
        )

    app.load(
        refresh_dashboard,
        outputs=[
            revenue_box, orders_box, customers_box, products_box,
            avg_box, inventory_box, low_stock_box, monthly_table,
            daily_table, category_table, top_table, ranking_table,
            payment_status_table, order_status_table, inventory_table,
            low_stock_table, revenue_plot, category_plot
        ]
    )


if __name__ == "__main__":
    app.launch()
