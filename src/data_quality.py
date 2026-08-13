"""Meet en rapporteer datakwaliteit vóór en na de cleaning-pipeline."""

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.json"


def build_data_quality_report(raw_data: pd.DataFrame, cleaned_data: pd.DataFrame) -> dict[str, int | float]:
    """Geef transparante aantallen voor verwijderde en behouden rijen."""
    raw_rows = len(raw_data)
    clean_rows = len(cleaned_data)
    duplicate_orders = int(raw_data.duplicated(subset="order_id").sum())
    return {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "removed_rows": raw_rows - clean_rows,
        "duplicate_orders": duplicate_orders,
        "retention_percent": round(clean_rows / raw_rows * 100, 2) if raw_rows else 0.0,
    }


def save_data_quality_report(report: dict[str, int | float], path: str | Path = DEFAULT_REPORT_PATH) -> Path:
    """Schrijf het kwaliteitsrapport als leesbaar JSON-bestand weg."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return output_path
