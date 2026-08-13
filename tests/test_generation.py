import pandas as pd

from src.generate_sample_data import generate_sales_data


def test_generator_creates_three_years_of_realistic_source_data(tmp_path):
    sales_path = tmp_path / "sales.csv"
    targets_path = tmp_path / "monthly_targets.csv"
    customers_path = tmp_path / "customers.csv"

    count = generate_sales_data(sales_path, targets_path, customers_path)
    sales = pd.read_csv(sales_path)
    targets = pd.read_csv(targets_path)
    customers = pd.read_csv(customers_path)

    assert count == len(sales)
    assert len(targets) == 36
    assert {"Boots", "Sportswear"}.issubset(set(sales["product"].str.title()))
    assert not set(["C997", "C998", "C999"]).intersection(customers["customer_id"])
