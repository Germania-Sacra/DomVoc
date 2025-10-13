# data/reconciliation
Dieser Ordner wird während der Abarbeitung des Workflows mit verschiedenen Dateien gefüllt. 

## Place Matching
- `places_reconciled.xlsx` enthält eine Liste, die den Orten aus der Tabelle `gs_places` jeweils einer FactGird Q-Nummer zuordnet. Die Tabelle sollte mindestens eine Spalte `place_id` (Die ID des Ortes in der Klosterdatenbank) und eine Spalte `factgrid_id` (die zugehörige FactGrid ID) enthalten.
- `places_without_factgrid.xlsx` diese Tabelle wird im Laufe des Workflows erstellt und enthält Orte, die im aktuell zu verarbeitenden Datensatz enthalten sind, aber noch keine Zuordnung zu einer FactGrid-ID haben.