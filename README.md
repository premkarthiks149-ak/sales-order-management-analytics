# Sales & Order Management Analytics System

A modular Python + SQLite business application for managing customers, products, orders, payments and inventory, with SQL-driven analytics and an interactive Gradio dashboard.

## 🚀 What This Project Demonstrates

This project is designed as an internship-ready portfolio application rather than a single notebook.

- Relational database design with SQLite
- SQL joins, grouping, aggregation and filtering
- Python application development
- Pandas analytics and Matplotlib visualization
- Gradio dashboard development
- Transaction-safe order processing
- Inventory validation and stock restoration
- Order lifecycle and payment tracking
- Search and filtering
- Automated tests with pytest
- GitHub Actions CI
- Docker-ready deployment
- Environment-based configuration

## ✨ Features

### Customer Management
- Add customers
- Validate required fields
- Prevent duplicate emails
- Search by name, email or city

### Product & Inventory Management
- Add products
- Validate price and stock
- Search by product name or category
- View inventory value
- Low-stock monitoring
- Restock products

### Order Management
- Create orders
- Validate customer and product
- Prevent ordering more than available stock
- Automatically reduce inventory
- Transaction-safe order creation
- View order details
- Search orders
- Track lifecycle: PROCESSING → SHIPPED → COMPLETED
- Cancel orders and restore stock automatically

### Payment Management
- Payment records linked to orders
- Payment search
- PAID status for checkout
- REFUNDED status when an order is cancelled

### Analytics Dashboard
- Total revenue, orders, customers and products
- Average order value and inventory value
- Low-stock count
- Monthly and daily sales
- Category performance
- Top products
- Customer ranking
- Payment and order status analysis
- Inventory value by product

## 🧠 Business Logic

Order creation is handled as a database transaction:

```text
Validate customer
      ↓
Validate product
      ↓
Validate quantity and stock
      ↓
Create order
      ↓
Create order item
      ↓
Reduce inventory
      ↓
Create payment record
      ↓
Commit transaction
```

If a database error occurs, the transaction is rolled back so partial updates are not left behind.

Order cancellation reverses the inventory change and marks the related payment as REFUNDED.

## 🏗️ Architecture

```text
                    Gradio UI
                        │
                        ▼
                     app.py
                ┌───────┴────────┐
                ▼                ▼
          database.py       analytics.py
                │                │
                └───────┬────────┘
                        ▼
                    SQLite DB
```

- `app.py` — UI, validation and business workflows
- `database.py` — SQLite connection, schema and seed data
- `analytics.py` — SQL queries, Pandas analysis and charts
- `tests/` — automated database tests
- `notebooks/` — original Colab project
- `.github/workflows/` — continuous integration
- `Dockerfile` — container deployment
- `.env.example` — environment configuration

## 🗄️ Database Design

```text
customers
   │
   └── orders
          │
          ├── order_items ─── products
          │
          └── payments
```

| Table | Purpose |
|---|---|
| customers | Customer information |
| products | Product and inventory information |
| orders | Order header and lifecycle status |
| order_items | Products and quantities in an order |
| payments | Payment records linked to orders |

## 🛠️ Tech Stack

Python 3.11+ · SQLite · SQL · Pandas · Matplotlib · Gradio · pytest · GitHub Actions · Docker

## ▶️ Run Locally

```bash
git clone https://github.com/premkarthiks149-ak/sales-order-management-analytics.git
cd sales-order-management-analytics
python -m venv .venv
```

Windows:
```text
.venv\Scripts\activate
```

macOS/Linux:
```text
source .venv/bin/activate
```

Then:
```bash
pip install -r requirements.txt
python app.py
```

The app uses port 7860 by default.

## ⚙️ Configuration

Supported environment variables:

- `DATABASE_PATH` — SQLite database file path
- `PORT` — application port

Example:

```text
DATABASE_PATH=sales_analytics.db
PORT=7860
```

## 🧪 Testing

```bash
pytest -q
```

GitHub Actions runs the test suite automatically on pushes and pull requests.

## 🐳 Docker

```bash
docker build -t sales-analytics .
docker run -p 7860:7860 sales-analytics
```

## ☁️ Deployment

The application can run outside Google Colab on Hugging Face Spaces, Docker-based hosting, or other Python-compatible cloud platforms.

For production, use persistent storage or migrate the SQLite layer to PostgreSQL/MySQL.

## 📊 Business Questions Answered

- What is completed revenue?
- Which products generate the most revenue?
- Which category performs best?
- Which customers generate the most revenue?
- Which products have low stock?
- How are sales changing over time?
- What is current inventory value?
- How many orders are in each lifecycle state?
- What is the payment status distribution?

## 🔐 Production Considerations

This is an internship/portfolio project, not a full enterprise ERP.

Future production upgrades could include authentication, role-based permissions, PostgreSQL, migrations, API endpoints, audit logging, monitoring and end-to-end tests.

## 📁 Project Structure

```text
sales-order-management-analytics/
├── app.py
├── database.py
├── analytics.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
├── tests/
│   └── test_database.py
├── docs/
│   ├── architecture.md
│   └── RESUME.md
├── .github/
│   └── workflows/
│       └── tests.yml
└── notebooks/
    └── Sales_Order_Analytics_Colab_Project_.ipynb
```

## 👨‍💻 Author

Prem Karthik
