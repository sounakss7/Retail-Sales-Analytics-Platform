import os
import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Executive Retail Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

@st.cache_data
def load_data_from_db(db_url: str) -> tuple[pd.DataFrame, dict]:
    """Connects to PostgreSQL and fetches the entire dataset and database status metadata."""
    conn = psycopg2.connect(db_url)
    
    # Query database metadata for stats
    metadata = {}
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT pg_size_pretty(pg_relation_size('retail_orders'));")
        metadata['table_size'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM retail_orders;")
        metadata['row_count'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT customer_id) FROM retail_orders;")
        metadata['unique_customers'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT product_id) FROM retail_orders;")
        metadata['unique_products'] = cur.fetchone()[0]
        
    query = "SELECT * FROM retail_orders;"
    df = pd.read_sql(query, conn)
    
    # Ensure datatypes
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            
    conn.close()
    return df, metadata

@st.cache_data
def load_data_from_csv(csv_path: str) -> pd.DataFrame:
    """Loads retail orders data from processed CSV."""
    df = pd.read_csv(csv_path)
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df

# Data Fetching Logic (Dual Mode)
db_url = os.getenv("DATABASE_URL")
data_loaded_from = "CSV File"
db_metadata = {}
df = None

if db_url:
    try:
        df, db_metadata = load_data_from_db(db_url)
        data_loaded_from = "PostgreSQL Database (Neon Cloud)"
    except Exception as e:
        st.sidebar.warning(f"Database connection failed: {e}. Falling back to local CSV.")

if df is None:
    csv_path = os.path.join(os.path.dirname(__file__), "data", "processed", "superstore_clean.csv")
    if not os.path.exists(csv_path):
        # Generate the clean CSV using the pipeline if it doesn't exist
        st.sidebar.info("Running ETL pipeline to generate processed CSV...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
            from retail_analytics.pipeline import run_pipeline
            raw_path = os.path.join(os.path.dirname(__file__), "Superstore.csv")
            if not os.path.exists(raw_path):
                raw_path = os.path.join(os.path.dirname(__file__), "data", "raw", "superstore.csv")
            run_pipeline(raw_path, csv_path)
            df = load_data_from_csv(csv_path)
        except Exception as err:
            st.error(f"Failed to generate processed data: {err}")
            st.stop()
    else:
        df = load_data_from_csv(csv_path)

# App Title & Layout
st.title("🛒 Executive Retail Sales Analytics Dashboard")
st.markdown("---")

# Sidebar Filters & DB Connection Panel
st.sidebar.header("🎯 Dashboard Controls")

# 1. Database Connection Status Panel
st.sidebar.subheader("🔌 Connection Status")
if data_loaded_from.startswith("PostgreSQL"):
    st.sidebar.success(f"Connected: Neon PostgreSQL")
    st.sidebar.write(f"**Loaded Table**: `retail_orders`")
    st.sidebar.write(f"**Table Size**: `{db_metadata.get('table_size')}`")
    st.sidebar.write(f"**Database Rows**: `{db_metadata.get('row_count'):,}`")
else:
    st.sidebar.info("Data source: Local CSV File")

# 2. Filters
st.sidebar.subheader("🔍 Filters")

# Region Filter
regions = df["region"].dropna().unique().tolist()
selected_regions = st.sidebar.multiselect("Regions", options=regions, default=regions)

# Segment Filter
segments = df["segment"].dropna().unique().tolist()
selected_segments = st.sidebar.multiselect("Customer Segments", options=segments, default=segments)

# Category Filter
categories = df["category"].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect("Product Categories", options=categories, default=categories)

# Order Date Range Filter
min_date = df["order_date"].min().to_pydatetime()
max_date = df["order_date"].max().to_pydatetime()
start_date, end_date = st.sidebar.slider(
    "Order Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Apply Filters
filtered_df = df[
    df["region"].isin(selected_regions) &
    df["segment"].isin(selected_segments) &
    df["category"].isin(selected_categories) &
    (df["order_date"] >= pd.to_datetime(start_date)) &
    (df["order_date"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No records match the selected filters. Please adjust your controls.")
    st.stop()

# ----------------- KPI BLOCK -----------------
total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
gross_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
total_orders = filtered_df["order_id"].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Revenue", f"${total_sales:,.2f}")
kpi2.metric("Total Profit", f"${total_profit:,.2f}")
kpi3.metric("Gross Profit Margin", f"{gross_margin:.2f}%")
kpi4.metric("Total Orders", f"{total_orders:,}")
kpi5.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.markdown("---")

# Main Visualization Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales & Profit Trends", "👥 Segment Contribution", "📦 Product Performance", "🚚 Shipping Logistics"])

with tab1:
    st.header("Sales and Profit Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Sales Trend ($)")
        monthly_sales = filtered_df.groupby(["order_year", "order_month", "order_month_name"]).agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        monthly_sales = monthly_sales.sort_values(by=["order_year", "order_month"])
        monthly_sales["month_year"] = monthly_sales["order_month_name"] + " " + monthly_sales["order_year"].astype(str)
        st.line_chart(monthly_sales, x="month_year", y=["revenue", "profit"])
        
    with col2:
        st.subheader("Cumulative Revenue Over Time ($)")
        monthly_sales["running_sales"] = monthly_sales["revenue"].cumsum()
        st.area_chart(monthly_sales, x="month_year", y="running_sales")
        
    st.subheader("Regional Performance Summary Table")
    region_perf = filtered_df.groupby("region").agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        qty_sold=("quantity", "sum")
    ).reset_index().sort_values(by="revenue", ascending=False)
    region_perf["margin_%"] = ((region_perf["profit"] / region_perf["revenue"]) * 100).round(2)
    st.dataframe(region_perf.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "orders": "{:,}",
        "qty_sold": "{:,}",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab2:
    st.header("Segment and Categorical Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Customer Segment")
        segment_perf = filtered_df.groupby("segment").agg(
            revenue=("sales", "sum")
        ).reset_index()
        st.bar_chart(segment_perf, x="segment", y="revenue")
        
    with col2:
        st.subheader("Revenue by Product Category")
        category_perf = filtered_df.groupby("category").agg(
            revenue=("sales", "sum")
        ).reset_index()
        st.bar_chart(category_perf, x="category", y="revenue")
        
    st.subheader("Granular Segment & Category Performance Table")
    seg_cat_perf = filtered_df.groupby(["segment", "category", "sub_category"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        qty_sold=("quantity", "sum")
    ).reset_index().sort_values(by=["segment", "revenue"], ascending=[True, False])
    seg_cat_perf["margin_%"] = ((seg_cat_perf["profit"] / seg_cat_perf["revenue"]) * 100).round(2)
    st.dataframe(seg_cat_perf.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "qty_sold": "{:,}",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab3:
    st.header("Product Performance & Discounting Metrics")
    col1, col2 = st.columns(2)
    
    with col2:
        st.subheader("Profitability Across Discount Bands")
        discount_perf = filtered_df.groupby("discount_band", observed=False).agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        st.bar_chart(discount_perf, x="discount_band", y="profit")
        
    with col1:
        st.subheader("Sales by Product Sub-Category ($)")
        sub_cat_perf = filtered_df.groupby("sub_category")["sales"].sum().reset_index().sort_values(by="sales", ascending=False)
        st.bar_chart(sub_cat_perf, x="sub_category", y="sales")
        
    st.subheader("Top 10 Customers by Total Profit ($)")
    top_cust = filtered_df.groupby(["customer_name", "segment", "region"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique")
    ).reset_index().sort_values(by="profit", ascending=False).head(10)
    top_cust["margin_%"] = ((top_cust["profit"] / top_cust["revenue"]) * 100).round(2)
    st.dataframe(top_cust.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "orders": "{:,}",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab4:
    st.header("Shipping & Logistics Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Shipping Days by Shipping Mode")
        ship_days = filtered_df.groupby("ship_mode")["shipping_days"].mean().reset_index()
        ship_days.columns = ["Shipping Mode", "Avg Shipping Days"]
        st.bar_chart(ship_days, x="Shipping Mode", y="Avg Shipping Days")
        
    with col2:
        st.subheader("Shipping Performance by Region")
        region_ship = filtered_df.groupby("region")["shipping_days"].mean().reset_index()
        region_ship.columns = ["Region", "Avg Shipping Days"]
        st.bar_chart(region_ship, x="Region", y="Avg Shipping Days")
        
    st.subheader("Weekend Shipping Analysis (Weekend Orders vs. Weekday Orders)")
    weekend_ship = filtered_df.groupby("weekend_flag").agg(
        orders=("order_id", "nunique"),
        avg_shipping_days=("shipping_days", "mean"),
        total_revenue=("sales", "sum"),
        total_profit=("profit", "sum")
    ).reset_index()
    weekend_ship["weekend_flag"] = weekend_ship["weekend_flag"].map({True: "Weekend Order", False: "Weekday Order"})
    weekend_ship.columns = ["Order Day Type", "Total Orders", "Avg Transit Time (Days)", "Total Revenue ($)", "Total Profit ($)"]
    st.dataframe(weekend_ship.style.format({
        "Total Orders": "{:,}",
        "Avg Transit Time (Days)": "{:.2f} days",
        "Total Revenue ($)": "${:,.2f}",
        "Total Profit ($)": "${:,.2f}"
    }), use_container_width=True)
