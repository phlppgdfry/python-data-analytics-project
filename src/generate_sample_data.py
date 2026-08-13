"""Genereer reproduceerbare, realistische voorbeeldverkopen voor het portfolio."""

import calendar
import csv
from datetime import date
from pathlib import Path
import random


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"
RANDOM_SEED = 42

PRODUCTS = {
    "Shoes": {"price": 89.99, "unit_cost": 39.5},
    "Shirt": {"price": 49.99, "unit_cost": 17.5},
    "Jacket": {"price": 129.99, "unit_cost": 62.0},
    "Accessories": {"price": 29.99, "unit_cost": 8.5},
    "Sneakers": {"price": 109.99, "unit_cost": 51.0},
}
COUNTRIES = ["Belgium", "France", "Netherlands", "Germany", "United Kingdom"]
COUNTRY_VARIANTS = {
    "Belgium": ["Belgium", "belgium", "BELGIUM "],
    "France": ["France", "france"],
    "Netherlands": ["Netherlands", "netherlands"],
    "Germany": ["Germany", "germany"],
    "United Kingdom": ["United Kingdom", "UK", "united kingdom"],
}


def _month_start(year: int, month: int) -> date:
    return date(year, month, 1)


TARGETS_OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "monthly_targets.csv"
CUSTOMERS_OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "customers.csv"


def _format_money(amount: float, order_number: int) -> str:
    """Geef de cleaning-pipeline enkele realistische prijsformaten."""
    if order_number % 13 == 0:
        return f"€{amount:.2f}"
    if order_number % 17 == 0:
        return f"{amount:.2f}".replace(".", ",")
    return f"{amount:.2f}"


def generate_sales_data(output_path: Path = OUTPUT_PATH) -> int:
    """Schrijf 24 maanden verkoopdata met enkele doelbewuste datakwaliteitsfouten."""
    random.seed(RANDOM_SEED)
    rows: list[dict[str, str | int]] = []
    monthly_revenue: dict[str, float] = {}
    order_id = 10_000

    for month_index in range(24):
        year = 2024 + month_index // 12
        month = month_index % 12 + 1
        days_in_month = calendar.monthrange(year, month)[1]
        orders_this_month = 26 + month_index

        for _ in range(orders_this_month):
            product = random.choices(list(PRODUCTS), weights=[30, 22, 16, 14, 18])[0]
            country = random.choices(COUNTRIES, weights=[31, 22, 18, 17, 12])[0]
            quantity = random.choices([1, 2, 3, 4], weights=[48, 31, 15, 6])[0]
            order_date = date(year, month, random.randint(1, days_in_month))
            price = PRODUCTS[product]["price"]
            unit_cost = PRODUCTS[product]["unit_cost"]

            rows.append(
                {
                    "order_id": order_id,
                    "order_date": order_date.isoformat(),
                    "customer_id": f"C{random.randint(1, 280):03d}",
                    "country": random.choice(COUNTRY_VARIANTS[country]),
                    "product": product.lower() if order_id % 11 == 0 else product,
                    "quantity": quantity,
                    "price": _format_money(price, order_id),
                    "unit_cost": _format_money(unit_cost, order_id + 3),
                }
            )
            month_key = _month_start(year, month).isoformat()
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + price * quantity
            order_id += 1

    # Fouten die de cleaning-pipeline moet onderscheppen.
    rows.extend(
        [
            rows[30].copy(),  # dubbele order
            {"order_id": order_id, "order_date": "2025-12-03", "customer_id": "C999", "country": "Belgium", "product": "Jacket", "quantity": 1, "price": "", "unit_cost": "62.00"},
            {"order_id": order_id + 1, "order_date": "2025-12-07", "customer_id": "C998", "country": "Unknown", "product": "Shoes", "quantity": 1, "price": "89.99", "unit_cost": "39.50"},
            {"order_id": order_id + 2, "order_date": "2025-12-12", "customer_id": "C997", "country": "France", "product": "Shoes", "quantity": 999, "price": "89.99", "unit_cost": "39.50"},
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["order_id", "order_date", "customer_id", "country", "product", "quantity", "price", "unit_cost"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    with TARGETS_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["month", "target_revenue"], lineterminator="\n")
        writer.writeheader()
        for month_index, (month, revenue) in enumerate(sorted(monthly_revenue.items())):
            target_factor = 0.94 + (month_index % 5) * 0.025
            writer.writerow({"month": month, "target_revenue": round(revenue * target_factor, 2)})

    customer_first_purchase: dict[str, str] = {}
    for row in rows:
        customer_id = str(row["customer_id"])
        order_date = str(row["order_date"])
        if customer_id not in customer_first_purchase or order_date < customer_first_purchase[customer_id]:
            customer_first_purchase[customer_id] = order_date
    profile_random = random.Random(RANDOM_SEED + 1)
    with CUSTOMERS_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["customer_id", "customer_name", "customer_since", "acquisition_channel"], lineterminator="\n")
        writer.writeheader()
        for customer_id, first_purchase in sorted(customer_first_purchase.items()):
            writer.writerow(
                {
                    "customer_id": customer_id,
                    "customer_name": f"Customer {customer_id[1:]}",
                    "customer_since": first_purchase,
                    "acquisition_channel": profile_random.choice(["Organic", "Paid search", "Email", "Referral"]),
                }
            )
    return len(rows)


if __name__ == "__main__":
    count = generate_sales_data()
    print(f"Generated {count} raw sales rows in {OUTPUT_PATH}")
