"""Start met: streamlit run dashboard/app.py"""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analysis import (  # noqa: E402
    calculate_kpis,
    filter_sales_data,
    revenue_by_country,
    revenue_by_month,
    revenue_by_product,
)
from clean_data import clean_sales_data, save_cleaned_sales_data  # noqa: E402
from load_data import load_sales_csv  # noqa: E402


st.set_page_config(page_title="Sales analytics", page_icon="📊", layout="wide")


@st.cache_data
def get_sales_data() -> pd.DataFrame:
    processed_path = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"
    if processed_path.exists():
        return pd.read_csv(processed_path, parse_dates=["order_date"])
    data = clean_sales_data(load_sales_csv())
    save_cleaned_sales_data(data)
    return data


data = get_sales_data()
st.title("Sales analytics")
st.caption("Interactief overzicht van de schoongemaakte voorbeeldverkoopdata.")

with st.sidebar:
    st.header("Filters")
    selected_dates = st.date_input(
        "Order period",
        value=(data["order_date"].min().date(), data["order_date"].max().date()),
        min_value=data["order_date"].min().date(),
        max_value=data["order_date"].max().date(),
    )
    countries = st.multiselect("Country", sorted(data["country"].unique()), default=sorted(data["country"].unique()))
    products = st.multiselect("Product", sorted(data["product"].unique()), default=sorted(data["product"].unique()))

if len(selected_dates) != 2:
    st.info("Selecteer een begin- en einddatum om de analyse te tonen.")
    st.stop()

filtered_data = filter_sales_data(data, countries, products, selected_dates[0], selected_dates[1])
if filtered_data.empty:
    st.warning("Geen gegevens voor deze filters.")
    st.stop()

kpis = calculate_kpis(filtered_data)
columns = st.columns(4)
columns[0].metric("Revenue", f"€{kpis['total_revenue']:,.2f}")
columns[1].metric("Orders", f"{kpis['orders']:,}")
columns[2].metric("Customers", f"{kpis['customers']:,}")
columns[3].metric("Average order value", f"€{kpis['average_order_value']:,.2f}")

monthly_data = revenue_by_month(filtered_data)
st.plotly_chart(px.line(monthly_data, x="month", y="revenue", markers=True, title="Revenue over time"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(px.bar(revenue_by_country(filtered_data), x="country", y="revenue", title="Revenue by country"), use_container_width=True)
with right:
    st.plotly_chart(px.bar(revenue_by_product(filtered_data), x="product", y="revenue", title="Top products"), use_container_width=True)

country_data = revenue_by_country(filtered_data)
product_data = revenue_by_product(filtered_data)
st.subheader("Key insights")
insight_left, insight_right = st.columns(2)
insight_left.info(f"**Top country:** {country_data.iloc[0]['country']} (€{country_data.iloc[0]['revenue']:,.2f})")
insight_right.info(f"**Top product:** {product_data.iloc[0]['product']} (€{product_data.iloc[0]['revenue']:,.2f})")

with st.expander("View cleaned data"):
    st.dataframe(filtered_data, use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales_data.csv",
        mime="text/csv",
    )
