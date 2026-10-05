# Architecture

## Application Flow

```text
User -> Gradio UI -> app.py
                     |-> database.py -> SQLite
                     |-> analytics.py -> SQL + Pandas -> Dashboard
```

## Order Transaction

1. Verify customer
2. Verify product
3. Verify quantity and stock
4. Create order
5. Create order item
6. Reduce inventory
7. Create payment
8. Commit

If an error occurs, the transaction is rolled back.

## Cancellation Flow

```text
Cancel Order -> Restore Stock -> CANCELLED -> REFUNDED
```