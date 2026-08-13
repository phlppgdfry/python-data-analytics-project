-- PostgreSQL-schema voor wanneer CSV door een echte database wordt vervangen.
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    product VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0)
);
