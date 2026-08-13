"""Executive-overviewpagina."""

import streamlit as st

from src.analysis import (
    calculate_kpis,
    calculate_period_comparison,
    calculate_profit_kpis,
    monthly_performance,
    previous_period_bounds,
    revenue_by_country,
    revenue_by_product,
    revenue_vs_target,
)
from dashboard.shared import format_compact_currency, format_delta, get_dashboard_context, page_intro
from visualizations.plotly_charts import create_monthly_performance_chart


context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("Executive overview", "Een compacte momentopname van omzet, winst, orders en de belangrijkste markten.")
filtered_data = context.filtered_data
previous_start, previous_end = previous_period_bounds(context.selected_start, context.selected_end)
previous_data = filtered_data.iloc[0:0] if previous_end < context.data["order_date"].min() else context.data.loc[
    context.data["country"].isin(context.countries)
    & context.data["product"].isin(context.products)
    & context.data["order_date"].between(previous_start, previous_end)
]
kpis = calculate_kpis(filtered_data)
profit_kpis = calculate_profit_kpis(filtered_data)
comparison = calculate_period_comparison(filtered_data, previous_data)
target_data = revenue_vs_target(filtered_data, context.monthly_targets)
target_total = float(target_data["target_revenue"].sum())
target_attainment = target_data["revenue"].sum() / target_total * 100 if target_total else 0.0

columns = st.columns(5)
columns[0].metric("Revenue", format_compact_currency(kpis["total_revenue"]), delta=format_delta(comparison["revenue_change_percent"]), help=f"Exact revenue: €{kpis['total_revenue']:,.2f}.")
columns[1].metric("Gross profit", format_compact_currency(profit_kpis["gross_profit"]), help=f"Exact gross profit: €{profit_kpis['gross_profit']:,.2f}.")
columns[2].metric("Gross margin", f"{profit_kpis['margin_percent']:.1f}%", help="Brutowinst als percentage van omzet.")
columns[3].metric("Orders", f"{kpis['orders']:,}", delta=format_delta(comparison["orders_change_percent"]), help="Aantal unieke orders.")
columns[4].metric("Target progress", f"{target_attainment:.1f}%", help="Werkelijke omzet tegenover het maanddoel voor de geselecteerde maanden.")

st.caption(f"Compared with {previous_start:%d %b %Y} – {previous_end:%d %b %Y}. Data source: {'PostgreSQL' if context.database_url else 'CSV fallback'}.")
st.plotly_chart(create_monthly_performance_chart(monthly_performance(filtered_data)), width="stretch")

country_data = revenue_by_country(filtered_data)
product_data = revenue_by_product(filtered_data)
insight_left, insight_right = st.columns(2)
insight_left.success(f"**Top country:** {country_data.iloc[0]['country']} (€{country_data.iloc[0]['revenue']:,.2f})")
insight_right.success(f"**Top product:** {product_data.iloc[0]['product']} (€{product_data.iloc[0]['revenue']:,.2f})")

with st.expander("Inspect and export cleaned data"):
    st.dataframe(filtered_data, width="stretch", hide_index=True)
    st.download_button(
        "Download selected data as CSV",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales_data.csv",
        mime="text/csv",
        width="content",
    )
