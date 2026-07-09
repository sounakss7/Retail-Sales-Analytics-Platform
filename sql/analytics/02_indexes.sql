-- 02_indexes.sql
-- Improves performance for common filtering and aggregation patterns.

CREATE INDEX IF NOT EXISTS idx_retail_orders_order_date ON retail_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_retail_orders_region ON retail_orders(region);
CREATE INDEX IF NOT EXISTS idx_retail_orders_category ON retail_orders(category);
CREATE INDEX IF NOT EXISTS idx_retail_orders_customer_id ON retail_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_retail_orders_product_id ON retail_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_retail_orders_segment ON retail_orders(segment);
