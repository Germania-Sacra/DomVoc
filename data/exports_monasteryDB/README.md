# data/exports_monasteryDB
Dieser Ordner enthält Export-Dateien aus der Klosterdatenbank im Excel-Format. Die Exporte tragen den Namen der jeweiligen Tabelle. Die für den Prozess benötigten Tabellen sind:

- `gs_external_url_type`: Liste aller externen Identifier in der Datenbank, inklusive Zuordnung zu einer FactGrid-Property, falls vorhanden.
- `gs_external_urls_monastery`: Verlinkung zwischen Klöstern in der Datenbank und externen URLs (zum Beispiel Wikidata, GND, ...)
- `gs_monastery_location`: Verbindung zwischen Klöstern und Standorten. Die Standorte sind die Grundlage für die Erschaffung der Gebäudekomplex-Items.
- `gs_monastery_order`: Verbindung zwischen Klöstern und religiösen Orden.
- `gs_monastery`: Liste aller Klöster in der Datenbank.
- `gs_orders`: Liste aller Orden in der Datenbank, inklusive FactGridID.
- `gs_places`: Liste aller Orte in der Datenbank, inklusive Koordinaten und GeonamesID.

Das folgende Diagramm veranschaulicht die Beziehungen zwischen den Tabellen. Es werden nur die Felder gezeigt, die für die Überführung nach FactGrid relevant sind.
![UML-Diagramm Datenbank Klöster und Stifte](../../documentation-images/KlosterDB%20Datenbank.png)
