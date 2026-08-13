import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from src.load_to_postgres import load_data_to_postgres


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.mark.integration
@pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL is required for the PostgreSQL integration test.")
def test_postgres_import_loads_all_analytics_tables():
    engine = create_engine(DATABASE_URL)
    schema_statements = (PROJECT_ROOT / "sql" / "schema.sql").read_text(encoding="utf-8").split(";")
    with engine.begin() as connection:
        for statement in schema_statements:
            if statement.strip():
                connection.execute(text(statement))

    results = load_data_to_postgres(DATABASE_URL)
    assert results["sales_orders"] > 1_000
    assert results["monthly_targets"] == 36
    assert results["customers"] > 400

    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM sales_orders")).scalar_one() == results["sales_orders"]
