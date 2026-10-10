# Testanleitung – Funktionstest in PLCSIM

Testfälle 001–013 aus der [FeatureSpec, Abschnitt 13](FeatureSpec.md#13-testfälle), durchgeführt in der Azure-VM ([Anleitung_Azure-VM.md](Anleitung_Azure-VM.md)). Solange es noch kein HMI gibt, wird die Anlage über eine **Beobachtungstabelle** bedient und beobachtet.

## 1. Vorbereitung

1. **Laptop:** geänderte Quellen importieren und übersetzen.
2. **Laptop:** Beobachtungstabelle anlegen (Abschnitt 2) – auf dem Laptop, damit sie im Archiv steckt. Eine nur in der VM angelegte Tabelle geht beim nächsten Dearchivieren verloren.
3. **Laptop:** Projekt archivieren (`C:\TIA\Archiv\SortingLine.zap21`).
4. Azure-Portal → `vm-tia` → **Starten**, dann `C:\TIA\vm-tia.rdp`.
5. **VM:** TIA Portal schließen, den alten Projektordner `C:\TIA\SortingLine` löschen, Archiv holen und dearchivieren:
   ```
   robocopy \\tsclient\C\TIA\Archiv C:\TIA SortingLine.zap21 /Z
   ```
6. **VM:** `PLC_SortingLine` → **Online → Simulation → Start** → Laden → **Start all**. PLCSIM zeigt RUN.

## 2. Beobachtungstabelle anlegen

Auf dem Laptop: Projektbaum → `PLC_SortingLine` → **Watch and force tables → Add new watch table** → Name `WT_Test`. Die Tabelle wird mit dem Projekt archiviert; in der VM öffnen und dort beobachten.

Die folgenden Zeilen markieren, kopieren und in der Tabelle in die erste Zelle der Spalte **Name** einfügen (Strg+V). Klappt das Einfügen nicht, die Namen einzeln eintippen – TIA ergänzt beim Tippen.

```
"DB_Plant".State
"DB_Plant".HomePosition
"DB_Plant".Conveyor.Running
"DB_Plant".Sorters[1].State
"DB_Plant".Sorters[2].State
"DB_Plant".Sorters[3].State
"DB_Plant".Alarm.Latched
"DB_Plant".Alarm.AnyFault
"DB_Plant".Alarm.AnyWarning
"DB_Plant".Alarm.FirstAlarm
"DB_IO".Outputs.LampRun
"DB_IO".Outputs.LampFault
"DB_Packages".ActiveCount
"DB_Hmi".Plant.Start
"DB_Hmi".Plant.Stop
"DB_Hmi".Plant.Reset
"DB_Hmi".Plant.SelectManual
"DB_Hmi".Manual.ConveyorRun
"DB_Hmi".Manual.SorterExtend[1]
"DB_Simulation".Settings.AutoGenerate
"DB_Simulation".ManualPackage.Material
"DB_Simulation".ManualPackage.Size
"DB_Simulation".ManualPackage.Weight
"DB_Simulation".ManualPackage.QualityOk
"DB_Simulation".ManualPackage.Generate
"DB_Simulation".Faults.SorterBlocked[1]
"DB_Simulation".Faults.SorterStuck[1]
"DB_Simulation".Faults.SortEntrySensorDefect
"DB_Simulation".Faults.EmergencyStop
"DB_Statistics".Statistics.Total
"DB_Statistics".Statistics.ExitCount[1]
"DB_Statistics".Statistics.ExitCount[2]
"DB_Statistics".Statistics.ExitCount[3]
"DB_Statistics".Statistics.ExitCount[4]
"DB_Statistics".Statistics.Errors
"DB_Hmi".Statistics.Reset
```

- Bei `"DB_Plant".Alarm.Latched` die Spalte **Display format** auf **Hex** stellen.
- In der VM: **Monitor all** (Brillen-Symbol) einschalten: Die Spalte *Monitor value* zeigt jetzt die aktuellen Werte.

**Werte vorgeben:** In der Spalte **Modify value** den Wert eintragen (z. B. `TRUE`, `2`, `0.5`), Zeile(n) markieren → **Modify now** (Blitz-Symbol mit „1“) oder Rechtsklick → *Modify → Modify now*. Tasten wie `Start`, `Reset` und `Generate` setzt das Programm selbst wieder auf FALSE – einfach jedes Mal neu *Modify now* auf `TRUE`.

**Pakete beobachten:** Zusätzlich `DB_Packages` öffnen (Projektbaum → Program blocks) und dort ebenfalls **Monitor all** einschalten. Unter `Packages[1..5]` stehen Status, Position, Größe, Material, Gewicht, Ziel und Ausschussgrund jedes Pakets. Fenster nebeneinander: *Window → Split editor space vertically*.

## 3. Codes

| Wert | Anlage `State` | Paket `Status` | Sortierer `State` | `Target` | `RejectReason` |
|---|---|---|---|---|---|
| 0 | OFF | EMPTY (frei) | eingefahren | – | – |
| 1 | READY | – | fährt aus | Ausgang 1 Metall | Qualität |
| 2 | AUTO | – | ausgefahren | Ausgang 2 Kunststoff klein | zu leicht |
| 3 | MANUAL | DETECTED (an ST1) | fährt ein | Ausgang 3 Kunststoff groß | zu schwer |
| 4 | FAULT | INSPECTION (ST2–ST5) | – | Ausgang 4 Ausschuss | ungültig |
| 5 | EMERGENCY | SORTING (Ziel bestimmt) | – | – | Fehlsortierung |
| 6 | – | SORTED | – | – | Waage defekt |
| 7 | – | REJECTED | – | – | – |
| 8 | – | ERROR | – | – | – |
| 9 | – | – | FAULT | – | – |

Eingaben für Pakete: `Material` 1 = Metall, 2 = Kunststoff · `Size` 1 = klein, 2 = groß · `Weight` in kg.

Alarmbits in `Alarm.Latched` (Hex): `16#0001` Not-Halt · `16#0004` Sortierer 1 nicht ausgefahren · `16#0020` Sortierer 1 nicht zurückgefahren · `16#0200` Paket nicht erkannt · `16#0400` Paket nicht am Ausgang · `16#0800` Fehlsortierung (Warnung) · `16#1000` Waage (Warnung). Vollständige Liste: [Anlagenkonfiguration, Abschnitt 8](Anlagenkonfiguration.md#8-alarme).

**Zeiten:** Ein Paket braucht vom Einlauf bis Sortierer 1 ca. 13 s, bis Sortierer 2 ca. 15 s, bis Sortierer 3 ca. 17 s, bis zum Bandende 20 s.

**SORTED/REJECTED sieht man nicht:** Diese Status stehen nur 100 ms an, danach ist der Platz wieder frei. Ob ein Paket richtig angekommen ist, zeigen die Zähler `ExitCount[1..4]`.

## 4. Grundtest – Anlage einschalten

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 0.1 | nach dem Laden nur beobachten | `State` = 1 (READY), `HomePosition` = TRUE, `LampRun` blinkt, `Alarm.Latched` = 16#0000 | |
| 0.2 | `AutoGenerate` = FALSE | keine neuen Pakete mehr (ein bereits erzeugtes Paket kann am Einlauf stehen) | |
| 0.3 | `Start` = TRUE | `State` = 2 (AUTO), `Conveyor.Running` = TRUE, `LampRun` Dauerlicht | |
| 0.4 | warten, bis `ActiveCount` = 0 | ein evtl. vorhandenes Zufallspaket hat die Anlage verlassen | |
| 0.5 | `"DB_Hmi".Statistics.Reset` = TRUE | alle Zähler = 0 | |
| 0.6 | `Stop` = TRUE, danach wieder `Start` = TRUE | `State` 2 → 1 → 2, Band steht bzw. läuft | |

Die Anlage bleibt für die Tests 001–008 in AUTO. Pakete einzeln erzeugen und jeweils warten, bis `ActiveCount` wieder 0 ist.

## 5. Sortierung (Tests 001–008)

Ablauf je Test: `Material`, `Size`, `Weight`, `QualityOk` eintragen → alle vier **Modify now** → dann `Generate` = TRUE → in `DB_Packages` mitverfolgen → nach ca. 20 s Zähler prüfen.

| Test | Material | Size | Weight | QualityOk | Erwartet | Ergebnis |
|---|---|---|---|---|---|---|
| 001 | 1 | 1 | 2.0 | TRUE | `Target` = 1, Sortierer 1 fährt aus und ein, `ExitCount[1]` +1 | |
| 002 | 1 | 2 | 2.0 | TRUE | `Target` = 1, `ExitCount[1]` +1 | |
| 003 | 2 | 1 | 2.0 | TRUE | `Target` = 2, Sortierer 2 fährt aus, `ExitCount[2]` +1 | |
| 004 | 2 | 2 | 2.0 | TRUE | `Target` = 3, Sortierer 3 fährt aus, `ExitCount[3]` +1 | |
| 005 | 1 | 1 | 2.0 | FALSE | `Target` = 4, `RejectReason` = 1, kein Sortierer bewegt sich, `ExitCount[4]` +1 | |
| 006 | 1 | 1 | 0.3 | TRUE | gemessen 0.3, `Target` = 4, `RejectReason` = 2, `ExitCount[4]` +1 | |
| 007 | 1 | 1 | 6.0 | TRUE | gemessen 6.0, `Target` = 4, `RejectReason` = 3, `ExitCount[4]` +1 | |
| 008a | 2 | 1 | 0.5 | TRUE | gemessen **0.5**, `Target` = 2, `ExitCount[2]` +1 | |
| 008b | 2 | 2 | 5.0 | TRUE | gemessen **5.0**, `Target` = 3, `ExitCount[3]` +1 | |

In `DB_Packages` dabei prüfen: `Status` 3 → 4 → 5, gemessene `Size`, `Material` und `Weight` stimmen mit der Eingabe überein, `Position` steigt um 0,5 je 100 ms.

Nach allen Tests: `Total` = 9, `ExitCount` = 2 / 2 / 2 / 3, `Alarm.Latched` = 16#0000.

## 6. Kapazität (Test 009)

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 9.1 | `AutoGenerate` = TRUE, Anlage in AUTO | alle 3 s ein neues Zufallspaket | |
| 9.2 | warten, bis `ActiveCount` = 5 → sofort `Stop` = TRUE | Band steht, 5 Pakete auf dem Band | |
| 9.3 | `AutoGenerate` = FALSE, dann `Generate` = TRUE | `Generate` **bleibt TRUE**, `ActiveCount` bleibt 5 – kein 6. Paket | |
| 9.4 | `Start` = TRUE | sobald ein Paket die Anlage verlassen hat, wird das wartende erzeugt: `Generate` → FALSE | |
| 9.5 | warten, bis `ActiveCount` = 0 | alle Pakete sortiert, `Alarm.Latched` = 16#0000 | |

`ActiveCount` darf während des ganzen Tests nie größer als 5 werden.

## 7. Störungen (Tests 010–012)

Vorher: Anlage in AUTO, `AutoGenerate` = FALSE, `ActiveCount` = 0.

### Test 010 – Sortierer blockiert

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 10.1 | `Faults.SorterBlocked[1]` = TRUE, dann Metallpaket (1 / 1 / 2.0 / TRUE) erzeugen | | |
| 10.2 | nach ca. 13 s | `Sorters[1].State` = 1, nach 1 s = 9 (FAULT) | |
| 10.3 | | `Alarm.Latched` = 16#0004, `AnyFault` = TRUE, `State` = 4 (FAULT), `Conveyor.Running` = FALSE, `LampFault` blinkt | |
| 10.4 | `Faults.SorterBlocked[1]` = FALSE, dann `Reset` = TRUE | `Sorters[1].State` = 0, `State` 4 → 0 → 1, `Latched` = 16#0000 | |
| 10.5 | `Start` = TRUE | Paket ist am Sortierer vorbei und läuft ans Bandende: `ExitCount[4]` +1, `Latched` = 16#0800 (Warnung Fehlsortierung), `AnyWarning` = TRUE, Band läuft weiter | |
| 10.6 | `Reset` = TRUE | `Latched` = 16#0000 | |

### Test 011 – Sortierer klemmt beim Zurückfahren

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 11.1 | `Faults.SorterStuck[1]` = TRUE, dann Metallpaket erzeugen | | |
| 11.2 | nach ca. 13 s | Paket wird ausgeschleust: `ExitCount[1]` +1 | |
| 11.3 | | `Sorters[1].State` = 3, nach 1 s = 9; `Latched` = 16#0020, `State` = 4, Band steht | |
| 11.4 | `Reset` = TRUE, **während** `SorterStuck[1]` noch TRUE ist | Sortierer versucht einzufahren und geht nach 1 s erneut in FAULT, Alarm wieder da – erst Ursache beheben | |
| 11.5 | `Faults.SorterStuck[1]` = FALSE, dann `Reset` = TRUE | `Sorters[1].State` 3 → 0, `State` 4 → 0 → 1, `Latched` = 16#0000 | |

### Test 012 – Lichtschranke S6 defekt

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 12.1 | `Faults.SortEntrySensorDefect` = TRUE, dann Metallpaket erzeugen | | |
| 12.2 | nach ca. 11 s (Position 55) | Paket `Status` = 8 (ERROR), `Latched` = 16#0200, `State` = 4, Band steht, `Errors` +1 | |
| 12.3 | `Faults.SortEntrySensorDefect` = FALSE, dann `Reset` = TRUE | ERROR-Paket entfernt: `ActiveCount` = 0; `State` → 1 | |
| 12.4 | `Start` = TRUE | Das echte (simulierte) Paket liegt noch auf dem Band und fällt ans Bandende. Die Steuerung kennt es nicht mehr: **kein** Zähler ändert sich, kein neuer Alarm | |

## 8. Not-Halt (Test 013)

| Schritt | Aktion | Erwartet | Ergebnis |
|---|---|---|---|
| 13.1 | `SelectManual` = TRUE | `State` = 3 (MANUAL), `LampRun` blinkt | |
| 13.2 | `Manual.ConveyorRun` = TRUE, `Manual.SorterExtend[1]` = TRUE | Band läuft, `Sorters[1].State` = 2 (ausgefahren) | |
| 13.3 | `Faults.EmergencyStop` = TRUE | `State` = 5, `Conveyor.Running` = FALSE, `Sorters[1].State` → 3 → 0 (fährt zurück), `Latched` = 16#0001, `LampFault` blinkt; `Manual.ConveyorRun` und `SorterExtend[1]` springen auf FALSE | |
| 13.4 | `Faults.EmergencyStop` = FALSE | `State` bleibt 5 – Not-Halt muss quittiert werden | |
| 13.5 | `Reset` = TRUE | `State` 5 → 0 → 1 → 3 (Schalter steht noch auf Hand); Band und Sortierer bleiben aus – nichts läuft von allein wieder an | |
| 13.6 | `SelectManual` = FALSE | `State` = 1 (READY) | |

## 9. Ergebnisse zurückmelden

Pro Test reicht ein Wort in der Spalte *Ergebnis* (OK / Abweichung). Bei einer Abweichung einen Screenshot von Beobachtungstabelle und `DB_Packages` machen – Claude korrigiert die Quellen, danach: Laptop importieren → übersetzen → archivieren → in der VM dearchivieren → Test wiederholen.

Nach dem Test: Projekt in der VM speichern, VM im Azure-Portal **beenden**.
