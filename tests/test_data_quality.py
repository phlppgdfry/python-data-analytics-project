import pandas as pd

from src.data_quality import build_data_quality_report


def test_data_quality_report_counts_removed_and_duplicate_rows():
    raw_data = pd.DataFrame({"order_id": [1, 1, 2, 3]})
    cleaned_data = pd.DataFrame({"order_id": [1, 2]})

    assert build_data_quality_report(raw_data, cleaned_data) == {
        "raw_rows": 4,
        "clean_rows": 2,
        "removed_rows": 2,
        "duplicate_orders": 1,
        "retention_percent": 50.0,
    }
