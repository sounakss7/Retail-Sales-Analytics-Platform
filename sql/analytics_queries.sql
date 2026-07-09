-- analytics_queries.sql
-- Legacy helper queries retained for reference.

SELECT customer_name, SUM(sales) AS total_sales
FROM retail_orders
GROUP BY customer_name
ORDER BY total_sales DESC
LIMIT 10;
