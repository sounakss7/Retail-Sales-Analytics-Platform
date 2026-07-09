-- 02_indexes.sql
-- Optimized indexes for KPI queries used by Power BI and BI dashboards.

CREATE INDEX IF NOT EXISTS idx_retail_orders_order_date ON retail_orders (order_date);
CREATE INDEX IF NOT EXISTS idx_retail_orders_region ON retail_orders (region);
CREATE INDEX IF NOT EXISTS idx_retail_orders_category ON retail_orders (category);
CREATE INDEX IF NOT EXISTS idx_retail_orders_customer_id ON retail_orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_retail_orders_product_id ON retail_orders (product_id);
CREATE INDEX IF NOT EXISTS idx_retail_orders_segment ON retail_orders (segment);
CREATE INDEX IF NOT EXISTS idx_retail_orders_ship_mode ON retail_orders (ship_mode);
CREATE INDEX IF NOT EXISTS idx_retail_orders_order_year_month ON retail_orders (order_year, order_month);
