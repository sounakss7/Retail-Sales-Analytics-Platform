-- 1. Top 10 customers by sales
SELECT customer_name, SUM(sales) AS total_sales
FROM retail_orders
GROUP BY customer_name
ORDER BY total_sales DESC
LIMIT 10;

-- 2. Monthly revenue trend
SELECT order_year, order_month, SUM(sales) AS monthly_sales
FROM retail_orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- 3. Category profitability
SELECT category, SUM(profit) AS total_profit, SUM(sales) AS total_sales
FROM retail_orders
GROUP BY category
ORDER BY total_profit DESC;

-- 4. Region performance
SELECT region, COUNT(*) AS orders, SUM(sales) AS revenue, SUM(profit) AS profit
FROM retail_orders
GROUP BY region
ORDER BY revenue DESC;
