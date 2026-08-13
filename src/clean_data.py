"""Maak ruwe sales-data betrouwbaar en analyseerbaar."""

from pathlib import Path

import pandas as pd

from src.validation import validate_clean_sales_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"
REQUIRED_COLUMNS = ["order_id", "order_date", "customer_id", "country", "product", "quantity", "price", "unit_cost"]
COUNTRY_NAMES = {
    "belgium": "Belgium",
    "france": "France",
    "netherlands": "Netherlands",
    "germany": "Germany",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
}


def _parse_price(value: object) -> float | None:
    """Zet bijvoorbeeld '€49.99' en '49,99' om naar een getal."""
    if pd.isna(value):
        return None
    cleaned = str(value).strip().replace("€", "").replace(" ", "")
    return pd.to_numeric(cleaned.replace(",", "."), errors="coerce")


def clean_sales_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Normaliseer data, verwijder onbruikbare rijen en bereken omzet."""
    missing_columns = set(REQUIRED_COLUMNS) - set(raw_data.columns)
    if missing_columns:
        raise ValueError(f"Ontbrekende kolommen: {sorted(missing_columns)}")

    data = raw_data.copy()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    data["country"] = data["country"].astype("string").str.strip().str.lower().map(COUNTRY_NAMES)
    data["product"] = data["product"].astype("string").str.strip().str.title()
    data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce")
    data["price"] = data["price"].map(_parse_price)
    data["unit_cost"] = data["unit_cost"].map(_parse_price)

    data = data.drop_duplicates(subset="order_id")
    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data.query("quantity > 0 and quantity <= 100 and price > 0 and unit_cost > 0 and unit_cost < price")
    data["quantity"] = data["quantity"].astype(int)
    data["revenue"] = (data["quantity"] * data["price"]).round(2)
    data["gross_profit"] = (data["quantity"] * (data["price"] - data["unit_cost"])).round(2)
    data["margin_percent"] = (data["gross_profit"] / data["revenue"] * 100).round(2)
    cleaned_data = data.sort_values(["order_date", "order_id"]).reset_index(drop=True)
    return validate_clean_sales_data(cleaned_data)


def save_cleaned_sales_data(data: pd.DataFrame, path: str | Path = PROCESSED_DATA_PATH) -> Path:
    """Schrijf de schoongemaakte data weg en geef het outputpad terug."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    return output_path
