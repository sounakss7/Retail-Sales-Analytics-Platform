-- 04_business_queries.sql
-- Business-facing analytics queries for dashboards and stakeholder reporting.

-- 1. Executive KPI summary
SELECT
    SUM(sales) AS total_revenue,
    SUM(profit) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS avg_order_value
FROM retail_orders;

-- 2. Monthly sales trend with running total
WITH monthly AS (
    SELECT
        order_year,
        order_month,
        order_month_name,
        SUM(sales) AS monthly_sales,
        SUM(profit) AS monthly_profit
    FROM retail_orders
    GROUP BY order_year, order_month, order_month_name
)
SELECT
    order_year,
    order_month,
    order_month_name,
    monthly_sales,
    monthly_profit,
    SUM(monthly_sales) OVER (
        ORDER BY order_year, order_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_sales
FROM monthly
ORDER BY order_year, order_month;

-- 3. Sales by region and category
SELECT
    region,
    category,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY region, category
ORDER BY region, total_sales DESC;

-- 4. Customer segmentation and top customers
SELECT
    segment,
    customer_name,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    RANK() OVER (PARTITION BY segment ORDER BY SUM(sales) DESC) AS customer_rank
FROM retail_orders
GROUP BY segment, customer_name
ORDER BY segment, total_sales DESC;

-- 5. Top products by revenue and profit
SELECT
    product_name,
    category,
    sub_category,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS sales_rank,
    RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
FROM retail_orders
GROUP BY product_name, category, sub_category
ORDER BY total_sales DESC;

-- 6. Shipping performance analysis
SELECT
    ship_mode,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    AVG(shipping_days) AS avg_shipping_days,
    CASE
        WHEN AVG(shipping_days) > 5 THEN 'Slow'
        ELSE 'Efficient'
    END AS shipping_efficiency
FROM retail_orders
GROUP BY ship_mode
ORDER BY total_sales DESC;

-- 7. Discount impact analysis
SELECT
    discount_band,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY discount_band
ORDER BY total_sales DESC;
