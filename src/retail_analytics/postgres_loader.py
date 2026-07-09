from __future__ import annotations

from typing import Any

import pandas as pd

EXPECTED_COLUMNS: list[str] = [
    "row_id",
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_id",
    "customer_name",
    "segment",
    "country",
    "city",
    "state",
    "postal_code",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit",
    "profit_margin",
    "order_year",
    "order_month",
    "order_month_name",
    "order_quarter",
    "revenue_per_unit",
    "discount_percentage",
    "discount_band",
    "shipping_days",
    "weekend_flag",
    "profitability_flag",
]


def _coerce_text_values(series: pd.Series) -> pd.Series:
    """Convert values to PostgreSQL-friendly text values."""
    converted = series.astype("object")
    return converted.apply(lambda value: str(value) if pd.notna(value) else None)


def validate_dataframe_schema(df: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Validate the dataframe schema and align it to the shared expected column order."""
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    extra_columns = [column for column in df.columns if column not in EXPECTED_COLUMNS]

    if missing_columns or extra_columns:
        raise ValueError(
            "Schema validation failed. "
            f"Missing columns: {missing_columns}; Extra columns: {extra_columns}."
        )

    if debug:
        print("DataFrame columns:", list(df.columns))
        print("PostgreSQL schema columns:", EXPECTED_COLUMNS)

    current_order = list(df.columns)
    if current_order != EXPECTED_COLUMNS:
        if debug:
            print("Column order mismatch detected. Reordering DataFrame to match PostgreSQL schema.")
        return df[EXPECTED_COLUMNS]

    return df


def prepare_dataframe_for_postgres(df: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Prepare a cleaned dataframe for PostgreSQL import."""
    prepared = df.copy()

    for column in ["order_date", "ship_date"]:
        if column in prepared.columns:
            prepared[column] = pd.to_datetime(prepared[column], errors="coerce").dt.strftime("%Y-%m-%d")

    for column in ["profitability_flag", "weekend_flag"]:
        if column in prepared.columns:
            prepared[column] = prepared[column].astype("boolean")
            prepared[column] = prepared[column].apply(lambda value: bool(value) if pd.notna(value) else None).astype(object)

    numeric_columns = [
        "row_id",
        "postal_code",
        "sales",
        "quantity",
        "discount",
        "profit",
        "profit_margin",
        "order_year",
        "order_month",
        "order_quarter",
        "revenue_per_unit",
        "discount_percentage",
        "shipping_days",
    ]
    for column in numeric_columns:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    text_columns = [column for column in prepared.columns if column not in {"order_date", "ship_date", *numeric_columns, "profitability_flag", "weekend_flag"}]
    for column in text_columns:
        prepared[column] = _coerce_text_values(prepared[column])

    return validate_dataframe_schema(prepared, debug=debug)
