from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .cleaning import load_and_clean_superstore
from .feature_engineering import engineer_features


def run_pipeline(raw_csv: str, output_csv: str | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run the cleaning, validation, and feature engineering pipeline."""
    cleaned, report = load_and_clean_superstore(raw_csv, return_report=True)
    enriched = engineer_features(cleaned)

    if output_csv:
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        enriched.to_csv(output_csv, index=False)

    return enriched, report


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]
    raw_csv = base_dir / ".." / "data" / "raw" / "superstore.csv"
    output_csv = base_dir / ".." / "data" / "processed" / "superstore_clean.csv"
    run_pipeline(str(raw_csv), str(output_csv))
