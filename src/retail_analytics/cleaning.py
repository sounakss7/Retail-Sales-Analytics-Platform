from __future__ import annotations

import logging
import os
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def load_and_clean_superstore(csv_path: str, return_report: bool = False) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
    """Load the Superstore CSV, validate it, and return a cleaned dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    logger.info("Loading dataset from %s", csv_path)
    df = pd.read_csv(csv_path, encoding="latin-1")

    original_shape = df.shape
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]

    for col in ["sales", "quantity", "discount", "profit", "postal_code"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["customer_name", "segment", "country", "city", "state", "region", "category", "sub_category", "product_name", "ship_mode"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    duplicate_columns = [col for col in df.columns if col != "row_id"]
    duplicate_rows = int(df.duplicated(subset=duplicate_columns).sum())
    df = df.drop_duplicates(subset=duplicate_columns).reset_index(drop=True)

    missing_values = df.isna().sum().to_dict()
    missing_percent = {k: round(float(v / max(len(df), 1) * 100), 2) for k, v in missing_values.items() if v > 0}

    if "sales" in df.columns:
        invalid_sales = int(((df["sales"] < 0) | df["sales"].isna()).sum())
    else:
        invalid_sales = 0

    if "quantity" in df.columns:
        invalid_quantity = int(((df["quantity"] < 1) | df["quantity"].isna()).sum())
    else:
        invalid_quantity = 0

    if "discount" in df.columns:
        invalid_discount = int(((df["discount"] < 0) | (df["discount"] > 1) | df["discount"].isna()).sum())
    else:
        invalid_discount = 0

    if "order_date" in df.columns and "ship_date" in df.columns:
        invalid_dates = int(((df["order_date"].isna()) | (df["ship_date"].isna())).sum())
    else:
        invalid_dates = 0

    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["shipping_days"] = df["shipping_days"].clip(lower=0)

    if "sales" in df.columns and "profit" in df.columns:
        df["profit_margin"] = df["profit"] / df["sales"].replace(0, pd.NA)
        df["profit_margin"] = df["profit_margin"].clip(lower=0, upper=1)

    if "order_date" in df.columns:
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_month_name"] = df["order_date"].dt.strftime("%B")
        df["order_quarter"] = df["order_date"].dt.quarter
        df["weekend_flag"] = df["order_date"].dt.dayofweek.isin([5, 6])

    report = {
        "source_rows": int(original_shape[0]),
        "rows_after_cleaning": int(df.shape[0]),
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "missing_percent": missing_percent,
        "invalid_sales": invalid_sales,
        "invalid_quantity": invalid_quantity,
        "invalid_discount": invalid_discount,
        "invalid_dates": invalid_dates,
    }

    logger.info("Cleaning finished with report: %s", report)
    return (df, report) if return_report else df
