import pandas as pd

from src.analytics_store import query_revenue_by_country, save_analytics_parquet


def test_parquet_export_can_be_queried_with_duckdb(tmp_path):
    data = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "country": ["Belgium", "France", "Belgium"],
            "revenue": [100.25, 50.0, 99.75],
        }
    )
    parquet_path = save_analytics_parquet(data, tmp_path / "sales.parquet")

    result = query_revenue_by_country(parquet_path)

    assert result.to_dict("records") == [
        {"country": "Belgium", "revenue": 200.0, "orders": 2},
        {"country": "France", "revenue": 50.0, "orders": 1},
    ]
