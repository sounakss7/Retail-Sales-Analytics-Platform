from __future__ import annotations

import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create high-value business features for retail analytics."""
    result = df.copy()

    if "order_date" in result.columns:
        result["order_year"] = result["order_date"].dt.year
        result["order_month"] = result["order_date"].dt.month
        result["order_month_name"] = result["order_date"].dt.strftime("%B")
        result["order_quarter"] = result["order_date"].dt.quarter
        result["weekend_flag"] = result["order_date"].dt.dayofweek.isin([5, 6])

    if {"sales", "quantity"}.issubset(result.columns):
        result["revenue_per_unit"] = result["sales"] / result["quantity"].replace(0, pd.NA)

    if "discount" in result.columns:
        result["discount_percentage"] = result["discount"] * 100
        result["discount_band"] = pd.cut(
            result["discount"],
            bins=[-0.01, 0.1, 0.2, 0.3, 1.0],
            labels=["low", "medium", "high", "very_high"],
            include_lowest=True,
        )

    if {"profit", "sales"}.issubset(result.columns):
        result["profitability_flag"] = result["profit"] > 0
        result["profit_margin"] = result["profit"] / result["sales"].replace(0, pd.NA)
        result["profit_margin"] = result["profit_margin"].clip(lower=0, upper=1)

    if {"order_date", "ship_date"}.issubset(result.columns):
        result["shipping_days"] = (result["ship_date"] - result["order_date"]).dt.days
        result["shipping_days"] = result["shipping_days"].clip(lower=0)

    return result
