"""Laad gereinigde CSV-data reproduceerbaar in de lokale PostgreSQL-container."""

import os
from pathlib import Path
import sys

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.clean_data import clean_sales_data
from src.load_data import load_customer_directory_csv, load_monthly_targets_csv, load_sales_csv


def load_data_to_postgres(database_url: str | None = None) -> dict[str, int]:
    """Vervang lokale analyse-tabellen door de nieuwste schoongemaakte brondata."""
    database_url = database_url or os.environ["DATABASE_URL"]
    sales_data = clean_sales_data(load_sales_csv())
    targets_data = load_monthly_targets_csv()
    customer_data = load_customer_directory_csv()
    engine = create_engine(database_url)

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE sales_orders, monthly_targets, customers"))
        sales_data.to_sql("sales_orders", connection, if_exists="append", index=False, method="multi")
        targets_data.to_sql("monthly_targets", connection, if_exists="append", index=False, method="multi")
        customer_data.to_sql("customers", connection, if_exists="append", index=False, method="multi")

    return {"sales_orders": len(sales_data), "monthly_targets": len(targets_data), "customers": len(customer_data)}


if __name__ == "__main__":
    database_url = os.environ["DATABASE_URL"]
    results = load_data_to_postgres(database_url)
    print(f"Loaded PostgreSQL tables: {results}")
