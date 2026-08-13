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


def filter_sales_data(
    data: pd.DataFrame,
    countries: list[str],
    products: list[str],
    start_date: object,
    end_date: object,
) -> pd.DataFrame:
    """Filter sales-data inclusief de gekozen begin- en einddatum."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    matches = (
        data["country"].isin(countries)
        & data["product"].isin(products)
        & data["order_date"].between(start, end)
    )
    return data.loc[matches].copy()


def previous_period_bounds(start_date: object, end_date: object) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Geef de even lange periode vlak vóór de gekozen periode terug."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    period_length = (end - start).days + 1
    previous_end = start - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=period_length - 1)
    return previous_start, previous_end


def calculate_period_comparison(current_data: pd.DataFrame, previous_data: pd.DataFrame) -> dict[str, float | int | None]:
    """Vergelijk omzet en orders met de direct voorafgaande periode."""
    current = calculate_kpis(current_data)
    previous = calculate_kpis(previous_data) if not previous_data.empty else {"total_revenue": 0.0, "orders": 0}

    def percentage_change(current_value: float | int, previous_value: float | int) -> float | None:
        if previous_value == 0:
            return None
        return round((current_value - previous_value) / previous_value * 100, 1)

    return {
        "revenue_change_percent": percentage_change(current["total_revenue"], previous["total_revenue"]),
        "orders_change_percent": percentage_change(current["orders"], previous["orders"]),
    }


def revenue_by_month(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per kalendermaand."""
    result = data.assign(month=data["order_date"].dt.to_period("M").dt.to_timestamp())
    return result.groupby("month", as_index=False)["revenue"].sum().sort_values("month")


def monthly_performance(data: pd.DataFrame) -> pd.DataFrame:
    """Bereken omzet en unieke orders per kalendermaand."""
    result = data.assign(month=data["order_date"].dt.to_period("M").dt.to_timestamp())
    return (
        result.groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
        .sort_values("month")
    )


def revenue_by_country(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per land, hoog naar laag."""
    return data.groupby("country", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)


def revenue_by_product(data: pd.DataFrame) -> pd.DataFrame:
    """Tel omzet op per product, hoog naar laag."""
    return data.groupby("product", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)


def calculate_order_statistics(data: pd.DataFrame) -> dict[str, float]:
    """Pas NumPy-statistiek toe op de totale waarde per order."""
    return summarize_order_values(order_totals(data)["revenue"])
