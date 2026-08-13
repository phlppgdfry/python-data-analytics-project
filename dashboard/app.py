"""Start met: streamlit run dashboard/app.py"""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (  # noqa: E402
    calculate_kpis,
    calculate_profit_kpis,
    calculate_period_comparison,
    filter_sales_data,
    monthly_performance,
    previous_period_bounds,
    revenue_by_country,
    revenue_by_month,
    revenue_by_product,
    revenue_vs_target,
    top_customers,
)
from src.clean_data import clean_sales_data  # noqa: E402
from src.load_data import load_monthly_targets_csv, load_sales_csv  # noqa: E402
from visualizations.plotly_charts import create_actual_vs_target_chart, create_monthly_performance_chart  # noqa: E402


st.set_page_config(page_title="Sales analytics", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
        .block-container { max-width: 1240px; padding-top: 2.5rem; }
        div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #dbeafe; border-radius: 14px; padding: 1rem; }
        div[data-testid="stMetricLabel"] { color: #475569; }
        .eyebrow { color: #2563eb; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True,
)


RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"
TARGETS_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "monthly_targets.csv"


@st.cache_data
def get_sales_data(source_version: int) -> pd.DataFrame:
    """Clean raw data; its file version safely refreshes Streamlit's cache."""
    del source_version
    return clean_sales_data(load_sales_csv(RAW_DATA_PATH))


@st.cache_data
def get_monthly_targets(source_version: int) -> pd.DataFrame:
    """Load monthly targets and refresh them whenever their source file changes."""
    del source_version
    return load_monthly_targets_csv(TARGETS_DATA_PATH)


data = get_sales_data(RAW_DATA_PATH.stat().st_mtime_ns)
monthly_targets = get_monthly_targets(TARGETS_DATA_PATH.stat().st_mtime_ns)
st.markdown('<p class="eyebrow">Portfolio project · Sales intelligence</p>', unsafe_allow_html=True)
st.title("Sales analytics dashboard")
st.caption("Analyseer 24 maanden verkoopdata, vergelijk periodes en exporteer gefilterde inzichten.")

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

previous_start, previous_end = previous_period_bounds(selected_dates[0], selected_dates[1])
previous_data = filter_sales_data(data, countries, products, previous_start, previous_end)
kpis = calculate_kpis(filtered_data)
profit_kpis = calculate_profit_kpis(filtered_data)
comparison = calculate_period_comparison(filtered_data, previous_data)
target_data = revenue_vs_target(filtered_data, monthly_targets)
target_attainment = target_data["revenue"].sum() / target_data["target_revenue"].sum() * 100


def format_delta(change: float | None) -> str:
    """Formatteer een procentuele verandering voor Streamlit metric cards."""
    return "No prior period" if change is None else f"{change:+.1f}% vs prior period"


columns = st.columns(5)
columns[0].metric("Revenue", f"€{kpis['total_revenue']:,.2f}", delta=format_delta(comparison["revenue_change_percent"]))
columns[1].metric("Gross profit", f"€{profit_kpis['gross_profit']:,.2f}")
columns[2].metric("Gross margin", f"{profit_kpis['margin_percent']:.1f}%")
columns[3].metric("Orders", f"{kpis['orders']:,}", delta=format_delta(comparison["orders_change_percent"]))
columns[4].metric("Target progress", f"{target_attainment:.1f}%")

st.caption(f"Compared with {previous_start:%d %b %Y} – {previous_end:%d %b %Y}")
st.plotly_chart(create_monthly_performance_chart(monthly_performance(filtered_data)), width="stretch")
st.plotly_chart(create_actual_vs_target_chart(target_data), width="stretch")
st.caption("Targets are company-wide monthly revenue goals; use all countries and products for a full target comparison.")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        px.bar(
            revenue_by_country(filtered_data),
            x="revenue",
            y="country",
            orientation="h",
            title="Revenue by country",
            color_discrete_sequence=["#0F766E"],
            labels={"revenue": "Revenue (€)", "country": "Country"},
        ).update_layout(template="plotly_white", showlegend=False, margin={"l": 0, "r": 0, "t": 50, "b": 0}),
        width="stretch",
    )
with right:
    st.plotly_chart(
        px.bar(
            revenue_by_product(filtered_data),
            x="revenue",
            y="product",
            orientation="h",
            title="Revenue by product",
            color_discrete_sequence=["#7C3AED"],
            labels={"revenue": "Revenue (€)", "product": "Product"},
        ).update_layout(template="plotly_white", showlegend=False, margin={"l": 0, "r": 0, "t": 50, "b": 0}),
        width="stretch",
    )

country_data = revenue_by_country(filtered_data)
product_data = revenue_by_product(filtered_data)
st.subheader("Key insights")
insight_left, insight_right = st.columns(2)
insight_left.success(f"**Top country:** {country_data.iloc[0]['country']} (€{country_data.iloc[0]['revenue']:,.2f})")
insight_right.success(f"**Top product:** {product_data.iloc[0]['product']} (€{product_data.iloc[0]['revenue']:,.2f})")

with st.expander("View cleaned data"):
    st.dataframe(filtered_data, width="stretch")
    st.download_button(
        "Download filtered data as CSV",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales_data.csv",
        mime="text/csv",
    )

st.subheader("Top customers")
st.dataframe(
    top_customers(filtered_data).rename(columns={"customer_id": "Customer", "revenue": "Revenue (€)", "gross_profit": "Gross profit (€)", "orders": "Orders"}),
    width="stretch",
    hide_index=True,
)
