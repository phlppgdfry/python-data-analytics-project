"""Vertaal schone transactiegegevens naar zakelijke inzichten."""

import pandas as pd

from src.statistics import summarize_order_values


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


def calculate_profit_kpis(data: pd.DataFrame) -> dict[str, float]:
    """Bereken brutowinst en brutomarge voor de geselecteerde verkopen."""
    total_revenue = float(data["revenue"].sum())
    gross_profit = float(data["gross_profit"].sum())
    return {
        "gross_profit": round(gross_profit, 2),
        "margin_percent": round(gross_profit / total_revenue * 100, 2) if total_revenue else 0.0,
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


def profit_by_country(data: pd.DataFrame) -> pd.DataFrame:
    """Tel brutowinst op per land."""
    return data.groupby("country", as_index=False)["gross_profit"].sum().sort_values("gross_profit", ascending=False)


def profit_by_product(data: pd.DataFrame) -> pd.DataFrame:
    """Tel brutowinst op per product."""
    return data.groupby("product", as_index=False)["gross_profit"].sum().sort_values("gross_profit", ascending=False)


def revenue_vs_target(data: pd.DataFrame, monthly_targets: pd.DataFrame) -> pd.DataFrame:
    """Vergelijk werkelijke omzet met het maandelijkse omzetdoel."""
    actual = revenue_by_month(data)
    result = actual.merge(monthly_targets, on="month", how="left", validate="one_to_one")
    result["variance"] = (result["revenue"] - result["target_revenue"]).round(2)
    result["target_attainment_percent"] = (result["revenue"] / result["target_revenue"] * 100).round(1)
    return result


def top_customers(data: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Geef de klanten met de hoogste omzet inclusief orderaantal en winst."""
    return (
        data.groupby("customer_id", as_index=False)
        .agg(revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(limit)
    )


def customer_lifecycle(all_data: pd.DataFrame, selected_data: pd.DataFrame) -> pd.DataFrame:
    """Classificeer geselecteerde klanten als nieuw of terugkerend."""
    first_orders = all_data.groupby("customer_id", as_index=False)["order_date"].min().rename(columns={"order_date": "first_order_date"})
    selected_customers = (
        selected_data.groupby("customer_id", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
        .merge(first_orders, on="customer_id", validate="one_to_one")
    )
    period_start = selected_data["order_date"].min()
    period_end = selected_data["order_date"].max()
    selected_customers["customer_type"] = selected_customers["first_order_date"].between(period_start, period_end).map({True: "New", False: "Returning"})
    return selected_customers


def rfm_segments(data: pd.DataFrame) -> pd.DataFrame:
    """Maak een RFM-score (recency, frequency, monetary) per klant."""
    reference_date = data["order_date"].max() + pd.Timedelta(days=1)
    rfm = data.groupby("customer_id", as_index=False).agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
    )
    rfm["recency_days"] = (reference_date - rfm["last_order_date"]).dt.days
    def quartile_score(values: pd.Series, higher_is_better: bool) -> pd.Series:
        """Geef ook bij kleine, gefilterde selecties een stabiele score van 1 tot 4."""
        percentile = values.rank(method="first", pct=True, ascending=higher_is_better)
        return (percentile * 4).apply(lambda score: max(1, min(4, int(score - 1e-9) + 1)))

    rfm["recency_score"] = quartile_score(rfm["recency_days"], higher_is_better=False)
    rfm["frequency_score"] = quartile_score(rfm["frequency"], higher_is_better=True)
    rfm["monetary_score"] = quartile_score(rfm["monetary"], higher_is_better=True)

    def label_segment(row: pd.Series) -> str:
        if row["recency_score"] >= 3 and row["frequency_score"] >= 3 and row["monetary_score"] >= 3:
            return "Champions"
        if row["recency_score"] >= 3 and row["frequency_score"] >= 2:
            return "Loyal"
        if row["recency_score"] <= 2 and row["frequency_score"] >= 3:
            return "At risk"
        return "Potential"

    rfm["segment"] = rfm.apply(label_segment, axis=1)
    return rfm.sort_values(["monetary", "frequency"], ascending=False).reset_index(drop=True)


def rfm_segment_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Vat klantsegmenten samen voor een dashboardgrafiek."""
    return (
        rfm_segments(data)
        .groupby("segment", as_index=False)
        .agg(customers=("customer_id", "nunique"), revenue=("monetary", "sum"))
        .sort_values("revenue", ascending=False)
    )


def cohort_retention(data: pd.DataFrame) -> pd.DataFrame:
    """Bereken retentie per acquisitiecohort en maand sinds eerste aankoop."""
    orders = data[["customer_id", "order_date"]].copy()
    orders["order_month"] = orders["order_date"].dt.to_period("M")
    first_order_month = orders.groupby("customer_id")["order_month"].transform("min")
    orders["cohort_month"] = first_order_month
    orders["cohort_index"] = (orders["order_month"].dt.year - orders["cohort_month"].dt.year) * 12 + (orders["order_month"].dt.month - orders["cohort_month"].dt.month)
    counts = orders.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().unstack(fill_value=0)
    retention = counts.div(counts[0], axis=0).round(3)
    retention.index = retention.index.astype(str)
    retention.index.name = "cohort_month"
    return retention


def calculate_order_statistics(data: pd.DataFrame) -> dict[str, float]:
    """Pas NumPy-statistiek toe op de totale waarde per order."""
    return summarize_order_values(order_totals(data)["revenue"])
