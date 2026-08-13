import pandas as pd

from analysis import calculate_kpis, filter_sales_data, revenue_by_country


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
