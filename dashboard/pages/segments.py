"""Uitlegbare customer segmentation met scikit-learn."""

import plotly.express as px
import streamlit as st

from dashboard.shared import get_dashboard_context, page_intro
from src.segmentation import cluster_customers, customer_cluster_summary


context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("ML customer segments", "K-Means groepeert klanten met vergelijkbaar aankoopgedrag, zodat acties per groep kunnen verschillen.")
st.info("How to read this: recency means days since the last order; frequency is order count; monetary is total revenue. Features are standardised before K-Means so revenue does not dominate the grouping.")

clusters = cluster_customers(context.filtered_data)
summary = customer_cluster_summary(context.filtered_data)

metric_columns = st.columns(3)
metric_columns[0].metric("Customers segmented", len(clusters))
metric_columns[1].metric("Segments found", summary["cluster"].nunique())
metric_columns[2].metric("Largest segment", summary.sort_values("customers", ascending=False).iloc[0]["cluster_name"])

chart_left, chart_right = st.columns(2)
with chart_left:
    scatter = px.scatter(
        clusters,
        x="frequency",
        y="monetary",
        size="monetary",
        color="cluster_name",
        hover_data=["customer_id", "recency_days"],
        title="Customer value and purchase frequency",
        labels={"frequency": "Orders", "monetary": "Revenue (€)", "cluster_name": "Segment"},
    )
    scatter.update_layout(template="plotly_white", legend_title_text="Segment")
    st.plotly_chart(scatter, width="stretch")
with chart_right:
    bar = px.bar(
        summary,
        x="cluster_name",
        y="revenue",
        color="cluster_name",
        text="customers",
        title="Revenue concentration by segment",
        labels={"cluster_name": "Segment", "revenue": "Revenue (€)", "customers": "Customers"},
    )
    bar.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(bar, width="stretch")

st.subheader("Segment profiles")
profiles = summary.rename(
    columns={
        "cluster_name": "Segment",
        "customers": "Customers",
        "average_recency_days": "Avg. recency (days)",
        "average_orders": "Avg. orders",
        "revenue": "Revenue (€)",
    }
).drop(columns="cluster")
st.dataframe(profiles, width="stretch", hide_index=True)
st.download_button("Download customer segments", clusters.to_csv(index=False).encode("utf-8"), "customer_segments.csv", "text/csv", width="content")
