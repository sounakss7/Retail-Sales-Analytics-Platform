# Power BI Dashboard Plan

## Pages
1. Executive Dashboard
2. Sales Dashboard
3. Customer Dashboard
4. Product Dashboard

## Data Sources
Use the following SQL views:
- vw_sales_summary
- vw_monthly_sales
- vw_region_performance
- vw_customer_summary
- vw_product_performance
- vw_shipping_analysis

## Suggested Measures
- Total Sales = SUM(vw_sales_summary[sales])
- Total Profit = SUM(vw_sales_summary[profit])
- Total Orders = DISTINCTCOUNT(vw_sales_summary[order_id])
- Average Order Value = DIVIDE([Total Sales], [Total Orders])
- Profit Margin = DIVIDE([Total Profit], [Total Sales])
