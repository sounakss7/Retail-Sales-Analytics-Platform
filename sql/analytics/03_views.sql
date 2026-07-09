-- 03_views.sql
-- Reusable business-intelligence views for Power BI consumption.

CREATE OR REPLACE VIEW vw_sales_summary AS
WITH base AS (
    SELECT
        order_id,
        order_date,
        customer_id,
        customer_name,
        segment,
        region,
        category,
        sub_category,
        ship_mode,
        sales,
        profit,
        quantity,
        discount,
        profit_margin,
        shipping_days,
        weekend_flag,
        profitability_flag
    FROM retail_orders
)
SELECT
    order_id,
    order_date,
    customer_id,
    customer_name,
    segment,
    region,
    category,
    sub_category,
    ship_mode,
    sales,
    profit,
    quantity,
    discount,
    profit_margin,
    shipping_days,
    weekend_flag,
    profitability_flag,
    SUM(sales) OVER () AS total_sales_all_rows,
    SUM(profit) OVER () AS total_profit_all_rows
FROM base;

CREATE OR REPLACE VIEW vw_monthly_sales AS
WITH monthly AS (
    SELECT
        order_year,
        order_month,
        order_month_name,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit,
        COUNT(DISTINCT order_id) AS total_orders
    FROM retail_orders
    GROUP BY order_year, order_month, order_month_name
)
SELECT
    order_year,
    order_month,
    order_month_name,
    total_sales,
    total_profit,
    total_orders,
    SUM(total_sales) OVER (
        ORDER BY order_year, order_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_sales,
    AVG(total_sales) OVER (
        ORDER BY order_year, order_month
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS moving_avg_sales
FROM monthly
ORDER BY order_year, order_month;

CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS sales_rank
FROM retail_orders
GROUP BY region;

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
FROM retail_orders
GROUP BY category;

CREATE OR REPLACE VIEW vw_customer_summary AS
WITH customer_base AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        region,
        sales,
        profit,
        order_id
    FROM retail_orders
)
SELECT
    customer_id,
    customer_name,
    segment,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS sales_rank
FROM customer_base
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
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
FROM retail_orders
GROUP BY product_id, product_name, category, sub_category;

CREATE OR REPLACE VIEW vw_shipping_analysis AS
SELECT
    ship_mode,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    AVG(shipping_days) AS avg_shipping_days,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0), 4) AS profit_margin,
    CASE
        WHEN ship_mode IN ('First Class', 'Same Day') THEN 'Priority'
        ELSE 'Standard'
    END AS shipping_group
FROM retail_orders
GROUP BY ship_mode;
