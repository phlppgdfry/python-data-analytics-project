"""Customer-intelligencepagina."""

import plotly.express as px
import streamlit as st

from dashboard.shared import get_dashboard_context, page_intro
from src.analysis import cohort_retention, customer_lifecycle, rfm_segment_summary, top_customers
from visualizations.plotly_charts import create_cohort_retention_chart


context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("Customer intelligence", "Begrijp wie terugkomt, welke klanten waarde creëren en hoe aankoopcohorten zich gedragen.")
filtered_data = context.filtered_data
lifecycle_data = customer_lifecycle(context.data, filtered_data)
new_customer_count = int((lifecycle_data["customer_type"] == "New").sum())
returning_customer_count = int((lifecycle_data["customer_type"] == "Returning").sum())
returning_share = returning_customer_count / len(lifecycle_data) * 100 if len(lifecycle_data) else 0.0

customer_columns = st.columns(3)
customer_columns[0].metric("New customers", new_customer_count, help="Klanten waarvan de eerste aankoop in de gekozen periode ligt.")
customer_columns[1].metric("Returning customers", returning_customer_count)
customer_columns[2].metric("Returning customer share", f"{returning_share:.1f}%")

customer_left, customer_right = st.columns(2)
with customer_left:
    lifecycle_summary = lifecycle_data.groupby("customer_type", as_index=False).agg(customers=("customer_id", "nunique"), revenue=("revenue", "sum"))
    st.plotly_chart(
        px.bar(lifecycle_summary, x="customer_type", y="revenue", color="customer_type", title="Revenue: new vs returning customers", labels={"customer_type": "Customer type", "revenue": "Revenue (€)"}).update_layout(template="plotly_white", showlegend=False),
        width="stretch",
    )
with customer_right:
    segment_data = rfm_segment_summary(filtered_data)
    st.plotly_chart(
        px.bar(segment_data, x="segment", y="customers", color="segment", title="RFM customer segments", labels={"segment": "Segment", "customers": "Customers"}).update_layout(template="plotly_white", showlegend=False),
        width="stretch",
    )

st.subheader("Top customers")
customer_table = (
    top_customers(filtered_data)
    .merge(context.customer_directory[["customer_id", "customer_name", "acquisition_channel"]], on="customer_id", validate="one_to_one")
    .rename(columns={"customer_name": "Customer", "acquisition_channel": "Channel", "revenue": "Revenue (€)", "gross_profit": "Gross profit (€)", "orders": "Orders"})
    .drop(columns="customer_id")
)
st.dataframe(customer_table, width="stretch", hide_index=True)
st.download_button("Download top customers", customer_table.to_csv(index=False).encode("utf-8"), "top_customers.csv", "text/csv", width="content")

st.subheader("Cohort retention")
st.caption("Elke rij is de maand waarin klanten voor het eerst kochten; elke kolom toont hoeveel daarvan later opnieuw kocht.")
st.plotly_chart(create_cohort_retention_chart(cohort_retention(filtered_data)), width="stretch")
