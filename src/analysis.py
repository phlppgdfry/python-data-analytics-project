"""Vertaal schone transactiegegevens naar zakelijke inzichten."""

import pandas as pd

from statistics import summarize_order_values


def order_totals(data: pd.DataFrame) -> pd.DataFrame:
    """Bundel mogelijke orderregels tot één totaal per order."""
    return data.groupby("order_id", as_index=False).agg(
        order_date=("order_date", "min"),
        customer_id=("customer_id", "first"),
        revenue=("revenue", "sum"),
    )


def calculate_kpis(data: pd.DataFrame) -> dict[str, float | int]:
    """Bereken de KPI-kaarten voor het rapport en dashboard."""
    orders = order_totals(data)
    return {
        "total_revenue": round(float(data["revenue"].sum()), 2),
        "orders": int(orders["order_id"].nunique()),
        "customers": int(data["customer_id"].nunique()),
        "average_order_value": round(float(orders["revenue"].mean()), 2),
    }


def revenue_by_month(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per kalendermaand."""
    result = data.assign(month=data["order_date"].dt.to_period("M").dt.to_timestamp())
    return result.groupby("month", as_index=False)["revenue"].sum().sort_values("month")


def revenue_by_country(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per land, hoog naar laag."""
    return data.groupby("country", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)


def revenue_by_product(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per product, hoog naar laag."""
    return data.groupby("product", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)


def calculate_order_statistics(data: pd.DataFrame) -> dict[str, float]:
    """Pas NumPy-statistiek toe op de totale waarde per order."""
    return summarize_order_values(order_totals(data)["revenue"])
