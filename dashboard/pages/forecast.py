"""Forecast- en alertpagina."""

import streamlit as st

from dashboard.shared import get_dashboard_context, page_intro
from src.forecasting import detect_monthly_anomalies, evaluate_forecast_models, forecast_monthly_revenue, generate_alerts
from visualizations.plotly_charts import create_forecast_chart, create_forecast_evaluation_chart


context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("Forecast & alerts", "Een technische vooruitblik op omzet en opvallende afwijkingen in de volledige verkoopgeschiedenis.")
st.info("Forecasts and alerts intentionally use the full business history, not the current filters, so the time series remains stable.")
forecast_data = forecast_monthly_revenue(context.data)
st.plotly_chart(create_forecast_chart(forecast_data), width="stretch")

forecast_only = forecast_data.query("series == 'Forecast'").copy()
forecast_only["month"] = forecast_only["month"].dt.strftime("%b %Y")
forecast_only = forecast_only.rename(columns={"month": "Month", "revenue": "Forecast revenue (€)"}).drop(columns="series")
st.dataframe(forecast_only, width="stretch", hide_index=True)
st.download_button("Download three-month forecast", forecast_only.to_csv(index=False).encode("utf-8"), "revenue_forecast.csv", "text/csv", width="content")

st.subheader("Model evaluation")
st.caption("The final six historical months are held back from training. Lower MAE/RMSE means a more accurate forecast on unseen data; this is more credible than reporting a training score.")
backtest_predictions, model_metrics = evaluate_forecast_models(context.data)
metric_columns = st.columns(len(model_metrics))
for column, metric in zip(metric_columns, model_metrics.itertuples()):
    with column:
        st.metric(f"{metric.model} MAE", f"€{metric.MAE:,.0f}", help=f"RMSE: €{metric.RMSE:,.0f}. MAE is the average absolute monthly prediction error.")
st.plotly_chart(create_forecast_evaluation_chart(backtest_predictions), width="stretch")
st.dataframe(model_metrics.rename(columns={"model": "Model"}), width="stretch", hide_index=True)

st.subheader("Automated alerts")
alerts = generate_alerts(context.data, context.monthly_targets)
if alerts:
    for alert in alerts:
        getattr(st, alert["level"])(alert["message"])
else:
    st.success("No material anomalies or target risks detected.")

st.subheader("Detected monthly anomalies")
anomalies = detect_monthly_anomalies(context.data)
anomalies["month"] = anomalies["month"].dt.strftime("%b %Y")
anomalies = anomalies.rename(columns={"month": "Month", "revenue": "Revenue (€)", "z_score": "Z-score", "is_anomaly": "Anomaly"})
st.dataframe(anomalies[anomalies["Anomaly"]], width="stretch", hide_index=True)
