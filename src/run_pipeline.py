"""Voer de volledige CSV-naar-inzichten-pipeline uit."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "visualizations"))

from analysis import calculate_kpis, calculate_order_statistics, revenue_by_country, revenue_by_month, revenue_by_product  # noqa: E402
from clean_data import clean_sales_data, save_cleaned_sales_data  # noqa: E402
from load_data import load_sales_csv  # noqa: E402
from matplotlib_charts import create_static_charts  # noqa: E402
from plotly_charts import create_interactive_charts  # noqa: E402


CHARTS_DIR = PROJECT_ROOT / "reports" / "charts"


def main() -> None:
    raw_data = load_sales_csv()
    clean_data = clean_sales_data(raw_data)
    processed_path = save_cleaned_sales_data(clean_data)
    monthly_data = revenue_by_month(clean_data)
    country_data = revenue_by_country(clean_data)
    product_data = revenue_by_product(clean_data)

    create_static_charts(monthly_data, country_data, product_data, CHARTS_DIR)
    create_interactive_charts(monthly_data, country_data, product_data, CHARTS_DIR)

    print(f"Cleaned data saved to: {processed_path}")
    print("KPI's:")
    for name, value in calculate_kpis(clean_data).items():
        print(f"  {name}: {value}")
    print("Order statistics:")
    for name, value in calculate_order_statistics(clean_data).items():
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
