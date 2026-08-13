# Local PostgreSQL workflow

This project uses Docker Compose to run PostgreSQL on your own computer. It is a safe way to practise a real database flow without paying for a cloud provider or exposing credentials.

```text
sales.csv → Pandas cleaning + Pandera validation → PostgreSQL → Pandas → dashboard
```

## Start and load data

From the project root:

```bash
docker compose up -d
python src/run_pipeline.py --load-postgres
```

The first command starts a PostgreSQL container on port `5433`; the second one cleans the CSV, writes the data-quality report and replaces the three analytics tables in PostgreSQL.

## Run the dashboard against PostgreSQL

```bash
DATABASE_URL="postgresql+psycopg://analytics_user:analytics_dev_password@localhost:5433/analytics" \
streamlit run dashboard/app.py
```

The sidebar will show **Source: PostgreSQL**. Without `DATABASE_URL`, the app automatically reads its committed CSV fallback instead.

## Refresh after changing source data

```bash
python src/run_pipeline.py --regenerate --load-postgres
```

This performs the complete local refresh in one command: regenerate source data, clean it, validate it, update reports and load PostgreSQL.

## Stop or reset

```bash
docker compose down
```

Stopping the container does not remove its stored data. To deliberately remove the local database volume as well, use `docker compose down -v`; this deletes only this project's local PostgreSQL data.
