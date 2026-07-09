from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from retail_analytics.pipeline import run_pipeline
from retail_analytics.postgres_loader import prepare_dataframe_for_postgres


def load_to_postgres(csv_path: str, connection_string: str | None = None) -> None:
    """Load the processed dataset into PostgreSQL if a connection string is provided."""
    df, _ = run_pipeline(csv_path, 'data/processed/superstore_clean.csv')
    prepared = prepare_dataframe_for_postgres(df)

    if not connection_string:
        print('No PostgreSQL connection string provided. Prepared data is ready for import.')
        return

    try:
        import psycopg2
    except ImportError as exc:
        raise RuntimeError('psycopg2 is required for PostgreSQL loading') from exc

    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS retail_orders (row_id INT PRIMARY KEY, order_id TEXT, order_date DATE, ship_date DATE, ship_mode TEXT, customer_id TEXT, customer_name TEXT, segment TEXT, country TEXT, city TEXT, state TEXT, postal_code INT, region TEXT, product_id TEXT, category TEXT, sub_category TEXT, product_name TEXT, sales NUMERIC, quantity INT, discount NUMERIC, profit NUMERIC, profit_margin NUMERIC, order_year INT, order_month INT, order_month_name TEXT, order_quarter INT, revenue_per_unit NUMERIC, discount_percentage NUMERIC, discount_band TEXT, shipping_days INT, weekend_flag BOOLEAN, profitability_flag BOOLEAN)')
            for _, row in prepared.iterrows():
                cur.execute(
                    'INSERT INTO retail_orders (row_id, order_id, order_date, ship_date, ship_mode, customer_id, customer_name, segment, country, city, state, postal_code, region, product_id, category, sub_category, product_name, sales, quantity, discount, profit, profit_margin, order_year, order_month, order_month_name, order_quarter, revenue_per_unit, discount_percentage, discount_band, shipping_days, weekend_flag, profitability_flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    tuple(row.tolist())
                )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Load the processed retail dataset into PostgreSQL.')
    parser.add_argument('--csv', default='data/raw/superstore.csv')
    parser.add_argument('--connection-string', default=None)
    args = parser.parse_args()
    load_to_postgres(args.csv, args.connection_string)
