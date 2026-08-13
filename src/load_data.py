"""Functies om verkoopdata uit CSV of PostgreSQL te laden."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"


def load_sales_csv(path: str | Path = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """Lees de ruwe CSV zonder de waarden al te veranderen."""
    return pd.read_csv(path)


def load_sales_from_postgres(database_url: str, query: str) -> pd.DataFrame:
    """Voer een SQL-query uit en geef de resultaten als DataFrame terug."""
    engine = create_engine(database_url)
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
