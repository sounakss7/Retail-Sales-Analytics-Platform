import pandas as pd

from retail_analytics.postgres_loader import prepare_dataframe_for_postgres


def test_prepare_dataframe_for_postgres_formats_dates_and_booleans():
    df = pd.DataFrame(
        {
            "order_date": ["2016-11-08"],
            "ship_date": ["2016-11-11"],
            "weekend_flag": [True],
            "customer_name": ["Claire Gute"],
        }
    )

    prepared = prepare_dataframe_for_postgres(df)

    assert prepared.loc[0, "order_date"] == "2016-11-08"
    assert prepared.loc[0, "ship_date"] == "2016-11-11"
    assert prepared.loc[0, "weekend_flag"] is True
    assert prepared.loc[0, "customer_name"] == "Claire Gute"
