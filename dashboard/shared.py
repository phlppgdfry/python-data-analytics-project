"""Gedeelde data-, filter- en opmaaklogica voor alle dashboardpagina's."""

from dataclasses import dataclass
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import filter_sales_data
from src.clean_data import clean_sales_data
from src.load_data import (
    load_customer_directory_csv,
    load_monthly_targets_csv,
    load_sales_csv,
    load_sales_from_postgres,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"
TARGETS_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "monthly_targets.csv"
CUSTOMERS_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "customers.csv"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.json"
POSTGRES_QUERY_PATH = PROJECT_ROOT / "sql" / "dashboard_sales.sql"


@dataclass
class DashboardContext:
    """Alle beschikbare data en de huidige selectie van de gebruiker."""

    data: pd.DataFrame
    filtered_data: pd.DataFrame
    monthly_targets: pd.DataFrame
    customer_directory: pd.DataFrame
    database_url: str | None
    selected_start: object
    selected_end: object
    countries: list[str]
    products: list[str]


def apply_global_style() -> None:
    """Houd de portfolio-app visueel consistent op alle pagina's."""
    st.markdown(
        """
        <style>
            .block-container { max-width: 1240px; padding-top: 2.5rem; }
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 14px;
                padding: 1rem;
            }
            div[data-testid="stMetricLabel"] { color: #475569; }
            .eyebrow {
                color: #2563eb;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_database_url() -> str | None:
    """Lees optionele lokale/cloud databasecredentials zonder ze te tonen."""
    if database_url := os.getenv("DATABASE_URL"):
        return database_url
    try:
        return st.secrets.get("DATABASE_URL")
    except Exception:
        return None


@st.cache_data
def _get_sales_data(source_version: int, database_url: str | None) -> pd.DataFrame:
    """Gebruik PostgreSQL wanneer geconfigureerd, anders de CSV-fallback."""
    del source_version
    if database_url:
        query = POSTGRES_QUERY_PATH.read_text(encoding="utf-8")
        return clean_sales_data(load_sales_from_postgres(database_url, query))
    return clean_sales_data(load_sales_csv(RAW_DATA_PATH))


@st.cache_data
def _get_monthly_targets(source_version: int) -> pd.DataFrame:
    del source_version
    return load_monthly_targets_csv(TARGETS_DATA_PATH)


@st.cache_data
def _get_customer_directory(source_version: int) -> pd.DataFrame:
    del source_version
    return load_customer_directory_csv(CUSTOMERS_DATA_PATH)


def _reset_filters(data: pd.DataFrame) -> None:
    st.session_state["filter_period"] = (data["order_date"].min().date(), data["order_date"].max().date())
    st.session_state["filter_countries"] = sorted(data["country"].unique())
    st.session_state["filter_products"] = sorted(data["product"].unique())


def get_dashboard_context() -> DashboardContext | None:
    """Laad data en laat de gekozen filters op iedere pagina identiek werken."""
    database_url = get_database_url()
    data = _get_sales_data(RAW_DATA_PATH.stat().st_mtime_ns, database_url)
    monthly_targets = _get_monthly_targets(TARGETS_DATA_PATH.stat().st_mtime_ns)
    customer_directory = _get_customer_directory(CUSTOMERS_DATA_PATH.stat().st_mtime_ns)

    with st.sidebar:
        st.header("Analyse filters")
        st.caption("Deze selectie geldt voor de volledige huidige pagina.")
        if st.button("Reset filters", width="stretch"):
            _reset_filters(data)
        selected_dates = st.date_input(
            "Order period",
            value=(data["order_date"].min().date(), data["order_date"].max().date()),
            min_value=data["order_date"].min().date(),
            max_value=data["order_date"].max().date(),
            key="filter_period",
        )
        countries = st.multiselect(
            "Country",
            sorted(data["country"].unique()),
            default=sorted(data["country"].unique()),
            key="filter_countries",
        )
        products = st.multiselect(
            "Product",
            sorted(data["product"].unique()),
            default=sorted(data["product"].unique()),
            key="filter_products",
        )
        st.divider()
        st.caption("Source: PostgreSQL" if database_url else "Source: CSV fallback")

    if len(selected_dates) != 2:
        st.info("Selecteer een begin- en einddatum om de analyse te tonen.")
        return None

    filtered_data = filter_sales_data(data, countries, products, selected_dates[0], selected_dates[1])
    if filtered_data.empty:
        st.warning("Geen gegevens voor deze selectie. Kies minstens één land, product en een periode met orders.")
        return None

    return DashboardContext(
        data=data,
        filtered_data=filtered_data,
        monthly_targets=monthly_targets,
        customer_directory=customer_directory,
        database_url=database_url,
        selected_start=selected_dates[0],
        selected_end=selected_dates[1],
        countries=countries,
        products=products,
    )


def page_intro(section: str, description: str) -> None:
    """Render een consistente, compacte kop voor een dashboardpagina."""
    st.markdown('<p class="eyebrow">Portfolio project · Sales intelligence</p>', unsafe_allow_html=True)
    st.title(section)
    st.caption(description)


def format_delta(change: float | None) -> str:
    """Formatteer een procentuele vergelijking voor een KPI-kaart."""
    return "No prior period" if change is None else f"{change:+.1f}% vs prior period"


def format_compact_currency(amount: float) -> str:
    """Houd grote bedragen volledig leesbaar in compacte dashboard-KPI's."""
    return f"€{amount / 1_000:,.1f}K" if abs(amount) >= 1_000 else f"€{amount:,.2f}"


def load_quality_report() -> dict[str, int | float]:
    """Lees het meest recente pipeline-kwaliteitsrapport voor de quality-pagina."""
    if not QUALITY_REPORT_PATH.exists():
        return {}
    return json.loads(QUALITY_REPORT_PATH.read_text(encoding="utf-8"))
