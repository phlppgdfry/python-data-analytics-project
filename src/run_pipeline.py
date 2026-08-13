"""Voer de volledige CSV-naar-inzichten-pipeline uit."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import calculate_kpis, calculate_order_statistics, calculate_profit_kpis, monthly_performance, revenue_by_country, revenue_by_month, revenue_by_product, revenue_vs_target  # noqa: E402
from src.clean_data import clean_sales_data, save_cleaned_sales_data  # noqa: E402
from src.data_quality import build_data_quality_report, save_data_quality_report  # noqa: E402
from src.load_data import load_monthly_targets_csv, load_sales_csv  # noqa: E402
from visualizations.matplotlib_charts import create_static_charts  # noqa: E402
from visualizations.plotly_charts import create_interactive_charts  # noqa: E402


CHARTS_DIR = PROJECT_ROOT / "reports" / "charts"


def main() -> None:
    raw_data = load_sales_csv()
    clean_data = clean_sales_data(raw_data)
    processed_path = save_cleaned_sales_data(clean_data)
    quality_report_path = save_data_quality_report(build_data_quality_report(raw_data, clean_data))
    monthly_data = revenue_by_month(clean_data)
    performance_data = monthly_performance(clean_data)
    country_data = revenue_by_country(clean_data)
    product_data = revenue_by_product(clean_data)
    target_data = revenue_vs_target(clean_data, load_monthly_targets_csv())

    create_static_charts(monthly_data, country_data, product_data, CHARTS_DIR)
    create_interactive_charts(monthly_data, country_data, product_data, CHARTS_DIR, performance_data)

    print(f"Cleaned data saved to: {processed_path}")
    print(f"Data quality report saved to: {quality_report_path}")
    print("KPI's:")
    for name, value in calculate_kpis(clean_data).items():
        print(f"  {name}: {value}")
    print("Order statistics:")
    for name, value in calculate_order_statistics(clean_data).items():
        print(f"  {name}: {value}")
    print("Profit KPI's:")
    for name, value in calculate_profit_kpis(clean_data).items():
        print(f"  {name}: {value}")
    print(f"Target attainment: {target_data['target_attainment_percent'].mean():.1f}%")


if __name__ == "__main__":
    main()
