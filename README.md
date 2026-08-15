# Sales Analytics Project

[![Tests](https://github.com/phlppgdfry/python-data-analytics-project/actions/workflows/tests.yml/badge.svg)](https://github.com/phlppgdfry/python-data-analytics-project/actions/workflows/tests.yml)
[![Live dashboard](https://img.shields.io/badge/live%20dashboard-Streamlit-ff4b4b)](https://sales-analytics-phlppgdfry.streamlit.app/)
[![Status](https://img.shields.io/badge/status-portfolio%20complete-16a34a)](https://sales-analytics-phlppgdfry.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-data%20analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-local%20data%20layer-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**[Open the live dashboard →](https://sales-analytics-phlppgdfry.streamlit.app/)**

![Sales analytics dashboard preview](assets/dashboard-preview.png)

An end-to-end Python sales-analytics portfolio project. It turns deliberately imperfect sales data into validated business insights, an interactive dashboard and a reproducible local PostgreSQL workflow.

> The data is synthetic. The engineering and analytics workflow mirrors how a small business-intelligence product can be structured in practice.

## What it demonstrates

```text
Raw CSV / PostgreSQL
          ↓
Pandas cleaning + Pandera data contract
          ↓
Revenue, profit, ML customer segmentation and evaluated forecasting
          ↓
Parquet + DuckDB analytical SQL → Plotly + Streamlit dashboard / Matplotlib reports
```

| Area | Implementation |
| --- | --- |
| Data preparation | Pandas normalisation, duplicate removal, type conversion and derived revenue/profit fields |
| Data quality | Pandera contract plus a machine-readable quality report |
| Business intelligence | Revenue, orders, gross profit, gross margin, targets and period comparisons |
| Customer analytics | Top customers, new vs returning customers, RFM segments and cohort retention |
| Advanced analytics | Holt trend forecast, Random Forest comparison, holdout evaluation, z-score anomaly detection and business alerts |
| Customer segmentation | RFM features, StandardScaler and reproducible K-Means clusters with actionable profiles |
| Analytical storage | Parquet export plus DuckDB SQL directly on columnar files |
| Data engineering | CSV-to-PostgreSQL import with Docker Compose; CSV fallback for the public app |
| Product delivery | Streamlit dashboard, downloadable analysis extracts, automated tests and GitHub Actions |

## Dashboard

The dashboard is split into focused pages rather than one long report:

- **Executive overview** — KPI cards, period comparison, monthly performance and data export.
- **Sales & profitability** — actual versus target and gross-profit contribution by market and product.
- **Customer intelligence** — returning customers, RFM segments, top customers and cohorts.
- **ML customer segments** — K-Means groups based on recency, frequency and revenue; profile summaries make each group actionable.
- **Forecast & alerts** — three-month revenue forecast, Holt-versus-Random-Forest holdout evaluation, anomaly detection and target-risk alerts.
- **Data quality** — the data contract, retained-row rate and the latest quality report.

All pages share the same date, country and product filters. The forecast deliberately uses the complete history so it remains statistically meaningful when exploration filters are narrow.
Large monetary KPI cards use compact accounting notation (for example, `€263.9K`) to remain readable at every screen width; hovering the KPI reveals the exact value.

## Demo insights

The current reproducible source contains **1,717 valid orders** from January 2024 to December 2026, after four deliberately bad rows are removed.

- Revenue rises from **€65,992.42 in 2024** to **€109,257.49 in 2026**.
- **Belgium** is the largest market at **€69,372.00** in revenue.
- **Shoes** is the highest-revenue product at **€75,861.57**.
- Total gross profit is **€148,243.35** at a **56.17%** gross margin.
- The source intentionally includes country casing, currency formatting, a duplicate and invalid values; the pipeline retains **99.77%** of source rows after cleaning.

## Run locally

```bash
git clone https://github.com/phlppgdfry/python-data-analytics-project.git
cd python-data-analytics-project

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Refresh cleaned data, quality report and chart outputs.
python src/run_pipeline.py

streamlit run dashboard/app.py
```

The pipeline produces both `data/processed/cleaned_sales.csv` and
`data/processed/cleaned_sales.parquet`. The latter is a compact columnar format
for analytics; `src/analytics_store.py` demonstrates DuckDB SQL directly on it,
without first loading data into a database server.

## Why the ML additions matter

This project uses machine learning only where it answers a decision question:

- **Who should receive which retention or upsell action?** K-Means uses the three RFM dimensions—days since last order, order count and revenue—to find behavioral groups. `StandardScaler` makes the units comparable before distance-based clustering. Cluster numbers are arbitrary, so the app ranks the profiles and gives them readable names.
- **Which forecasting approach is credible?** The final six known months are excluded from training and used as a holdout set. The dashboard reports MAE (average error in euros) and RMSE (which penalises large misses more). This compares Holt's trend model with a Random Forest honestly instead of reporting an in-sample score.
- **When should analytics use a file rather than a database?** The cleaned Parquet file is fast, typed and compact. DuckDB can query it with SQL locally, which is a useful middle ground between CSV and a managed warehouse.

## Business decisions enabled

| Question | Evidence in the app | Example action |
| --- | --- | --- |
| Which customers deserve retention attention? | ML segment profile with recency, frequency and revenue | Re-engage inactive high-value customers with a targeted offer. |
| Is a forecast useful enough to plan from? | Six-month Holt vs Random Forest backtest with MAE/RMSE | Prefer the model with the lower out-of-sample error for monthly planning. |
| Where is revenue concentrated? | Country/product dashboards and DuckDB revenue query | Prioritise inventory or campaigns in the strongest markets. |

The existing dashboard preview above shows the product interface; after running it locally, use the **ML customer segments** and **Forecast & alerts** pages as the strongest demo screens for a portfolio walkthrough.

For a fresh deterministic source dataset plus the complete refresh:

```bash
python src/run_pipeline.py --regenerate
```

## Local PostgreSQL with Docker

The public Streamlit deployment intentionally uses the committed CSV fallback: it is free, reliable and contains no database credentials. The project can also run against a real local PostgreSQL database to demonstrate a production-style workflow.

```bash
docker compose up -d
python src/run_pipeline.py --load-postgres

DATABASE_URL="postgresql+psycopg://analytics_user:analytics_dev_password@localhost:5433/analytics" \
streamlit run dashboard/app.py
```

The dashboard then reports **Source: PostgreSQL**. Stop the local database when you no longer need it:

```bash
docker compose down
```

See [the local PostgreSQL guide](docs/LOCAL_POSTGRES.md) for the flow and [the cloud database guide](docs/CLOUD_POSTGRES.md) for an optional future deployment.

## Data quality and testing

`src/validation.py` defines the Pandera data contract. A row must have a unique order ID, recognised country/product, valid customer ID, positive quantities and prices, a cost lower than price, and correctly derived revenue/profit fields.

```bash
python -m pytest -q
```

The test suite covers cleaning, business calculations, generation, forecasts, alerts, dashboard rendering and—when `DATABASE_URL` is present—the PostgreSQL import. GitHub Actions runs the tests on each push and pull request, starts a temporary PostgreSQL service and uploads the refreshed quality report as an artifact.

## Project structure

```text
python-data-analytics-project/
├── dashboard/                 # Streamlit entry point, shared UX and five focused pages
├── data/raw/                  # reproducible synthetic source data and targets
├── data/processed/            # cleaned sales output
├── src/                       # generation, loading, cleaning, validation and analytics
├── visualizations/            # Plotly dashboard figures and Matplotlib report charts
├── sql/                       # PostgreSQL schema and dashboard query
├── reports/                   # data-quality report and generated charts
├── tests/                     # unit, dashboard and PostgreSQL integration tests
├── docker-compose.yml         # local PostgreSQL service
└── .github/workflows/         # continuous integration
```

## Technology stack

`Python` · `Pandas` · `NumPy` · `scikit-learn` · `Pandera` · `Plotly` · `Matplotlib` · `Streamlit` · `statsmodels` · `DuckDB` · `Parquet` · `PyArrow` · `PostgreSQL` · `SQLAlchemy` · `psycopg` · `Docker Compose` · `pytest` · `GitHub Actions`

## Learning map

| Topic | Main files |
| --- | --- |
| Python functions and Git | `src/01_python_basics.py` |
| Pandas loading and cleaning | `src/load_data.py`, `src/clean_data.py` |
| Data contracts | `src/validation.py` |
| KPIs and customer analysis | `src/analysis.py` |
| Forecasts and alerts | `src/forecasting.py` |
| ML customer segmentation | `src/segmentation.py` |
| Parquet and DuckDB analytics | `src/analytics_store.py` |
| SQL and PostgreSQL | `sql/`, `src/load_to_postgres.py` |
| Dashboard product work | `dashboard/` |

## Optional cloud database

A managed cloud PostgreSQL database is **not required** for this portfolio. Add one only when data must change online or multiple users/services need the same live source. Credentials must live in Streamlit Secrets or environment variables—never in this repository. The app already switches to PostgreSQL automatically when a `DATABASE_URL` is configured.
