-- Lokale PostgreSQL-datalaag voor de analytics-app.
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    product VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost > 0 AND unit_cost < price),
    revenue NUMERIC(12, 2) NOT NULL CHECK (revenue > 0),
    gross_profit NUMERIC(12, 2) NOT NULL CHECK (gross_profit > 0),
    margin_percent NUMERIC(5, 2) NOT NULL CHECK (margin_percent BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS monthly_targets (
    month DATE PRIMARY KEY,
    target_revenue NUMERIC(12, 2) NOT NULL CHECK (target_revenue > 0)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_since DATE NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL
);
