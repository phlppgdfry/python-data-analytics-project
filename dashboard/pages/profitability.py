"""Sales- en profitabilitypagina."""

import plotly.express as px
import streamlit as st

from dashboard.shared import get_dashboard_context, page_intro
from src.analysis import profit_by_country, profit_by_product, revenue_by_country, revenue_by_product, revenue_vs_target
from visualizations.plotly_charts import create_actual_vs_target_chart


GROSS_PROFIT_LABEL = "Gross profit (€)"



context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("Sales & profitability", "Vergelijk omzet met maandtargets en zie welke markten en producten de meeste waarde opleveren.")
filtered_data = context.filtered_data
target_data = revenue_vs_target(filtered_data, context.monthly_targets)
actual_total = float(target_data["revenue"].sum())
target_total = float(target_data["target_revenue"].sum())
variance_total = actual_total - target_total

metrics = st.columns(3)
metrics[0].metric("Actual revenue", f"€{actual_total:,.2f}")
metrics[1].metric("Revenue target", f"€{target_total:,.2f}")
metrics[2].metric("Variance to target", f"€{variance_total:,.2f}", delta=f"{variance_total / target_total * 100:+.1f}%" if target_total else None)
st.plotly_chart(create_actual_vs_target_chart(target_data), width="stretch")
st.caption("Targets are company-wide monthly goals. Narrow country or product filters are useful for exploration, but are not equivalent to a filtered target.")

left, right = st.columns(2)
with left:
    country_data = revenue_by_country(filtered_data).merge(profit_by_country(filtered_data), on="country", validate="one_to_one")
    st.plotly_chart(
        px.bar(country_data, x="gross_profit", y="country", orientation="h", title="Gross profit by country", color_discrete_sequence=["#0F766E"], labels={"gross_profit": GROSS_PROFIT_LABEL, "country": "Country"}).update_layout(template="plotly_white", showlegend=False, margin={"l": 0, "r": 0, "t": 50, "b": 0}),
        width="stretch",
    )
with right:
    product_data = revenue_by_product(filtered_data).merge(profit_by_product(filtered_data), on="product", validate="one_to_one")
    st.plotly_chart(
        px.bar(product_data, x="gross_profit", y="product", orientation="h", title="Gross profit by product", color_discrete_sequence=["#7C3AED"], labels={"gross_profit": GROSS_PROFIT_LABEL, "product": "Product"}).update_layout(template="plotly_white", showlegend=False, margin={"l": 0, "r": 0, "t": 50, "b": 0}),
        width="stretch",
    )

st.subheader("Market contribution")
contribution = country_data[["country", "revenue", "gross_profit"]].rename(columns={"country": "Country", "revenue": "Revenue (€)", "gross_profit": GROSS_PROFIT_LABEL})
st.dataframe(contribution, width="stretch", hide_index=True)
st.download_button("Download profitability summary", contribution.to_csv(index=False).encode("utf-8"), "profitability_by_country.csv", "text/csv", width="content")
