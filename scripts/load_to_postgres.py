from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

load_dotenv(REPO_ROOT / ".env")

from retail_analytics.pipeline import run_pipeline
from retail_analytics.postgres_loader import EXPECTED_COLUMNS, prepare_dataframe_for_postgres


def create_table(cur: Any) -> None:
    """Create PostgreSQL table if it doesn't exist."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS retail_orders (
            row_id INT PRIMARY KEY,
            order_id TEXT,
            order_date DATE,
            ship_date DATE,
            ship_mode TEXT,
            customer_id TEXT,
            customer_name TEXT,
            segment TEXT,
            country TEXT,
            city TEXT,
            state TEXT,
            postal_code INT,
            region TEXT,
            product_id TEXT,
            category TEXT,
            sub_category TEXT,
            product_name TEXT,
            sales NUMERIC,
            quantity INT,
            discount NUMERIC,
            profit NUMERIC,
            profit_margin NUMERIC,
            order_year INT,
            order_month INT,
            order_month_name TEXT,
            order_quarter INT,
            revenue_per_unit NUMERIC,
            discount_percentage NUMERIC,
            discount_band TEXT,
            shipping_days INT,
            weekend_flag BOOLEAN,
            profitability_flag BOOLEAN
        );
        """
    )


def load_to_postgres(
    csv_path: str,
    connection_string: str | None = None,
    debug: bool = False,
) -> None:
    """Run the ETL pipeline and load the processed data into PostgreSQL."""
    print("=" * 60)
    print("Retail Sales Analytics Loader")
    print("=" * 60)

    if not connection_string:
        connection_string = os.getenv("DATABASE_URL")

    if not connection_string:
        raise ValueError("DATABASE_URL not found. Please add it to your .env file.")

    print("Running ETL Pipeline...")
    start_time = time.perf_counter()

    df, _report = run_pipeline(csv_path, "data/processed/superstore_clean.csv")
    prepared = prepare_dataframe_for_postgres(df, debug=debug)

    prepared = prepared[EXPECTED_COLUMNS]

    print(f"Processed Rows: {len(prepared)}")
    print("Connecting to PostgreSQL...")

    conn: Any = None
    cur: Any = None
    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False
        cur = conn.cursor()
        print("Connected Successfully")

        create_table(cur)
        cur.execute("TRUNCATE TABLE retail_orders;")

        rows = [tuple(row) for row in prepared.itertuples(index=False, name=None)]
        insert_query = """
            INSERT INTO retail_orders (
                row_id, order_id, order_date, ship_date, ship_mode,
                customer_id, customer_name, segment, country, city,
                state, postal_code, region, product_id, category,
                sub_category, product_name, sales, quantity, discount,
                profit, profit_margin, order_year, order_month,
                order_month_name, order_quarter, revenue_per_unit,
                discount_percentage, discount_band, shipping_days,
                weekend_flag, profitability_flag
            ) VALUES %s
        """
        execute_values(cur, insert_query, rows, page_size=1000)
        conn.commit()

        elapsed_time = time.perf_counter() - start_time
        print("=" * 60)
        print(f"Total rows inserted: {len(rows)}")
        print(f"Execution time: {elapsed_time:.2f} seconds")
        print("Success: Data loaded into PostgreSQL.")
        print("=" * 60)
    except Exception as exc:  # pragma: no cover - exercised in runtime usage
        if conn is not None:
            conn.rollback()
        raise RuntimeError(f"PostgreSQL load failed: {exc}") from exc
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
        print("Connection Closed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load Retail Sales data into PostgreSQL")
    parser.add_argument("--csv", default="data/raw/superstore.csv", help="Path to raw CSV dataset")
    parser.add_argument("--connection-string", default=None, help="Optional PostgreSQL connection string")
    parser.add_argument("--debug", action="store_true", help="Print schema and column information before insertion")
    args = parser.parse_args()

    load_to_postgres(args.csv, args.connection_string, debug=args.debug)
