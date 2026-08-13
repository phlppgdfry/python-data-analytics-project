# Cloud PostgreSQL: productiekoppeling

De portfolio-app gebruikt standaard een reproduceerbare CSV, zodat de publieke
demo altijd zonder externe credentials werkt. Wanneer `DATABASE_URL` is
ingesteld, leest het dashboard automatisch PostgreSQL via
`load_sales_from_postgres()` en anders gebruikt het de CSV-fallback.

## Voor je een cloud-database koppelt

1. Kies een PostgreSQL-provider, bijvoorbeeld Neon, Supabase, Render of AWS RDS.
2. Maak een database aan en voer `sql/schema.sql` uit.
3. Laad alleen niet-gevoelige demo- of bedrijfsdata in.
4. Plaats de connectiestring in Streamlit Community Cloud via **App settings →
   Secrets**. Gebruik nooit een wachtwoord in een Git-bestand.

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"
```

## Huidige keuze in de app

```text
DATABASE_URL aanwezig → PostgreSQL → Pandas → dashboard
geen DATABASE_URL     → CSV → Pandas → dashboard
```

Zo blijft de publieke demo betrouwbaar, terwijl een productieversie veilig van
een beheerde database kan lezen. Voor lokaal oefenen zonder cloudprovider staat
de volledige flow in [LOCAL_POSTGRES.md](LOCAL_POSTGRES.md).
