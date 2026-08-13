"""Statische PNG-grafieken voor een rapport of presentatie."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _save_figure(filename: str, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    output_path = directory / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def create_static_charts(monthly_data: pd.DataFrame, country_data: pd.DataFrame, product_data: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    """Maak drie herbruikbare rapportgrafieken."""
    plt.style.use("seaborn-v0_8-whitegrid")
    outputs = []

    plt.figure(figsize=(9, 4.5))
    plt.plot(monthly_data["month"], monthly_data["revenue"], marker="o", color="#2563eb")
    plt.title("Monthly revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue (€)")
    outputs.append(_save_figure("monthly_revenue.png", output_dir))

    plt.figure(figsize=(7, 4.5))
    plt.bar(country_data["country"], country_data["revenue"], color="#0f766e")
    plt.title("Revenue by country")
    plt.xlabel("Country")
    plt.ylabel("Revenue (€)")
    outputs.append(_save_figure("revenue_by_country.png", output_dir))

    plt.figure(figsize=(7, 4.5))
    plt.bar(product_data["product"], product_data["revenue"], color="#7c3aed")
    plt.title("Revenue by product")
    plt.xlabel("Product")
    plt.ylabel("Revenue (€)")
    outputs.append(_save_figure("revenue_by_product.png", output_dir))
    return outputs
