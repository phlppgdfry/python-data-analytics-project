"""Kleine, herbruikbare NumPy-statistiekfuncties."""

import numpy as np
import pandas as pd


def summarize_order_values(order_values: pd.Series) -> dict[str, float]:
    """Geef statistieken voor een reeks orderwaarden terug."""
    values = np.asarray(order_values, dtype=float)
    if values.size == 0:
        raise ValueError("Er zijn geen orderwaarden om samen te vatten.")
    return {
        "mean": round(float(np.mean(values)), 2),
        "median": round(float(np.median(values)), 2),
        "std": round(float(np.std(values)), 2),
        "min": round(float(np.min(values)), 2),
        "max": round(float(np.max(values)), 2),
        "p90": round(float(np.percentile(values, 90)), 2),
    }
