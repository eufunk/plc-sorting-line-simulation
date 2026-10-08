# src – Quellen für TIA Portal

Exportierte Textquellen des SPS-Programms. Das TIA-Portal-Projekt selbst liegt außerhalb des Repositorys (z. B. `C:\TIA\SortingLine\`).

| Ordner       | Inhalt |
|--------------|--------|
| `Constants/` | PLC-Konstanten (Anwenderkonstanten) als CSV |
| `UDT/`       | PLC-Datentypen (`.udt`) |
| `DB/`        | Globale Datenbausteine (`.db`) |

## Import-Reihenfolge

Abhängigkeiten zuerst:

1. **Konstanten** – UDTs und Bausteine verwenden sie.
2. **UDTs**
3. **Datenbausteine** (ab Phase 2)
4. **Funktionsbausteine** (ab Phase 3)

## Konstanten anlegen

`Constants/Constants.csv` enthält alle Anwenderkonstanten (Name, Datentyp, Wert, Kommentar).

1. In TIA Portal unter *PLC-Variablen* eine neue Variablentabelle `Constants` anlegen.
2. Register **Anwenderkonstanten** öffnen.
3. Die Konstanten eintragen. Real-Werte immer mit Punkt schreiben (`2.0`, nicht `2,0`).

Das genaue Importformat für Variablentabellen klären wir, sobald TIA Portal installiert ist: einmal eine Tabelle exportieren, dann kann die CSV in dieses Format umgewandelt und direkt importiert werden.

## UDTs importieren

1. Im Projektbaum unter *Externe Quellen* → *Neue externe Datei hinzufügen* die `.udt`-Dateien auswählen.
2. Rechtsklick auf die Datei → *Bausteine aus Quelle generieren*.
3. Die Datentypen erscheinen unter *PLC-Datentypen*.

## Datenbausteine importieren

Wie bei den UDTs: `.db`-Dateien unter *Externe Quellen* hinzufügen → *Bausteine aus Quelle generieren*. Erst importieren, wenn Konstanten und UDTs fehlerfrei übersetzt sind.

| Datenbaustein | Inhalt | Remanent |
|---|---|---|
| `DB_IO` | Ein-/Ausgangsabbild, Umschaltung Simulation/Hardware | nein |
| `DB_Packages` | Paketverfolgung der Steuerung | nein |
| `DB_Plant` | Anlagenzustand, Förderband, Sortierer, Alarme | nein |
| `DB_Statistics` | Zähler und Kennzahlen | ja |
| `DB_Hmi` | Tasten und Eingaben vom Bedienpanel | nein |
| `DB_Simulation` | simulierte Pakete, Erzeugung, Störungen | nein |

## Nach Änderungen in TIA Portal

Rechtsklick auf den Baustein bzw. Datentyp → *Quelle aus Bausteinen generieren* → Datei hier im passenden Ordner überschreiben.
