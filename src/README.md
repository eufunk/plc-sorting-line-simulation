# src – Quellen für TIA Portal

Exportierte Textquellen des SPS-Programms. Das TIA-Portal-Projekt selbst liegt außerhalb des Repositorys (z. B. `C:\TIA\SortingLine\`).

| Ordner       | Inhalt |
|--------------|--------|
| `Constants/` | PLC-Konstanten (Anwenderkonstanten) als CSV |
| `UDT/`       | PLC-Datentypen (`.udt`) |
| `DB/`        | Globale Datenbausteine (`.db`) |
| `Tags/`      | PLC-Variablen mit Hardware-Adressen (I/O-Liste) als CSV |
| `FC/`        | Funktionen (`.scl`) |
| `FB/`        | Funktionsbausteine (`.scl`) |
| `OB/`        | Organisationsbausteine (`.scl`) |

## Import-Reihenfolge

Abhängigkeiten zuerst:

1. **Konstanten** und **I/O-Variablen** – UDTs und Bausteine verwenden sie.
2. **UDTs**
3. **Datenbausteine**
4. **Funktionen und Funktionsbausteine** – aufgerufene vor aufrufenden: `FC_Random`, `FB_Simulation`, `FB_InputMapping`, `FB_OutputMapping`, zuletzt `FB_Main`
5. **Organisationsbausteine** – siehe unten, OB30 wird von Hand angelegt

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

## Funktionsbausteine importieren

Wie UDTs und DBs: `.scl`-Dateien unter *Externe Quellen* hinzufügen → *Bausteine aus Quelle generieren*.

## OB30 anlegen

Den Typ eines Organisationsbausteins legt eine Quelle nicht sicher fest. Deshalb von Hand:

1. *Programmbausteine* → *Neuen Baustein hinzufügen* → *Organisationsbaustein* → **Cyclic interrupt**
2. Name `OB_Cyclic100ms`, Nummer **30**, Taktzeit **100000 µs**, Sprache **SCL**
3. Inhalt aus `OB/OB_Cyclic100ms.scl` übernehmen: die Zeile `"IDB_Main"();`
4. Übersetzen – TIA legt den Instanz-DB `IDB_Main` an (Abfrage bestätigen).

`Main [OB1]` bleibt leer: Das gesamte Programm läuft im 100-ms-Takt von OB30.

## Nach Änderungen in TIA Portal

Rechtsklick auf den Baustein bzw. Datentyp → *Quelle aus Bausteinen generieren* → Datei hier im passenden Ordner überschreiben.
