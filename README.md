# Python Data Analytics Project

Een volledige, werkende sales-analyticsportfolio-app. We zullen deze eindversie
later stap voor stap ontleden en opnieuw opbouwen; zo zie je steeds waar een
concept naartoe leidt.

```text
CSV / PostgreSQL
       ↓
Pandas → cleaning → analyses & NumPy-statistiek → KPI's
       ↓                         ↓
 Matplotlib (PNG)           Plotly (interactief) → Streamlit-dashboard
```

## Wat deze projectversie doet

1. Leest bewust onzuivere verkoopdata uit `data/raw/sales.csv`.
2. Normaliseert landen, datums, prijzen en producten; verwijdert ongeldige en
   dubbele rijen; berekent omzet.
3. Levert KPI's, omzet per maand, land en product, plus statistieken.
4. Genereert PNG-rapportgrafieken én interactieve Plotly-HTML.
5. Toont dezelfde inzichten in een filterbaar Streamlit-dashboard.

## Installeren en uitvoeren

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_pipeline.py
streamlit run dashboard/app.py
```

Na de pipeline staan de schone gegevens in `data/processed/cleaned_sales.csv`
en de grafieken in `reports/charts/`.

## Projectstructuur

```text
python-data-analytics-project/
├── data/raw/sales.csv              # brondata, met opzettelijke fouten
├── data/processed/                 # output van de cleaning-pipeline
├── src/                            # loading, cleaning, analyse, statistiek
├── visualizations/                 # Matplotlib en Plotly
├── dashboard/app.py                # interactieve Streamlit-app
├── sql/                            # PostgreSQL-schema en voorbeeldqueries
├── reports/charts/                 # gegenereerde grafieken
└── tests/                          # pytest-controles
```

## Belangrijkste zakelijke vragen

- Wat is de totale omzet, het aantal orders, klanten en de gemiddelde orderwaarde?
- Hoe ontwikkelt omzet zich per maand?
- Welke landen en producten dragen het meeste bij?
- Hoe zijn individuele orderwaarden verdeeld?

## Leerroute

| Fase | Onderwerp | Waar je het terugziet |
| --- | --- | --- |
| 0 | Python-basis en Git | `src/01_python_basics.py` |
| 1 | NumPy/statistiek | `src/statistics.py` |
| 2 | Pandas en CSV | `src/load_data.py` |
| 3 | Data cleaning | `src/clean_data.py` |
| 4 | Analyse en KPI's | `src/analysis.py` |
| 5–6 | Matplotlib en Plotly | `visualizations/` |
| 7 | PostgreSQL en SQL | `sql/`, `src/load_data.py` |
| 8 | Dashboard | `dashboard/app.py` |
