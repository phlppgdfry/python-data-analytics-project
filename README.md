# Python Data Analytics Project

[![Tests](https://github.com/phlppgdfry/python-data-analytics-project/actions/workflows/tests.yml/badge.svg)](https://github.com/phlppgdfry/python-data-analytics-project/actions/workflows/tests.yml)

**[Open the live dashboard →](https://sales-analytics-phlppgdfry.streamlit.app/)**

![Sales analytics dashboard preview](assets/dashboard-preview.png)

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

1. Leest 24 maanden bewust onzuivere verkoopdata uit `data/raw/sales.csv`.
2. Normaliseert landen, datums, prijzen en producten; verwijdert ongeldige en
   dubbele rijen; berekent omzet.
3. Levert omzet-, brutowinst-, marge- en target-KPI's, plus statistieken.
4. Genereert PNG-rapportgrafieken én interactieve Plotly-HTML.
5. Toont dezelfde inzichten in een filterbaar Streamlit-dashboard.

## Dashboardfeatures

- filters op periode, land en product;
- KPI-kaarten voor omzet, orders, klanten en gemiddelde orderwaarde;
- brutowinst, brutomarge en maandelijkse omzetdoelen;
- automatische vergelijking met de vorige even lange periode;
- gecombineerde interactieve grafiek voor maandelijkse omzet én orders;
- actual-versus-target-grafiek en een topklantenoverzicht;
- interactieve vergelijkingen per land en product;
- belangrijkste land- en productinzicht voor de geselecteerde data;
- download van de gefilterde, opgeschoonde data als CSV.

## Installeren en uitvoeren

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/generate_sample_data.py  # optioneel: reproduceer de brondata
python src/run_pipeline.py
streamlit run dashboard/app.py
```

Na de pipeline staan de schone gegevens in `data/processed/cleaned_sales.csv`
en de grafieken in `reports/charts/`.

## Business insights in deze demo

De reproduceerbare demo bevat **900 geldige orders** over januari 2024 tot en
met december 2025. Ze laat onder andere zien dat:

- omzet groeide van **€54.033,50 in 2024** naar **€76.230,42 in 2025**
  (**+41,1%**);
- België met **€42.634,92** de grootste markt is;
- Shoes met **€46.074,88** de hoogste productomzet heeft.
- de totale brutowinst **€73.943,92** is bij een marge van **56,76%**.

De waarden zijn synthetisch, maar de cleaning-, analyse- en dashboardflow is
dezelfde als voor echte bedrijfsdata.

## Projectstructuur

```text
python-data-analytics-project/
├── data/raw/sales.csv              # brondata, met opzettelijke fouten
├── data/raw/monthly_targets.csv    # maandelijkse omzetdoelen
├── data/processed/                 # output van de cleaning-pipeline
├── src/                            # loading, cleaning, validatie, analyse, statistiek
├── visualizations/                 # Matplotlib en Plotly
├── dashboard/app.py                # interactieve Streamlit-app
├── sql/                            # PostgreSQL-schema en voorbeeldqueries
├── reports/charts/                 # gegenereerde grafieken
├── docs/                            # deployment- en databasehandleiding
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

## PostgreSQL in productie

De portfolio-app kan al queryresultaten uit PostgreSQL in Pandas laden via
`src/load_data.py`. Voor een live cloud-database staat de veilige stappenkaart
in [docs/CLOUD_POSTGRES.md](docs/CLOUD_POSTGRES.md). Databasecredentials horen
uitsluitend in Streamlit secrets, nooit in Git.

## Data quality

Naast de cleaning-pipeline valideert [Pandera](https://pandera.readthedocs.io/)
de finale dataset als data contract: verplichte kolommen, geldige landen en
producten, unieke order-ID's, positieve prijzen/kosten en een geldige marge.
Een foute bronrij komt dus niet stilzwijgend in het dashboard terecht.
