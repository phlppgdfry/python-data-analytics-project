"""Pandera-contracten voor betrouwbare gezuiverde sales-data."""

import pandera.pandas as pa


SALES_SCHEMA = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, checks=pa.Check.greater_than(0), unique=True),
        "order_date": pa.Column(pa.DateTime),
        "customer_id": pa.Column(str, checks=pa.Check.str_matches(r"^C\d{3}$")),
        "country": pa.Column(str, checks=pa.Check.isin(["Belgium", "France", "Netherlands", "Germany", "United Kingdom", "Spain", "Italy", "Sweden"])),
        "product": pa.Column(str, checks=pa.Check.isin(["Shoes", "Shirt", "Jacket", "Accessories", "Sneakers", "Boots", "Sportswear"])),
        "quantity": pa.Column(int, checks=pa.Check.in_range(1, 100)),
        "price": pa.Column(float, checks=pa.Check.greater_than(0)),
        "unit_cost": pa.Column(float, checks=pa.Check.greater_than(0)),
        "revenue": pa.Column(float, checks=pa.Check.greater_than(0)),
        "gross_profit": pa.Column(float, checks=pa.Check.greater_than(0)),
        "margin_percent": pa.Column(float, checks=pa.Check.in_range(0, 100)),
    },
    strict=True,
    coerce=True,
)


def validate_clean_sales_data(data):
    """Valideer de contractuele vorm én zakelijke grenzen van sales-data."""
    validated_data = SALES_SCHEMA.validate(data, lazy=True)
    if (validated_data["unit_cost"] >= validated_data["price"]).any():
        raise ValueError("Unit cost must be lower than sales price.")
    return validated_data
