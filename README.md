# Sales & Order Management Analytics System

A Python and SQL based sales and order management application with an interactive analytics dashboard.

## Project Overview

This project manages customers, products, orders, order items, payments, inventory, and sales analytics using a relational SQLite database.

## Current Features

- Customer management
- Product and inventory management
- Order placement
- Payment tracking
- SQLite relational database
- SQL-based analytics
- Revenue and order metrics
- Top-product and customer analysis
- Interactive Gradio interface
- Sales visualizations with Matplotlib

## Tech Stack

- Python
- SQLite
- SQL
- Pandas
- Matplotlib
- Gradio
- Google Colab

## Project Structure

```
sales-order-management-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py
├── database.py
├── analytics.py
├── data/
├── screenshots/
└── notebooks/
    └── Sales_Order_Analytics_Colab_Project_.ipynb
```

> The Python modules, database setup, testing, and deployment structure will be added as the project is upgraded.

## Database Design

The application uses a relational SQLite database containing:

- Customers
- Products
- Orders
- Order Items
- Payments

The main relationships connect customers to orders, orders to order items, products to order items, and orders to payments.

## Planned Improvements

- Modular Python application structure
- Better validation and error handling
- Advanced sales analytics
- Interactive dashboard filters
- Inventory alerts
- Order lifecycle management
- Automated testing
- Deployment outside Google Colab

## Author

Prem Karthik
