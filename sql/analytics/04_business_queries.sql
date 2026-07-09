-- 04_business_queries.sql
-- Business-focused queries for dashboards and stakeholder reporting.

-- Top 10 customers by revenue
SELECT customer_name, total_sales
FROM (
    SELECT customer_name, SUM(sales) AS total_sales,
           RANK() OVER (ORDER BY SUM(sales) DESC) AS sales_rank
    FROM retail_orders
    GROUP BY customer_name
) ranked
WHERE sales_rank <= 10;

-- Category contribution to profit
SELECT category, SUM(profit) AS total_profit, SUM(sales) AS total_sales
FROM retail_orders
GROUP BY category
ORDER BY total_profit DESC;

-- Regional performance with ranking
SELECT region,
       SUM(sales) AS total_sales,
       SUM(profit) AS total_profit,
       RANK() OVER (ORDER BY SUM(sales) DESC) AS sales_rank
FROM retail_orders
GROUP BY region;

-- Product profitability analysis
SELECT product_name, category, sub_category, SUM(profit) AS total_profit, SUM(sales) AS total_sales
FROM retail_orders
GROUP BY product_name, category, sub_category
ORDER BY total_profit DESC;
