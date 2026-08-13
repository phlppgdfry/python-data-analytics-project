"""Interactieve HTML-grafieken voor browser en dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_monthly_performance_chart(performance_data: pd.DataFrame) -> go.Figure:
    """Maak een gecombineerde omzet- en ordergrafiek met twee schalen."""
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(go.Bar(x=performance_data["month"], y=performance_data["revenue"], name="Revenue", marker_color="#2563EB"), secondary_y=False)
    figure.add_trace(go.Scatter(x=performance_data["month"], y=performance_data["orders"], name="Orders", mode="lines+markers", line={"color": "#F97316", "width": 3}), secondary_y=True)
    figure.update_layout(
        template="plotly_white",
        title={"text": "Monthly revenue and orders", "x": 0, "xanchor": "left", "y": 0.98, "yanchor": "top"},
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 0.87, "yanchor": "top"},
        margin={"l": 0, "r": 0, "t": 110, "b": 0},
    )
    figure.update_yaxes(title_text="Revenue (€)", secondary_y=False)
    figure.update_yaxes(title_text="Orders", secondary_y=True)
    return figure


def create_actual_vs_target_chart(target_data: pd.DataFrame) -> go.Figure:
    """Toon werkelijke omzet als kolommen tegenover een maandtargetlijn."""
    figure = go.Figure()
    figure.add_trace(go.Bar(x=target_data["month"], y=target_data["revenue"], name="Actual revenue", marker_color="#2563EB"))
    figure.add_trace(go.Scatter(x=target_data["month"], y=target_data["target_revenue"], name="Revenue target", mode="lines+markers", line={"color": "#F97316", "width": 3, "dash": "dash"}))
    figure.update_layout(
        template="plotly_white",
        title={"text": "Actual revenue vs target", "x": 0, "xanchor": "left"},
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.02, "yanchor": "bottom"},
        margin={"l": 0, "r": 0, "t": 85, "b": 0},
        yaxis_title="Revenue (€)",
    )
    return figure


def create_cohort_retention_chart(retention_data: pd.DataFrame) -> go.Figure:
    """Maak een heatmap die klantretentie per cohort toont."""
    figure = px.imshow(
        retention_data,
        text_auto=".0%",
        aspect="auto",
        color_continuous_scale="Blues",
        labels={"x": "Months since first purchase", "y": "Customer cohort", "color": "Retention"},
    )
    figure.update_layout(template="plotly_white", title={"text": "Customer retention by cohort", "x": 0, "xanchor": "left"}, margin={"l": 0, "r": 0, "t": 55, "b": 0})
    return figure


def create_interactive_charts(monthly_data: pd.DataFrame, country_data: pd.DataFrame, product_data: pd.DataFrame, output_dir: str | Path, performance_data: pd.DataFrame | None = None) -> list[Path]:
    """Schrijf dezelfde kerninzichten als interactieve HTML weg."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    charts = [
        (px.line(monthly_data, x="month", y="revenue", markers=True, title="Monthly revenue"), "monthly_revenue.html"),
        (px.bar(country_data, x="country", y="revenue", title="Revenue by country"), "revenue_by_country.html"),
        (px.bar(product_data, x="product", y="revenue", title="Revenue by product"), "revenue_by_product.html"),
    ]
    outputs = []
    for figure, filename in charts:
        figure.update_layout(template="plotly_white", yaxis_title="Revenue (€)")
        output_path = directory / filename
        figure.write_html(output_path, include_plotlyjs="cdn")
        outputs.append(output_path)
    if performance_data is not None:
        output_path = directory / "monthly_performance.html"
        create_monthly_performance_chart(performance_data).write_html(output_path, include_plotlyjs="cdn")
        outputs.append(output_path)
    return outputs
