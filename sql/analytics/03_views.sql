-- 03_views.sql
-- Reusable business-intelligence views consumed by Power BI.

CREATE OR REPLACE VIEW vw_sales_summary AS
SELECT
    order_id,
    customer_id,
    customer_name,
    region,
    category,
    sub_category,
    ship_mode,
    order_date,
    sales,
    profit,
    quantity,
    discount,
    profit_margin,
    shipping_days,
    weekend_flag,
    profitability_flag
FROM retail_orders;

CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    order_year,
    order_month,
    order_month_name,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_orders
GROUP BY order_year, order_month, order_month_name
ORDER BY order_year, order_month;

CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY region;

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY category;

CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT
    customer_id,
    customer_name,
    segment,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY customer_id, customer_name, segment, region;

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    product_id,
    product_name,
    category,
    sub_category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin
FROM retail_orders
GROUP BY product_id, product_name, category, sub_category;

CREATE OR REPLACE VIEW vw_shipping_analysis AS
SELECT
    ship_mode,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    AVG(shipping_days) AS avg_shipping_days
FROM retail_orders
GROUP BY ship_mode;
