# DomVoc

*English translation to follow. This repository is currently under development and likely to change multiple times. A final version is to be expected by November 2025. Before that date, we recommend to contact us before using methods from this repository.*

Das im Rahmen der NFDI4Memory Incubator Funds geförderte Projekt "DomVoc"  verfolgt das Ziel, intern genutzte Vokabulare aus den Projekten der Germania Sacra teilautomatisiert in ontologiebasierte, persistent addressierbare und frei zugängliche Vokabulare zu überführen. Im Zuge des Projekts wurden die Daten aus der Datenbank ["Klöster und Stifte des alten Reiches"](https://klosterdatenbank.adw-goe.de/liste) nach FactGrid überführt. Dieses Repository enthält die dafür verwendeten Jupyter Notebooks und erläutert den Prozess der Datentransformation.

Die Übertragung aus der relationalen Datenbank nach FactGrid erfolgt in 4 Schritten in vier verschiedenen Notebooks, die nacheinander ausgeführt werden müssen. Ausgangspunkt sind Exporte aus der Klosterdatenbank. Am Ende jedes Notebook entsteht eine TSV-Datei, die Anweisungen im Quick-Statements Format enthält. Diese können genutzt werden, um die Daten in eine Wikibase, in unserem Fall FactGrid zu importieren.

## Über das verwendete Datenmodell
*work in progress*

## Notebooks in diesem Repository
1. **Erstellen von Items zu Gebäudekomplexen.** Basierend auf der Tabelle `gs_monastery_location` wird für jeden Standpunkt eines Klosters, Stifts, oder religiöser Gemeinschaft ein Item vom Typ Gebäudekomplex erstellt.
   1. a. **Übersetzen von Klosternamen und Beschreibungen**. FactGrid ist ein multilinguales System. Die Klosterdatenbank wurde bislang deutschsprachig gepflegt. Um auch Englische Item-Labels und Beschreibungen bereit zu stellen, übersetzt das Notebook 1a die Namen der religiösen Gemeinschaften und Gebäudekomplexe ins Englische. Hierfür wird über die KISSKI API der GWDG ein Large Language Model verwendet.
2. **Erstellen von Items für Religiöse Gemeinschaften.** Basierend auf der Tabelle `gs_monastery` wird für jedes Kloster, Stift, oder religiöse Gemeinschaft ein Item erstellt und zur Klosterdatenbank verlinkt. Dabei wird für jedes Kloster abgeglichen, ob es in FactGrid bereits ein entsprechendes Item gibt, um Dubletten zu vermeiden.
3. **Verknüpfen von Gebäudekomplexen und Religiösen Gemeinschaften.** Nach dem Ausführen von Notebook zwei können die Quick-Statements-Anweisungen in FactGrid importiert werden. Anschließend werden die Daten in FactGrid abgefragt, um die Identifikatoren der neu erstellten Items zu erhalten. Nun werden Gebäudekomplexe und Religiöse Gemeinschaften über die Eigenschaften `Nutzer` und `Liegenschaft` miteinander verbunden.
4. **Verknüpfen von Informationen zu religiösen Orden.** Zuletzt werden die Informationen zur Zugehörigkeit zu religiösen Orden mit den religiösen Gemeinschaften verlinkt. Dabei wird jeder Datensatz auch einer Unterklasse von `Religiöse Gemeinschaft` zugeordnet.

### Workflow für das Hochladen neuer Items in FactGrid
1. Vorhandene Daten in FactGrid abfragen (Siehe Abschnitt SPARQL-Abfragen für vorhandene Daten in FactGrid)
2. Notebook 1 bis inklusive Schritt 1.2.3.1 ausführen.
3. Notebook 1a ausführen.
4. Notebook 1 ab Schritt 1.2.3.2 ausführen. Wenn nötig, bei Punkt 1.4.2 zusätzliche Orte in FactGrid einpflegen.
5. Notebook 2 ausführen.
6. Die Ergebnisse von Notebook 1 und 2 in FactGrid importieren.
7. Erneut vorhandene Daten in FactGrid abfragen.
8. Notebook 3 ausführen.
9. Notebook 4 ausführen.
10. Die Ergebnisse von Notebook 3 und 4 in FactGrid importieren.

## SPARQL-Abfragen für vorhandene Daten in FactGrid
### Alle Items mit Klosterdatenbank-ID in FactGrid
```sparql
SELECT ?item ?KlosterdatenbankID WHERE{
  ?item wdt:P471 ?KlosterdatenbankID 
}
```
### Alle Gebäudekomplexe der Germania Sacra in FactGrid
```sparql
SELECT ?item ?GSVocabTerm WHERE{
  ?item wdt:P2 wd:Q635758 .
  ?item wdt:P1301 ?GSVocabTerm
}
```

## Datei-Struktur des Repositories
Um die Notebooks reibungslos nutzen zu können, muss folgende Dateistruktur eingehalten werden:
```txt
data/
    exports_monasteryDB/
        gs_external_url_type_with_factgrid.xlsx
        gs_external_urls_monastery.xlsx
        gs_monastery_location.xlsx
        gs_monastery_order.xlsx
        gs_monastery.xlsx
        gs_orders.xlsx
        gs_places.xlsx
    factgrid_data/
        monasteries_in_factgrid.csv
        building_complexes_in_factgrid.csv
    reconciliation/
        < Wird im Laufe des Workflows gefüllt >
    results/
        < Wird im Laufe des Workflows gefüllt >
    translation/
        < Wird im Laufe des Workflows gefüllt >
```
Informationen zu den einzelnen Dateien finden sich in den Readme-Dateien der Unterordner.

## Kontakt
Niedersächsische Akademie der Wissenschaften zu Göttingen<br>
Projekt DomVoc<br>
Geiststraße 10<br>
37073 Göttingen

### Email
Johanna Störiko: johanna.stoeriko@adwgoe.de (Bis zum 07.11.2025)<br>
Bärbel Kroeger: baerbel.kroeger@adwgoe.de<br>
Christian Popp: christian.popp@adwgoe.de

