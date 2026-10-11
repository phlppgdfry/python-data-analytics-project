# Sales Analytics: van herkennen naar zelf kunnen

[Leerroute](README.md) · [Codewandeling](codewandeling.md)

Maak de opdrachten eerst op papier. Codewijzigingen horen in een oefenbranch;
databaseoefeningen uitsluitend in de lokale demo-omgeving. De [README](../../README.md)
bevat de setup. Deze gids beweert niet dat jij de oefeningen al hebt uitgevoerd.

## 1. Omzet, winst en totale marge

Order A: 2 stuks à €50, kostprijs €30 per stuk. Order B: 1 stuk à €100,
kostprijs €90. Bereken totale omzet, brutowinst, marge en gemiddelde orderwaarde.

<details><summary>Antwoord</summary>

A: €100 omzet, €40 winst. B: €100 omzet, €10 winst. Totaal: **€200 omzet,
€50 winst, 25% marge en €100 gemiddelde orderwaarde**.
Bereken de marge altijd uit totalen. Hier valt het ongewogen gemiddelde toevallig
gelijk uit door gelijke omzet; bij ongelijke omzet hoeft dat niet zo te zijn.

</details>

## 2. Een gewogen ratio

A heeft €100 omzet en €50 winst; B heeft €900 omzet en €90 winst. Een collega
zegt dat de marge 30% is. Leg de fout uit en wijs de juiste functie aan.

<details><summary>Antwoord</summary>

Totale marge = 140/1000 = **14%**. 30% is het ongewogen gemiddelde van 50% en 10%.
`calculate_profit_kpis()` berekent de verhouding van totalen. Een grote order
moet naar zijn omzet meewegen.

</details>

## 3. Welke rijen verdwijnen?

Twee geldige rijen hebben dezelfde order-ID maar verschillende producten.
Daarnaast is er een order uit land `Atlantis` en een order met kostprijs hoger
dan verkoopprijs. Wat doet de huidige cleaning? Is dat altijd zakelijk juist?

<details><summary>Antwoord</summary>

Van de dubbele order-ID blijft alleen de eerste invoerrij over. Atlantis wordt
niet herkend en verdwijnt na de ontbrekende-waardencontrole. De verlieslatende
order wordt weggefilterd. Voor de synthetische aannames is dit verklaarbaar;
voor echte orderregels of verkoop met verlies kan het onjuist zijn. Grain en
toegestane zakelijke uitzonderingen moeten eerst vaststaan.

</details>

## 4. SQL narekenen

Schrijf een query die per land omzet en marge toont op `sales_orders`.
Waarom mag je hier niet simpelweg `AVG(margin_percent)` gebruiken?

<details><summary>Mogelijke read-only query</summary>

```sql
SELECT country,
       SUM(revenue) AS revenue,
       SUM(gross_profit) AS gross_profit,
       100.0 * SUM(gross_profit) / NULLIF(SUM(revenue), 0) AS margin_percent
FROM sales_orders
GROUP BY country
ORDER BY revenue DESC;
```

De ratio moet omzetgewogen zijn. `NULLIF` laat bij nul totale omzet een onbekende
ratio ontstaan in plaats van te delen door nul. Bepaal vervolgens hoe het
dashboard die onbekende waarde begrijpelijk toont.

</details>

## 5. Het contract is groen, de omzet klopt niet

Je geeft een volledig geldig gevormde rij rechtstreeks aan de validator.
Aantallen en prijzen zijn geldig, maar `revenue` is positief en expres €10 te
hoog. Waarom hoeft het contract dit niet tegen te houden?

<details><summary>Antwoord en leeropdracht</summary>

Het contract controleert niet expliciet de gelijkheid tussen omzet en aantal ×
prijs. Het verwacht binnen de normale route dat cleaning die berekening verzorgt.
Ontwerp een extra controle met afgesproken afronding. Test zowel een goede rij
als een positieve maar fout berekende rij. Blind alle positieve bedragen toelaten
is een zwakker contract dan zakelijke consistentie controleren.

</details>

## 6. Kleine aanpassing

Een gebruiker wil een KPI “omzet per unieke klant”. Reken eerst orders van €100
en €50 voor C001 plus €150 voor C002 na. Zoek vervolgens welke bestaande functie
je kunt uitbreiden en wat een test moet controleren.

<details><summary>Verwachting en aanpak</summary>

€300 / 2 unieke klanten = **€150**. Deel niet door drie orders. Een test moet
herhaalde klanten bevatten; drie unieke klanten zou deze fout niet zichtbaar maken.
Bespreek ook lege data en welke filters de KPI moet volgen. Bouw de uitbreiding
alleen in je oefenbranch en noteer voor/na-resultaten.

</details>

## 7. Waarom verandert het dashboard niet?

De database is bijgewerkt, de lokale CSV niet. Het scherm toont oude omzet.
Welke code bekijk je en welke andere bron gebruikt het kwaliteitsrapport?

<details><summary>Antwoord</summary>

Bekijk de cache en bronkeuze in `dashboard/shared.py`. Een databasewijziging
wijzigt niet automatisch het meegegeven CSV-bestandstijdstip. Het kwaliteitsrapport
komt uit `reports/data_quality_report.json`; controleer wanneer de pipeline dat
bestand schreef en op welke bron het gebaseerd is.

</details>

## 8. Beoordeel een voorspelling

Een model voorspelt 100, 120, 130; werkelijkheid is 110, 100, 150. Bereken MAE.
Zegt een lage fout op deze synthetische data dat het model commercieel inzetbaar is?

<details><summary>Antwoord</summary>

Absolute fouten: 10, 20 en 20. MAE = 50/3 ≈ **16,67** in dezelfde eenheid als
de omzet. Het zegt alleen iets over deze evaluatie. Onderzoek echte bronkwaliteit,
representativiteit, meerdere tijdvensters en vergelijking met een simpele baseline.

</details>

## 9. Leg een keuze aan de business voor

De business wil retouren meetellen. Schrijf drie verduidelijkingsvragen en één
klein acceptatievoorbeeld voordat je code verandert.

<details><summary>Voorbeeld</summary>

Vragen: boeken we de retour op verkoopdatum of retourdatum? Is omzet inclusief
btw/korting? Hoe behandelen we gedeeltelijke retouren en kosten?
Voorbeeld: verkoop €100 en een retour van €40 binnen dezelfde afgesproken periode
geven €60 netto-omzet. Dat vereist andere regels dan uitsluitend positieve sales.

</details>

## Eindproef

Leg één order, één filter en één KPI uit met code. Toon een handberekening, een
fout die je onderzocht hebt en een beperking van het huidige model. Vul daarna
je eigen niveau in het [leerlogboek](leerlogboek.md) in.
