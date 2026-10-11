# Leer je Sales Analytics-project begrijpen

**Doel:** van een verkoopregel kunnen uitleggen hoe omzet, winst en een dashboard
ontstaan. Daarna leer je aannames controleren, een fout vinden en een kleine
bedrijfsregel aanpassen. Afgestemd op de code op 11 oktober 2026.

## Je route

1. [Volg een order van CSV tot dashboard](codewandeling.md).
2. [Leer begrippen: Python, SQL, modellen, KPI's en kwaliteit](begrippen.md).
3. [Maak de oefeningen en controleer je antwoord](oefeningen.md).
4. [Gebruik de herhaalkaarten en de leerwijze met AI](onthouden.md).
5. [Vul je eigen bewijs en vooruitgang in](leerlogboek.md).

## Wat dit project wel en niet laat zien

De repo bevat concrete verwerking van synthetische verkoopdata, KPI-functies,
kwaliteitscontroles, een dashboard, modelvergelijking, SQL, tests en workflowcode.
De lokale database is optioneel. Het dashboard kiest bij configuratie PostgreSQL;
anders leest en reinigt het de ruwe CSV opnieuw. Het leest niet standaard het
door de pipeline geproduceerde Parquet-bestand.

Dit is geen gerealiseerde Power BI/Fabric-implementatie en geen bewijs van ervaring
met echte bedrijfsdata. De leergids verklaart bestaande code; hij heeft de live
dashboardstatus en cloudinstellingen niet geverifieerd.

## Vaardighedenkaart

| Vaardigheid | Waar kijken | Zelf aantonen |
|---|---|---|
| Python en cleaning | [clean_data.py](../../src/clean_data.py) | Voorspel welke rijen blijven |
| Datacontract | [validation.py](../../src/validation.py) | Onderscheid vormcontrole en juiste berekening |
| Zakelijke KPI's | [analysis.py](../../src/analysis.py) | Reken omzet, gemiddelde order en marge na |
| SQL | [sql/queries.sql](../../sql/queries.sql) en [schema](../../sql/schema.sql) | Verklaar sleutels, groepering en joins |
| ETL | [run_pipeline.py](../../src/run_pipeline.py) | Leg invoer en geproduceerde bestanden uit |
| Database-load | [load_to_postgres.py](../../src/load_to_postgres.py) | Leg volledige vervanging en transactie uit |
| Dashboards | [shared.py](../../dashboard/shared.py) | Traceer bronkeuze en filters |
| Voorspellen/statistiek | [forecasting.py](../../src/forecasting.py) | Leg holdout, MAE en beperkingen uit |
| Segmentatie | [segmentation.py](../../src/segmentation.py) | Verklaar schalen en betekenis van clusters |
| Analytische opslag | [analytics_store.py](../../src/analytics_store.py) | Onderscheid CSV, Parquet en querylaag |
| Testen en CI | [tests](../../tests) en [workflow](../../.github/workflows/tests.yml) | Controleer een nieuwe KPI met klein voorbeeld |
| Governance/stakeholders | KPI-afspraak in [leerlogboek](leerlogboek.md) | Bespreek retouren, btw en definities |
| Power BI/Fabric | Niet gebouwd in deze repo | Oefen afzonderlijk; een Python-dashboard is geen Power BI-ervaring |

## Andere projecten

- [Mobility ETL](https://github.com/phlppgdfry/belgium-mobility-weather-etl/tree/main/docs/leren)
- [Sensorplatform](https://github.com/phlppgdfry/environmental-sensor-data-platform/tree/main/docs/leren)
- [Fabric Lottery](https://github.com/phlppgdfry/fabric-lottery-data-platform/tree/main/docs/leren)

[Terug naar de project-README](../../README.md)
