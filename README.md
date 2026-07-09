# Retail Sales Analytics Platform

## Project Overview
This repository implements an end-to-end retail analytics workflow for the Superstore sales dataset. The project is structured as a portfolio-ready data engineering and analytics solution using Python, pandas, SQL, and Power BI.

## Architecture
1. Ingest the raw CSV from the data folder.
2. Clean and validate the dataset.
3. Engineer business-oriented features.
4. Export a processed dataset for downstream analytics.
5. Prepare SQL and BI assets for reporting.

## Folder Structure
- data/raw/superstore.csv: raw dataset
- data/processed/superstore_clean.csv: cleaned and enriched output
- src/retail_analytics/: reusable Python modules for cleaning, feature engineering, and orchestration
- sql/: PostgreSQL schema and analytics queries
- notebooks/: exploratory analysis notebooks
- docs/: architecture and design notes
- powerbi/: Power BI assets
- tests/: automated validation tests

## Tech Stack
- Python
- pandas
- pytest
- PostgreSQL (planned)
- Power BI (planned)

## Installation
1. Create a virtual environment.
2. Install dependencies: pip install -r requirements.txt
3. Run the pipeline: python -m src.retail_analytics.pipeline

## Workflow
- Load the raw CSV.
- Validate missing values, duplicates, ranges, and dates.
- Generate a data quality report.
- Produce enriched features such as shipping days, profit margin, order month, quarter, and weekend flags.

## Data Quality Notes
- The dataset is loaded with Latin-1 encoding.
- Duplicate rows are removed during preprocessing.
- Numeric and datetime columns are type-validated.
- Additional features support downstream business reporting.

## Next Steps
- Add PostgreSQL loading and SQL-based analytics.
- Build the Power BI dashboard.
- Extend the notebooks with deeper EDA and visual analysis.

## PostgreSQL Loading
A helper script is available for preparing the processed dataframe for import into PostgreSQL.

Run:
- python scripts/load_to_postgres.py --csv data/raw/superstore.csv

If you provide a PostgreSQL connection string, the script will attempt to connect and load the data into a table named retail_orders.

## SQL Analytics Layer
The SQL layer is organized into separate files for schema, indexes, reusable views, and business queries:
- sql/analytics/01_schema.sql
- sql/analytics/02_indexes.sql
- sql/analytics/03_views.sql
- sql/analytics/04_business_queries.sql

Power BI should consume the views rather than the raw retail_orders table directly.

## Power BI Dashboard Plan
A dashboard blueprint is available in powerbi/README.md with four proposed pages:
- Executive Dashboard
- Sales Dashboard
- Customer Dashboard
- Product Dashboard
