-- Dashboardbron: PostgreSQL-resultaat met dezelfde vorm als de CSV-bron.
SELECT order_id, order_date, customer_id, country, product, quantity, price, unit_cost
FROM sales_orders
WHERE order_date >= DATE '2024-01-01'
ORDER BY order_date, order_id;

-- Zakelijke analyse rechtstreeks in SQL.
SELECT
    country,
    SUM(revenue) AS revenue,
    SUM(gross_profit) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0) * 100, 2) AS margin_percent
FROM sales_orders
GROUP BY country
ORDER BY gross_profit DESC;
