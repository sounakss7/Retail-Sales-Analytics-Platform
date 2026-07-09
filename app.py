import os
import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Retail Sales Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

@st.cache_data
def load_data_from_db(db_url: str) -> pd.DataFrame:
    """Connects to Postgres and returns the retail orders dataset."""
    conn = psycopg2.connect(db_url)
    query = "SELECT * FROM retail_orders;"
    df = pd.read_sql(query, conn)
    # Parse dates explicitly
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    conn.close()
    return df

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
data_loaded_from = "CSV"
df = None

if db_url:
    try:
        df = load_data_from_db(db_url)
        data_loaded_from = "PostgreSQL Database (Neon)"
    except Exception as e:
        st.sidebar.warning(f"Database connection failed: {e}. Falling back to local CSV.")

if df is None:
    csv_path = os.path.join(os.path.dirname(__file__), "data", "processed", "superstore_clean.csv")
    if not os.path.exists(csv_path):
        # Generate the clean CSV using the pipeline if it doesn't exist
        st.sidebar.info("Processed CSV not found. Running ETL pipeline to generate it...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
            from retail_analytics.pipeline import run_pipeline
            raw_path = os.path.join(os.path.dirname(__file__), "data", "raw", "superstore.csv")
            if not os.path.exists(raw_path):
                # Fallback to root Superstore.csv
                raw_path = os.path.join(os.path.dirname(__file__), "Superstore.csv")
            run_pipeline(raw_path, csv_path)
            df = load_data_from_csv(csv_path)
        except Exception as err:
            st.error(f"Failed to generate processed data: {err}")
            st.stop()
    else:
        df = load_data_from_csv(csv_path)

# App Title
st.title("🛒 Retail Sales Analytics Dashboard")
st.markdown(f"**Enterprise Store Performance Dashboard** | *Data Source: {data_loaded_from}*")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🎯 Filter Options")

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
    st.warning("No records match the selected filters. Please expand your filtering criteria.")
    st.stop()

# ----------------- KPI BLOCK -----------------
total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
gross_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
total_orders = filtered_df["order_id"].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Sales", f"${total_sales:,.2f}")
kpi2.metric("Total Profit", f"${total_profit:,.2f}", delta=f"{gross_margin:.1f}% Margin")
kpi3.metric("Total Orders", f"{total_orders:,}")
kpi4.metric("Avg Order Value", f"${avg_order_value:,.2f}")
kpi5.metric("Units Sold", f"{filtered_df['quantity'].sum():,}")

st.markdown("---")

# Tab Layout
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales & Profit Trends", "👥 Customer Analytics", "📦 Product Insights", "🚚 Logistics & Shipping"])

with tab1:
    st.header("Sales and Profit Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Revenue Trend ($)")
        monthly_sales = filtered_df.groupby(["order_year", "order_month", "order_month_name"]).agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        # Sort chronologically
        monthly_sales = monthly_sales.sort_values(by=["order_year", "order_month"])
        # Format label
        monthly_sales["month_year"] = monthly_sales["order_month_name"] + " " + monthly_sales["order_year"].astype(str)
        st.line_chart(monthly_sales, x="month_year", y="revenue")
        
    with col2:
        st.subheader("Regional Performance (Revenue vs. Profit)")
        region_perf = filtered_df.groupby("region").agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        st.bar_chart(region_perf, x="region", y=["revenue", "profit"])
        
    st.subheader("State-Level Performance Data Grid")
    state_perf = filtered_df.groupby(["state", "region"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        avg_shipping_days=("shipping_days", "mean")
    ).reset_index().sort_values(by="revenue", ascending=False)
    state_perf["margin_%"] = ((state_perf["profit"] / state_perf["revenue"]) * 100).round(2)
    st.dataframe(state_perf.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "orders": "{:,}",
        "avg_shipping_days": "{:.1f} days",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab2:
    st.header("Customer Segments & Profiles")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Share by Customer Segment")
        segment_perf = filtered_df.groupby("segment").agg(
            revenue=("sales", "sum")
        ).reset_index()
        st.bar_chart(segment_perf, x="segment", y="revenue")
        
    with col2:
        st.subheader("Profit Margin across Segments (%)")
        segment_margin = filtered_df.groupby("segment").agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        segment_margin["margin_%"] = (segment_margin["profit"] / segment_margin["revenue"]) * 100
        st.bar_chart(segment_margin, x="segment", y="margin_%")
        
    st.subheader("Top 10 Customers by Revenue")
    top_cust = filtered_df.groupby(["customer_name", "segment", "region"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False).head(10)
    top_cust["margin_%"] = ((top_cust["profit"] / top_cust["revenue"]) * 100).round(2)
    st.dataframe(top_cust.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "orders": "{:,}",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab3:
    st.header("Product Performance Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Product Sub-Category ($)")
        sub_cat_perf = filtered_df.groupby("sub_category")["sales"].sum().reset_index().sort_values(by="sales", ascending=False)
        st.bar_chart(sub_cat_perf, x="sub_category", y="sales")
        
    with col2:
        st.subheader("Discount Band Impact on Profits")
        discount_perf = filtered_df.groupby("discount_band", observed=False).agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        ).reset_index()
        st.bar_chart(discount_perf, x="discount_band", y="profit")
        
    st.subheader("Top 15 Most Profitable Products")
    top_products = filtered_df.groupby(["product_name", "category", "sub_category"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        units_sold=("quantity", "sum")
    ).reset_index().sort_values(by="profit", ascending=False).head(15)
    top_products["margin_%"] = ((top_products["profit"] / top_products["revenue"]) * 100).round(2)
    st.dataframe(top_products.style.format({
        "revenue": "${:,.2f}",
        "profit": "${:,.2f}",
        "units_sold": "{:,}",
        "margin_%": "{:.2f}%"
    }), use_container_width=True)

with tab4:
    st.header("Shipping & Logistics Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Transit Days by Shipping Mode")
        ship_days = filtered_df.groupby("ship_mode")["shipping_days"].mean().reset_index()
        ship_days.columns = ["Shipping Mode", "Avg Shipping Days"]
        st.bar_chart(ship_days, x="Shipping Mode", y="Avg Shipping Days")
        
    with col2:
        st.subheader("Order Share by Shipping Mode")
        ship_share = filtered_df.groupby("ship_mode")["order_id"].nunique().reset_index()
        ship_share.columns = ["Shipping Mode", "Order Count"]
        st.bar_chart(ship_share, x="Shipping Mode", y="Order Count")
        
    st.subheader("Shipping Efficiency Analysis")
    ship_efficiency = filtered_df.groupby(["region", "ship_mode"]).agg(
        avg_shipping_days=("shipping_days", "mean"),
        total_orders=("order_id", "nunique"),
        total_revenue=("sales", "sum")
    ).reset_index().sort_values(by=["region", "avg_shipping_days"])
    st.dataframe(ship_efficiency.style.format({
        "avg_shipping_days": "{:.1f} days",
        "total_orders": "{:,}",
        "total_revenue": "${:,.2f}"
    }), use_container_width=True)
