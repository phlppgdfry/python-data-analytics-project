import pandas as pd

from src.analysis import (
    calculate_kpis,
    calculate_period_comparison,
    filter_sales_data,
    monthly_performance,
    previous_period_bounds,
    revenue_by_country,
)


def test_calculate_kpis_and_country_revenue():
    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "order_date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "customer_id": ["C1", "C1", "C2"],
            "country": ["Belgium", "France", "Belgium"],
            "product": ["Shoes", "Shirt", "Jacket"],
            "revenue": [100.0, 50.0, 200.0],
        }
    )
    assert calculate_kpis(data) == {
        "total_revenue": 350.0,
        "orders": 3,
        "customers": 2,
        "average_order_value": 116.67,
    }
    assert revenue_by_country(data).iloc[0].to_dict() == {"country": "Belgium", "revenue": 300.0}


def test_filter_sales_data_uses_all_filters_and_includes_boundary_dates():
    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "order_date": pd.to_datetime(["2026-01-01", "2026-01-31", "2026-02-01"]),
            "customer_id": ["C1", "C2", "C3"],
            "country": ["Belgium", "France", "Belgium"],
            "product": ["Shoes", "Shirt", "Shoes"],
            "revenue": [100.0, 50.0, 200.0],
        }
    )

    filtered_data = filter_sales_data(
        data,
        countries=["Belgium"],
        products=["Shoes"],
        start_date="2026-01-01",
        end_date="2026-01-31",
    )

    assert filtered_data["order_id"].tolist() == [1]


def test_period_comparison_and_monthly_performance():
    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "order_date": pd.to_datetime(["2025-01-01", "2025-01-31", "2025-02-01", "2025-02-28"]),
            "customer_id": ["C1", "C2", "C3", "C4"],
            "country": ["Belgium"] * 4,
            "product": ["Shoes"] * 4,
            "revenue": [100.0, 100.0, 150.0, 150.0],
        }
    )
    previous_start, previous_end = previous_period_bounds("2025-02-01", "2025-02-28")
    previous = filter_sales_data(data, ["Belgium"], ["Shoes"], previous_start, previous_end)
    current = filter_sales_data(data, ["Belgium"], ["Shoes"], "2025-02-01", "2025-02-28")

    assert (previous_start, previous_end) == (pd.Timestamp("2025-01-04"), pd.Timestamp("2025-01-31"))
    assert calculate_period_comparison(current, previous) == {"revenue_change_percent": 200.0, "orders_change_percent": 100.0}
    assert monthly_performance(data).to_dict("records") == [
        {"month": pd.Timestamp("2025-01-01"), "revenue": 200.0, "orders": 2},
        {"month": pd.Timestamp("2025-02-01"), "revenue": 300.0, "orders": 2},
    ]


def test_profit_target_and_customer_analyses():
    from src.analysis import calculate_profit_kpis, revenue_vs_target, top_customers

    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "order_date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-02-01"]),
            "customer_id": ["C1", "C1", "C2"],
            "country": ["Belgium", "Belgium", "France"],
            "product": ["Shoes", "Jacket", "Shirt"],
            "revenue": [100.0, 200.0, 50.0],
            "gross_profit": [40.0, 80.0, 20.0],
        }
    )
    targets = pd.DataFrame({"month": pd.to_datetime(["2025-01-01", "2025-02-01"]), "target_revenue": [250.0, 60.0]})

    assert calculate_profit_kpis(data) == {"gross_profit": 140.0, "margin_percent": 40.0}
    assert revenue_vs_target(data, targets)["target_attainment_percent"].tolist() == [120.0, 83.3]
    assert top_customers(data, limit=1).iloc[0].to_dict() == {"customer_id": "C1", "revenue": 300.0, "gross_profit": 120.0, "orders": 2}


def test_customer_lifecycle_and_cohort_retention():
    from src.analysis import cohort_retention, customer_lifecycle

    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "order_date": pd.to_datetime(["2025-01-05", "2025-02-10", "2025-02-12", "2025-03-01"]),
            "customer_id": ["C001", "C001", "C002", "C002"],
            "country": ["Belgium"] * 4,
            "product": ["Shoes"] * 4,
            "revenue": [100.0, 100.0, 50.0, 50.0],
            "gross_profit": [40.0, 40.0, 20.0, 20.0],
        }
    )
    selected_data = data[data["order_date"].between("2025-02-01", "2025-03-31")]

    lifecycle_data = customer_lifecycle(data, selected_data)
    retention = cohort_retention(data)

    assert lifecycle_data.sort_values("customer_id")["customer_type"].tolist() == ["Returning", "New"]
    assert retention.loc["2025-01", 1] == 1.0
    assert retention.loc["2025-02", 1] == 1.0


def test_forecast_and_anomaly_detection():
    from src.forecasting import detect_monthly_anomalies, forecast_monthly_revenue

    dates = pd.date_range("2024-01-01", periods=12, freq="MS")
    data = pd.DataFrame(
        {
            "order_id": range(1, 13),
            "order_date": dates,
            "customer_id": [f"C{number:03d}" for number in range(1, 13)],
            "country": ["Belgium"] * 12,
            "product": ["Shoes"] * 12,
            "revenue": [100.0 * (index + 1) for index in range(12)],
            "gross_profit": [40.0 * (index + 1) for index in range(12)],
        }
    )

    forecast = forecast_monthly_revenue(data, periods=3)
    anomalies = detect_monthly_anomalies(data)

    assert forecast["series"].value_counts().to_dict() == {"Actual": 12, "Forecast": 3}
    assert len(anomalies) == 12
