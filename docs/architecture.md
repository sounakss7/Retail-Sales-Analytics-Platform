# Architecture Overview

## Components
- Data ingestion: raw CSV from data/raw/superstore.csv
- Cleaning and normalization: src/retail_analytics/cleaning.py
- Feature engineering: src/retail_analytics/feature_engineering.py
- Orchestration: src/retail_analytics/pipeline.py
- Storage: PostgreSQL table retail_orders
- Reporting: Power BI dashboard in powerbi/

## Flow
1. Read raw CSV.
2. Standardize column names and data types.
3. Engineer business features.
4. Export cleaned data to data/processed/superstore_clean.csv.
5. Load into PostgreSQL for analytics.
