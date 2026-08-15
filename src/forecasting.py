"""Forecasting, anomaliedetectie en actioneerbare sales alerts."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
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


def evaluate_forecast_models(data: pd.DataFrame, holdout_months: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Vergelijk Holt met een Random Forest op de laatste, ongeziene maanden.

    De holdout is essentieel: een model beoordelen op trainingsdata geeft een
    te rooskleurig beeld. MAE is de gemiddelde fout in euro; RMSE straft grote
    missers zwaarder. Random Forest krijgt alleen kalender- en tijdsfeatures,
    zodat er geen toekomstige omzet in de voorspelling kan lekken.
    """
    historical = monthly_performance(data)[["month", "revenue"]].copy().reset_index(drop=True)
    if len(historical) < holdout_months + 6:
        raise ValueError("At least twelve months of data are required for forecast evaluation.")

    training = historical.iloc[:-holdout_months].copy()
    actual = historical.iloc[-holdout_months:].copy()
    holt = ExponentialSmoothing(training["revenue"], trend="add", initialization_method="estimated").fit(optimized=True)
    holt_predictions = holt.forecast(holdout_months).to_numpy()

    def features(frame: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "time_index": (frame["month"].dt.year - historical["month"].dt.year.min()) * 12 + frame["month"].dt.month,
                "month_sin": np.sin(2 * np.pi * frame["month"].dt.month / 12),
                "month_cos": np.cos(2 * np.pi * frame["month"].dt.month / 12),
            }
        )

    forest = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42)
    forest.fit(features(training), training["revenue"])
    forest_predictions = forest.predict(features(actual))
    predictions = pd.concat(
        [
            pd.DataFrame({"month": actual["month"], "actual_revenue": actual["revenue"], "predicted_revenue": holt_predictions, "model": "Holt trend"}),
            pd.DataFrame({"month": actual["month"], "actual_revenue": actual["revenue"], "predicted_revenue": forest_predictions, "model": "Random forest"}),
        ],
        ignore_index=True,
    )
    predictions["absolute_error"] = (predictions["actual_revenue"] - predictions["predicted_revenue"]).abs()
    predictions["squared_error"] = (predictions["actual_revenue"] - predictions["predicted_revenue"]) ** 2
    metrics = (
        predictions.groupby("model", as_index=False)
        .agg(MAE=("absolute_error", "mean"), mean_squared_error=("squared_error", "mean"))
        .assign(RMSE=lambda result: result.pop("mean_squared_error") ** 0.5)
        .round(2)
        .sort_values("MAE")
        .reset_index(drop=True)
    )
    return predictions.drop(columns="squared_error"), metrics


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
