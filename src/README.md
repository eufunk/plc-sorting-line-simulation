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
4. **Funktionen und Funktionsbausteine** – aufgerufene vor aufrufenden: `FC_Random`, `FB_Simulation`, `FB_InputMapping`, `FB_OutputMapping`, `FB_Plant`, `FB_Conveyor`, zuletzt `FB_Main` (danach `IDB_Main` neu generieren bzw. beim Übersetzen aktualisieren lassen)
5. **Organisationsbausteine** – siehe unten, OB30 wird von Hand angelegt

## Konstanten und I/O-Variablen importieren

`Constants/Constants.csv` (Anwenderkonstanten) und `Tags/IoTags.csv` (Variablen mit Hardware-Adressen) werden nicht abgetippt, sondern als Excel-Datei importiert. Die Datei erzeugt ein Skript im Format des TIA-Exports:

```
python tools/make_tag_import.py
```

Ergebnis: `C:\TIA\PlcTags_Import.xlsx` (außerhalb des Repositorys, wird bei jeder Änderung der CSVs neu erzeugt).

1. In TIA Portal eine Variablentabelle öffnen, z. B. *PLC-Variablen → Constants*.
2. In der Symbolleiste der Tabelle **Importieren** wählen, die Datei `PlcTags_Import.xlsx` auswählen.
3. Beim Import **Variablen** und **Konstanten** ankreuzen. Ohne den Haken bei *Konstanten* werden nur die I/O-Variablen übernommen – ohne Fehlermeldung.
4. TIA legt die Tabellen **Constants** (Konstanten) und **IO** (I/O-Variablen) an bzw. füllt sie.
5. Testeinträge aus dem Formatexport (`TEST`, `iTest`) löschen.

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
4. Den Instanz-DB aus der Quelle `DB/IDB_Main.db` generieren (erst nach `FB_Main`). TIA legt ihn **nicht** automatisch an, wenn der Aufruf von Hand getippt wird.
5. Übersetzen.

`Main [OB1]` bleibt leer: Das gesamte Programm läuft im 100-ms-Takt von OB30.

## Namensregel

Variablen- und Feldnamen dürfen keine SCL-Schlüsselwörter sein (z. B. `EXIT`, `RETURN`, `CONTINUE`, `CASE`, `REGION`). TIA nimmt solche Namen in UDTs zwar an, der Zugriff im SCL-Code (`#Inputs.Exit[1]`) scheitert dann aber mit *„Ungültige Variablendefinition … Bezeichner erwartet“*.

## Nach Änderungen in TIA Portal

Rechtsklick auf den Baustein bzw. Datentyp → *Quelle aus Bausteinen generieren* → Datei hier im passenden Ordner überschreiben.
