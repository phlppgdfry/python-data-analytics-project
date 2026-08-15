"""Parquet-export en lokale analytische SQL met DuckDB."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.parquet"


def save_analytics_parquet(data: pd.DataFrame, path: str | Path = ANALYTICS_PARQUET_PATH) -> Path:
    """Bewaar het schone resultaat als kolomformaat voor snelle analyses."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_parquet(output_path, index=False)
    return output_path


def query_revenue_by_country(path: str | Path = ANALYTICS_PARQUET_PATH) -> pd.DataFrame:
    """Toon DuckDB-SQL rechtstreeks op Parquet, zonder een server te starten."""
    try:
        import duckdb
    except ImportError as error:  # pragma: no cover - dependency feedback for manual users
        raise RuntimeError("Install DuckDB first: python -m pip install duckdb") from error

    parquet_path = Path(path)
    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}. Run the pipeline first.")
    return duckdb.execute(
        """
        SELECT country, ROUND(SUM(revenue), 2) AS revenue, COUNT(DISTINCT order_id) AS orders
        FROM read_parquet(?)
        GROUP BY country
        ORDER BY revenue DESC
        """,
        [str(parquet_path)],
    ).df()
