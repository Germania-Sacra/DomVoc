# data/results
in diesem Ordner befinden sich nach Ausführen des Workflows die für den FactGrid-Import vorbereiteten Dateien. Die folgenden Dateien liegen jeweils in drei Versionen vor: Eine CSV-Datei mit der CSV-Repräsentation der Import-Anweisungen ([siehe hier](https://www.wikidata.org/wiki/Help:QuickStatements#CSV_file_syntax)), dieselbe Tabelle als Excel-Format, sowie eine TSV-Datei, die die Anweisungen für den Import im Quickstatements V1-Format enthält ([siehe hier](https://www.wikidata.org/wiki/Help:QuickStatements#Command_sequence_syntax)).

**Übersicht über die Dateien:**
- `building_to_monastery`: Verbindungen zwischen Gebäudekomplexen und Religiösen Gemeinschaften. Kann nur erstellt werden, wenn `import_building_complexes` und `import_monasteries` bereits erstellt und importiert wurden.
- `import_building_complexes`: Anweisungen für neu zu erstellende Gebäudekomplexe.
- `import_monasteries`: Anweisungen für neu zu erstellende religiöse Gemeinschaften.
- `monastery_to_order`: Verbindungen zwischen religiösen Gemeinschaften und religiösen Orden. Zuweisung von der Eigenschaft "ist ein(e)" basierend auf der Ordenszugehörigkeit.