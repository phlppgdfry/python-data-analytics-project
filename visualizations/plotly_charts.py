"""Interactieve HTML-grafieken voor browser en dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px


def create_interactive_charts(monthly_data: pd.DataFrame, country_data: pd.DataFrame, product_data: pd.DataFrame, output_dir: str | Path) -> list[Path]:
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
    return outputs
