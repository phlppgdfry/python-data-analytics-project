import pandas as pd

from src.clean_data import clean_sales_data


def test_cleaning_normalizes_values_and_removes_invalid_rows():
    raw_data = pd.DataFrame(
        {
            "order_id": [1, 1, 2, 3],
            "order_date": ["2026-01-01"] * 4,
            "customer_id": ["C1", "C1", "C2", "C3"],
            "country": [" BELGIUM ", "Belgium", "France", "Unknown"],
            "product": [" shoes ", "Shoes", "shirt", "Jacket"],
            "quantity": [2, 2, 1, 1],
            "price": ["€10,50", "€10,50", "20.00", "50.00"],
        }
    )
    cleaned_data = clean_sales_data(raw_data)
    assert len(cleaned_data) == 2
    assert cleaned_data.loc[0, "country"] == "Belgium"
    assert cleaned_data.loc[0, "product"] == "Shoes"
    assert cleaned_data.loc[0, "revenue"] == 21.0
