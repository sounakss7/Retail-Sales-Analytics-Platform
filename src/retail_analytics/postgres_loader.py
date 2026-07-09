from __future__ import annotations

from typing import Any

import pandas as pd


def prepare_dataframe_for_postgres(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a cleaned dataframe for PostgreSQL import."""
    prepared = df.copy()

    for column in ["order_date", "ship_date"]:
        if column in prepared.columns:
            prepared[column] = pd.to_datetime(prepared[column], errors="coerce").dt.strftime("%Y-%m-%d")

    for column in ["profitability_flag", "weekend_flag"]:
        if column in prepared.columns:
            prepared[column] = prepared[column].astype("boolean")
            prepared[column] = prepared[column].apply(lambda value: bool(value) if pd.notna(value) else None).astype(object)

    return prepared
