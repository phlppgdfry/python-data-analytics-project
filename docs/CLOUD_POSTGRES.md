# Cloud PostgreSQL: productiekoppeling

De portfolio-app gebruikt nu een reproduceerbare CSV, zodat de publieke demo
altijd zonder externe credentials werkt. De code in `src/load_data.py` bevat al
`load_sales_from_postgres()`: die leest een SQL-resultaat rechtstreeks in een
Pandas DataFrame.

## Voor je een cloud-database koppelt

1. Kies een PostgreSQL-provider, bijvoorbeeld Neon, Supabase, Render of AWS RDS.
2. Maak een database aan en voer `sql/schema.sql` uit.
3. Laad alleen niet-gevoelige demo- of bedrijfsdata in.
4. Plaats de connectiestring in Streamlit Community Cloud via **App settings →
   Secrets**. Gebruik nooit een wachtwoord in een Git-bestand.

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"
```

## Veilige volgende implementatiestap

Wanneer de database bestaat, voegen we in `dashboard/app.py` een keuze toe:

```text
DATABASE_URL aanwezig → PostgreSQL → Pandas → dashboard
geen DATABASE_URL     → CSV → Pandas → dashboard
```

Zo blijft de publieke demo betrouwbaar, terwijl de productieversie veilig van
een beheerde database kan lezen.
