"""Forecasting, anomaliedetectie en actioneerbare sales alerts."""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.analysis import monthly_performance, revenue_vs_target


def forecast_monthly_revenue(data: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """Voorspel maandelijkse omzet met Holt's trendmodel."""
    historical = monthly_performance(data)[["month", "revenue"]].copy()
    if len(historical) < 6:
        raise ValueError("At least six months of data are required for a forecast.")
    model = ExponentialSmoothing(historical["revenue"], trend="add", initialization_method="estimated").fit(optimized=True)
    future_months = pd.date_range(historical["month"].max() + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    forecast = pd.DataFrame({"month": future_months, "revenue": model.forecast(periods).round(2), "series": "Forecast"})
    historical["series"] = "Actual"
    return pd.concat([historical, forecast], ignore_index=True)


def detect_monthly_anomalies(data: pd.DataFrame, threshold: float = 1.75) -> pd.DataFrame:
    """Markeer maanden met uitzonderlijke omzet op basis van z-scores."""
    monthly = monthly_performance(data)[["month", "revenue"]].copy()
    standard_deviation = monthly["revenue"].std(ddof=0)
    monthly["z_score"] = 0.0 if standard_deviation == 0 else ((monthly["revenue"] - monthly["revenue"].mean()) / standard_deviation).round(2)
    monthly["is_anomaly"] = monthly["z_score"].abs() >= threshold
    return monthly


def generate_alerts(data: pd.DataFrame, targets: pd.DataFrame) -> list[dict[str, str]]:
    """Geef compacte, actioneerbare alerts op basis van target en afwijkingen."""
    alerts: list[dict[str, str]] = []
    latest_target = revenue_vs_target(data, targets).sort_values("month").iloc[-1]
    if latest_target["target_attainment_percent"] < 100:
        alerts.append({"level": "warning", "message": f"{latest_target['month']:%b %Y} closed {latest_target['target_attainment_percent']:.1f}% of revenue target."})
    for anomaly in detect_monthly_anomalies(data).query("is_anomaly").tail(2).itertuples():
        direction = "above" if anomaly.z_score > 0 else "below"
        alerts.append({"level": "info", "message": f"{anomaly.month:%b %Y} revenue was unusually {direction} trend (z-score {anomaly.z_score:+.2f})."})
    return alerts
