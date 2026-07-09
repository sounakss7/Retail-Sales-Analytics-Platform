import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from retail_analytics.cleaning import load_and_clean_superstore


def test_load_and_clean_superstore_returns_expected_columns(tmp_path):
    csv_path = os.path.join(tmp_path, "superstore.csv")
    pd.DataFrame(
        [
            {
                "Row ID": "1",
                "Order ID": "CA-2016-152156",
                "Order Date": "11/8/2016",
                "Ship Date": "11/11/2016",
                "Ship Mode": "Second Class",
                "Customer ID": "CG-12520",
                "Customer Name": "Claire Gute",
                "Segment": "Consumer",
                "Country": "United States",
                "City": "Henderson",
                "State": "Kentucky",
                "Postal Code": "42420",
                "Region": "South",
                "Product ID": "FUR-BO-10001798",
                "Category": "Furniture",
                "Sub-Category": "Bookcases",
                "Product Name": "Bush Somerset Collection Bookcase",
                "Sales": "261.96",
                "Quantity": "2",
                "Discount": "0",
                "Profit": "41.9136",
            },
            {
                "Row ID": "2",
                "Order ID": "CA-2016-152156",
                "Order Date": "11/8/2016",
                "Ship Date": "11/11/2016",
                "Ship Mode": "Second Class",
                "Customer ID": "CG-12520",
                "Customer Name": "Claire Gute",
                "Segment": "Consumer",
                "Country": "United States",
                "City": "Henderson",
                "State": "Kentucky",
                "Postal Code": "42420",
                "Region": "South",
                "Product ID": "FUR-BO-10001798",
                "Category": "Furniture",
                "Sub-Category": "Bookcases",
                "Product Name": "Bush Somerset Collection Bookcase",
                "Sales": "261.96",
                "Quantity": "2",
                "Discount": "0",
                "Profit": "41.9136",
            },
        ]
    ).to_csv(csv_path, index=False)

    df, report = load_and_clean_superstore(csv_path, return_report=True)

    assert not df.empty
    assert {"order_date", "ship_date", "sales", "profit", "profit_margin"}.issubset(df.columns)
    assert {"shipping_days", "weekend_flag", "order_month_name"}.issubset(df.columns)
    assert df["sales"].dtype.kind in "fiu"
    assert df["profit_margin"].between(0, 1).all()
    assert isinstance(report, dict)
    assert "duplicate_rows" in report
    assert report["duplicate_rows"] == 1
