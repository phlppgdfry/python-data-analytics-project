"""Functies om verkoopdata uit CSV of PostgreSQL te laden."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"
DEFAULT_TARGETS_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "monthly_targets.csv"
DEFAULT_CUSTOMERS_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "customers.csv"


def load_sales_csv(path: str | Path = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """Lees de ruwe CSV zonder de waarden al te veranderen."""
    return pd.read_csv(path)


def load_monthly_targets_csv(path: str | Path = DEFAULT_TARGETS_CSV_PATH) -> pd.DataFrame:
    """Lees maandelijkse omzetdoelen in als date-aware DataFrame."""
    targets = pd.read_csv(path, parse_dates=["month"])
    return targets.sort_values("month").reset_index(drop=True)


def load_customer_directory_csv(path: str | Path = DEFAULT_CUSTOMERS_CSV_PATH) -> pd.DataFrame:
    """Lees het synthetische klantenbestand in."""
    return pd.read_csv(path, parse_dates=["customer_since"]).sort_values("customer_id").reset_index(drop=True)


def load_sales_from_postgres(database_url: str, query: str) -> pd.DataFrame:
    """Voer een SQL-query uit en geef de resultaten als DataFrame terug."""
    engine = create_engine(database_url)
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
