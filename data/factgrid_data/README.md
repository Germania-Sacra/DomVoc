# data/factgrid_data
Dieser Ordner sollte einen aktuellen Abzug der Klosterdatenbank-Daten in FactGrid enthalten. Dieser kann mit zwei verschiedenen Abfragen erstellt werden:

## monasteries_in_factgrid.csv
Zugrunde liegende Abfrage:
```sparql
SELECT ?item ?KlosterdatenbankID WHERE{
  ?item wdt:P471 ?KlosterdatenbankID 
}
```
Die Ausgabe der Abfrage wird als CSV-Datei heruntergeladen. Die Abfrage kann bei Bedarf erweitert oder eingeschränkt werden. Die resultierende Datei sollte aber mindestens diese Spalten enthalten:
- `?item` FactGrid-Link zum Item. In der Webanzeige z.B. `wd:Q422286`, in der heruntergeladenen Datei z.B. `https://database.factgrid.de/entity/Q422286`.
- `?KlosterdatenbankID`: Die korrespondierende KlosterdatenbankID, normalerweise verlinkt über [P471](https://database.factgrid.de/wiki/Property:P471).

### Beispiel CSV
```csv
item,KlosterdatenbankID
https://database.factgrid.de/entity/Q422286,114
https://database.factgrid.de/entity/Q470546,119
https://database.factgrid.de/entity/Q633292,120
https://database.factgrid.de/entity/Q633339,131
https://database.factgrid.de/entity/Q633346,139
```

## building_complexes_in_factgrid.csv
Zugrunde liegende Abfrage:
```sparql
SELECT ?item ?GSVocabTerm WHERE{
  ?item wdt:P2 wd:Q635758 .
  ?item wdt:P1301 ?GSVocabTerm
}
```
Die Ausgabe der Abfrage wird als CSV-Datei heruntergeladen. Die Abfrage kann bei Bedarf erweitert oder eingeschränkt werden. Die resultierende Datei sollte aber mindestens diese Spalten enthalten:
- `?item` FactGrid-Link zum Item. In der Webanzeige z.B. `wd:Q1746205`, in der heruntergeladenen Datei z.B. `https://database.factgrid.de/entity/Q1746205`.
- `?GSVocabTerm`: Der Vokabularbegriff der Germania Sacra, zum Beispiel `GSMonasteryLocation3786`, normalerweise verlinkt über [P1301](https://database.factgrid.de/wiki/Property:P1301).
- 
### Beispiel CSV
```csv
item,GSVocabTerm
https://database.factgrid.de/entity/Q1746205,GSMonasteryLocation3786
https://database.factgrid.de/entity/Q1746224,GSMonasteryLocation6151
https://database.factgrid.de/entity/Q1746347,GSMonasteryLocation362
https://database.factgrid.de/entity/Q1746354,GSMonasteryLocation10030
```

## Screenshot: Download aus FactGrid
![Download aus Factgrid](../../documentation-images/FactGrid%20Download.png)