-- Gebruik deze query later met load_sales_from_postgres().
SELECT order_id, order_date, customer_id, country, product, quantity, price,
       quantity * price AS revenue
FROM sales_orders
WHERE order_date >= DATE '2026-01-01'
ORDER BY order_date, order_id;

-- Een voorbeeld van analyse rechtstreeks in SQL.
SELECT country, SUM(quantity * price) AS revenue
FROM sales_orders
GROUP BY country
ORDER BY revenue DESC;
