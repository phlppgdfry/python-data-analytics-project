import pandas as pd
import pytest
from pandera.errors import SchemaErrors

from src.validation import validate_clean_sales_data


def test_validation_rejects_an_invalid_customer_identifier():
    data = pd.DataFrame(
        {
            "order_id": [1],
            "order_date": pd.to_datetime(["2025-01-01"]),
            "customer_id": ["C1"],
            "country": ["Belgium"],
            "product": ["Shoes"],
            "quantity": [1],
            "price": [100.0],
            "unit_cost": [40.0],
            "revenue": [100.0],
            "gross_profit": [60.0],
            "margin_percent": [60.0],
        }
    )

    with pytest.raises(SchemaErrors):
        validate_clean_sales_data(data)
