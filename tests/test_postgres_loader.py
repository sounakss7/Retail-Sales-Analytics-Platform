import pandas as pd
import pytest

from retail_analytics.postgres_loader import EXPECTED_COLUMNS, prepare_dataframe_for_postgres


def test_prepare_dataframe_for_postgres_formats_dates_and_booleans():
    df = pd.DataFrame({column: [None] for column in reversed(EXPECTED_COLUMNS)})
    df.loc[0, "row_id"] = 1
    df.loc[0, "order_id"] = "CA-2016-152156"
    df.loc[0, "order_date"] = "2016-11-08"
    df.loc[0, "ship_date"] = "2016-11-11"
    df.loc[0, "ship_mode"] = "Second Class"
    df.loc[0, "customer_id"] = "CG-12520"
    df.loc[0, "customer_name"] = "Claire Gute"
    df.loc[0, "segment"] = "Consumer"
    df.loc[0, "country"] = "United States"
    df.loc[0, "city"] = "Henderson"
    df.loc[0, "state"] = "Kentucky"
    df.loc[0, "postal_code"] = 42420
    df.loc[0, "region"] = "South"
    df.loc[0, "product_id"] = "FUR-BO-10001798"
    df.loc[0, "category"] = "Furniture"
    df.loc[0, "sub_category"] = "Bookcases"
    df.loc[0, "product_name"] = "Bush Somerset Collection Bookcase"
    df.loc[0, "sales"] = 261.96
    df.loc[0, "quantity"] = 2
    df.loc[0, "discount"] = 0
    df.loc[0, "profit"] = 41.9136
    df.loc[0, "profit_margin"] = 0.16
    df.loc[0, "order_year"] = 2016
    df.loc[0, "order_month"] = 11
    df.loc[0, "order_month_name"] = "November"
    df.loc[0, "order_quarter"] = 4
    df.loc[0, "revenue_per_unit"] = 130.98
    df.loc[0, "discount_percentage"] = 0.0
    df.loc[0, "discount_band"] = "low"
    df.loc[0, "shipping_days"] = 3
    df.loc[0, "weekend_flag"] = True
    df.loc[0, "profitability_flag"] = True

    prepared = prepare_dataframe_for_postgres(df)

    assert prepared.columns.tolist() == EXPECTED_COLUMNS
    assert prepared.loc[0, "order_date"] == "2016-11-08"
    assert prepared.loc[0, "ship_date"] == "2016-11-11"
    assert prepared.loc[0, "weekend_flag"] is True
    assert prepared.loc[0, "customer_name"] == "Claire Gute"


def test_prepare_dataframe_for_postgres_raises_for_missing_columns():
    df = pd.DataFrame({column: [None] for column in EXPECTED_COLUMNS if column != "customer_name"})

    with pytest.raises(ValueError, match="Missing columns"):
        prepare_dataframe_for_postgres(df)
