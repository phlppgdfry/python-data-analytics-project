SELECT order_id, order_date, customer_id, country, product, quantity, price, unit_cost
FROM sales_orders
ORDER BY order_date, order_id;
