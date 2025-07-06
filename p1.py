import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Custom Page Config and Style
st.set_page_config(page_title="📊 Global Trendz Sales Dashboard", layout="wide")

# Inject Custom CSS
st.markdown("""
    <style>
html, body, .stApp {
    background-color: #0e1117 !important;
    color: #FAFAFA;
}

.css-1d391kg, .css-1r6slb0, .css-1cpxqw2 {
    background-color: #0e1117 !important;
    color: #FAFAFA !important;
}

.stTextInput label, .stDateInput label, .stMultiSelect label, .stSelectbox label {
    color: #FAFAFA !important;
    font-size: 20px !important;
    font-weight: 600;
}

.stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5 {
    color: #FAFAFA !important;
}

.css-10trblm, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-size: 24px !important;
    color: #FAFAFA;
}
</style>
""", unsafe_allow_html=True)

# Logo + Title Section
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("qq_logo.png", width=60)
with col_title:
    st.title("📊 Global Trendz Sales Dashboard - Gulf & Egypt Region")

# Load Data
file_path = "مشروع_تحليل_مبيعات_بورتفوليو.xlsx"
df = pd.read_excel(file_path)

# Rename Columns
df.rename(columns={"الدولة": "Country", "المنتج": "Product", "إجمالي المبيعات": "Total Sales", "تاريخ الطلب": "Order Date"}, inplace=True)
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Sidebar Filters
with st.sidebar:
    st.header("📌 Filters")
    selected_country = st.multiselect("Select Country:", df["Country"].unique(), default=df["Country"].unique())
    selected_product = st.multiselect("Select Product:", df["Product"].unique(), default=df["Product"].unique())
    min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
    selected_date = st.date_input("Select Date Range:", [min_date, max_date])

# Filter Data
start_date, end_date = pd.to_datetime(selected_date[0]), pd.to_datetime(selected_date[1])
filtered_df = df[
    (df["Country"].isin(selected_country)) &
    (df["Product"].isin(selected_product)) &
    (df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)
]

# Aggregation
sales_by_product = filtered_df.groupby("Product")["Total Sales"].sum().reset_index()
sales_by_country = filtered_df.groupby("Country")["Total Sales"].sum().reset_index()
sales_over_time = filtered_df.groupby("Order Date")["Total Sales"].sum().reset_index()

# KPIs
total_sales = filtered_df["Total Sales"].sum()
total_orders = filtered_df.shape[0]
top_product = sales_by_product.sort_values(by="Total Sales", ascending=False).iloc[0]["Product"] if not sales_by_product.empty else "N/A"
top_country = sales_by_country.sort_values(by="Total Sales", ascending=False).iloc[0]["Country"] if not sales_by_country.empty else "N/A"

# KPI Row
st.markdown("##")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Total Sales", f"${total_sales:,.0f}")
kpi2.metric("📦 Orders", total_orders)
kpi3.metric("🏆 Top Product", top_product)
kpi4.metric("🌍 Top Country", top_country)

# Row for Charts 1 + 2
st.markdown("##")
chart1, chart2 = st.columns(2)
with chart1:
    if not sales_by_product.empty:
        fig1 = px.bar(sales_by_product, x="Product", y="Total Sales", color="Total Sales", title="📦 Sales by Product", text_auto=True, template="plotly", color_discrete_sequence=['#F4C430'])
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No product sales data available.")

with chart2:
    if not sales_by_country.empty:
        fig2 = px.pie(sales_by_country, names="Country", values="Total Sales", title="🌍 Sales by Country", template="plotly", color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No country sales data available.")

# Row for Time Series + Notes
chart3, notes_col = st.columns([2, 1])
with chart3:
    if not sales_over_time.empty:
        fig3 = px.line(sales_over_time, x="Order Date", y="Total Sales", title="📈 Sales Over Time", markers=True, template="plotly", color_discrete_sequence=['#003f5c'])
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No time series data available.")

with notes_col:
    st.markdown("""
    ### 📝 Insights
    - Track sales trends over time.
    - Discover your top countries and products.
    - Use filters to drill down by country and date.
    """)

# Project Summary
st.markdown("""
---
## 📄 Project Summary
This dashboard was created as part of a professional portfolio project for a fictional retail company called **Global Trendz**. The company operates in **Gulf Countries and Egypt**, selling a wide range of consumer products.

The dashboard helps managers:
- Track total and segmented sales.
- Visualize patterns.
- Understand performance drivers.
""")

# Raw Data
with st.expander("📂 Show Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)

# ⬇️ Download filtered data as CSV or Excel
st.markdown("##")
download_col1, download_col2 = st.columns(2)

with download_col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

with download_col2:
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="filtered_sales_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )