# HMI – Bedienpanel der Sortieranlage

Phase 4. Bilder und Inhalte nach [FeatureSpec, Abschnitt 11](FeatureSpec.md#11-hmi). Die Bilder werden in TIA Portal von Hand gebaut; dieses Dokument legt fest, **was** wohin kommt und an welche Variable es gebunden ist.

## 1. Gerät und Verbindung

| | |
|---|---|
| Gerät | **TP1200 Comfort** (12", 1280 × 800), Name `HMI_SortingLine` |
| Software | WinCC Advanced (Trial) – Comfort Panels |
| Verbindung | `HMI_SortingLine` ↔ `PLC_SortingLine` über PN/IE_1, Panel-IP **192.168.0.2** |
| Bilder | `01_Uebersicht` (Startbild), `02_Paketdaten`, `03_Statistik`, `04_Diagnose`, `05_Alarme` |
| Navigation | Tasten am unteren Rand aus dem Gerätewizard (Vorlage) |

### Panel anlegen

1. Projektbaum → **Add new device** → **HMI** → *SIMATIC Comfort Panel* → *12" Display* → **TP1200 Comfort**, neueste Version, **Start device wizard** angehakt → OK. Bei Nachfrage Trial-Lizenz **WinCC Advanced** aktivieren.
2. Gerätewizard:

   | Seite | Einstellung |
   |---|---|
   | PLC connections | *Browse* → `PLC_SortingLine` |
   | Screen layout | Kopfzeile mit Datum/Uhrzeit, Logo aus |
   | Alarms | alle Häkchen aus (eigenes Alarmbild) |
   | Screens | Startbild `01_Uebersicht`, auf gleicher Ebene `02_Paketdaten`, `03_Statistik`, `04_Diagnose`, `05_Alarme` |
   | System screens | alle aus |
   | Buttons | Navigation unten, *Exit* darf bleiben |

3. Gerät in `HMI_SortingLine` umbenennen. **Devices & networks**: Panel und CPU am Subnetz PN/IE_1 (sonst Schnittstellen per Maus verbinden), Panel-IP **192.168.0.2**.
4. `HMI_SortingLine` → **Compile → Software (rebuild all)**.

## 2. Grundregeln beim Bauen

- **Variablen nicht abtippen:** Im Projektbaum unter `PLC_SortingLine → Program blocks` den DB öffnen (oder *Details view* unten links), Variable **per Drag & Drop** auf das Bild oder in das Feld *Process tag* ziehen. TIA legt die HMI-Variable automatisch an (Tabelle *Default tag table*).
- **Erfassungszyklus:** Standard 1 s ist für Zähler in Ordnung. Für die **Paketpositionen** und Zustände auf `01_Uebersicht` in *HMI tags → Default tag table* den *Acquisition cycle* auf **100 ms** stellen, sonst springen die Pakete.
- **Tasten (START, STOPP, RESET, Paket erzeugen, Zähler zurücksetzen):** *Events → Press → SetBit* auf die Variable. Die SPS setzt das Bit selbst zurück – kein *ResetBit* nötig.
- **Tipptasten (Sortierer im Handbetrieb):** *Press → SetBit*, *Release → ResetBit*.
- **Schalter (Hand/Auto, Band EIN, Simulation, Störungen):** Objekt **Switch** mit *Process tag* auf die Bool-Variable.
- **Zahlenfelder:** Objekt **I/O field**, *Mode*: *Output* (nur Anzeige) bzw. *Input/output* (Eingabe).
- **Texte statt Zahlen:** Objekt **Symbolic I/O field** mit einer Textliste (Abschnitt 3).

## 3. Textlisten

Quelle: [src/HMI/TextLists.csv](../src/HMI/TextLists.csv). Nicht abtippen, sondern importieren:

1. `python tools/make_textlist_import.py` → erzeugt `C:\TIA\Textlisten_Import.xlsx`
2. *HMI_SortingLine → Text- und Grafiklisten → Textlisten* → Symbol **Importieren** (zweites Symbol oben links) → Datei wählen.

Bereich: *Wert/Bereich* (`Decimal`), für Bool-Variablen *Bit*.

| Name | Werte |
|---|---|
| `TL_PlantState` | 0 AUS · 1 BEREIT · 2 AUTOMATIK · 3 HAND · 4 STÖRUNG · 5 NOT-HALT |
| `TL_PkgStatus` | 0 – · 1 wartet · 2 unterwegs · 3 erkannt · 4 Prüfung · 5 Sortierung · 6 sortiert · 7 Ausschuss · 8 FEHLER |
| `TL_Target` | 0 – · 1 A1 Metall · 2 A2 Kunststoff klein · 3 A3 Kunststoff groß · 4 A4 Ausschuss |
| `TL_Material` | 0 ? · 1 Metall · 2 Kunststoff |
| `TL_Size` | 0 ? · 1 klein · 2 groß |
| `TL_Reason` | 0 – · 1 Qualität · 2 zu leicht · 3 zu schwer · 4 ungültig · 5 Fehlsortierung · 6 Waage defekt |
| `TL_SorterState` | 0 eingefahren · 1 fährt aus · 2 ausgefahren · 3 fährt ein · 9 STÖRUNG |
| `TL_Quality` (Bit) | 0 Ausschuss · 1 OK |

## 4. Bild `01_Uebersicht`

```
 x:   0        140   290  390  490  590  690  790  890  990  1140   1280
 y 70 ┌───────────────────────────────────────────────────────────────┐
 y 90 │  [02_Paketdaten] [03_Statistik] [04_Diagnose] [05_Alarme]      │
 y 170│ Zustand: [AUTOMATIK]   (●)H1 Betrieb  (●)H2 Störung            │
      │ Band: läuft   Pakete aktiv: [3]          [Alarmanzeige]        │
 y 250│                                      ┌┐   ┌┐   ┌┐              │
      │                                      Q1   Q2   Q3              │
 y 330│      ════[P]════════[P]═══════[P]════════════════════════ ┌────┐│
      │      ST1  ST2  ST3  ST4  ST5  S6                          │ A4 ││
 y 420│                                    ┌──┐ ┌──┐ ┌──┐        └────┘│
      │                                    │A1│ │A2│ │A3│              │
      │                                    └──┘ └──┘ └──┘              │
 y 560│  [ START ]  [ STOPP ]  [ RESET ]  [ HAND | AUTO ]              │
      └───────────────────────────────────────────────────────────────┘
       (darunter die Leiste der Vorlage: Startbild, Runtime beenden)
```

Die vier Navigationstasten hat der Gerätewizard angelegt (senkrecht links) – nicht löschen, sondern waagerecht direkt unter die Kopfzeile schieben.

**Band:** Bandposition 0–100 % = x 140–1140 (10 Pixel je %).

| Objekt | Typ | Position / Größe | Bindung |
|---|---|---|---|
| Band | Rectangle, grau | x 140, y 330, 1000 × 40 | – |
| Stationsmarken ST1–ST5, S6 | Text + kurze Line | x 160, 290, 390, 490, 590, 690 | – |
| Sortierer Q1–Q3 | Rectangle 30 × 60 | x 775 / 875 / 975, y 260 | *Animations → Appearance*, Tag `"DB_Plant".Sorters[n].State`: 0 grau · 1 gelb · 2 grün · 3 gelb · 9 rot |
| Ausgänge A1–A3 | Rectangle 80 × 60 + I/O field | x 750 / 850 / 950, y 420 | I/O field (Output): `"DB_Statistics".Statistics.ExitCount[1..3]` |
| Ausgang A4 | Rectangle 100 × 60 + I/O field | x 1150, y 320 | `"DB_Statistics".Statistics.ExitCount[4]` |
| **Paket 1–5** | Rectangle 40 × 30 | y 335, Startwert x 120 | siehe unten |
| Zustand | Symbolic I/O field | oben links | `"DB_Plant".State`, `TL_PlantState` |
| H1, H2 | Circle | oben | *Appearance*, Tag `"DB_IO".Outputs.LampRun` bzw. `LampFault`: 0 dunkelgrau · 1 grün bzw. rot |
| Band läuft | Circle oder Text | oben | *Appearance*, `"DB_Plant".Conveyor.Running` |
| Pakete aktiv | I/O field (Output) | oben | `"DB_Packages".ActiveCount` |
| Alarmanzeige | **Alarm indicator** (Toolbox → Controls) | oben rechts | zeigt anstehende Meldungen, Klick → Bild `05_Alarme` (*Events → Click → ActivateScreen*) |
| START / STOPP / RESET | Button | y 560 | *Press → SetBit* `"DB_Hmi".Plant.Start` / `.Stop` / `.Reset` |
| HAND / AUTO | Switch | y 560 | `"DB_Hmi".Plant.SelectManual` (Text: *Auto* / *Hand*) |

**Paket n (n = 1…5)** – ein Rechteck je Platz in `DB_Packages`:

| Animation | Einstellung |
|---|---|
| *Horizontal movement* | Tag `"DB_Packages".Packages[n].Position`, Bereich **0 … 100**, Start-x **120**, End-x **1120** |
| *Visibility* | Tag `"DB_Packages".Packages[n].Status`, *Visible* im Bereich **3 … 5** (erkannt bis Sortierung) |
| *Appearance* (Hintergrund) | Tag `"DB_Packages".Packages[n].Target`: 0 weiß (Ziel noch offen) · 1 blaugrau · 2 hellgrün · 3 dunkelgrün · 4 rot |

Paket 1 fertig bauen, dann 4× kopieren und in jeder Kopie bei den drei Animationen den Index `[1]` ersetzen.

## 5. Bild `02_Paketdaten`

Tabelle aus Feldern, eine Zeile je Platz `Packages[1..5]`:

| Spalte | Objekt | Variable `"DB_Packages".Packages[n].…` | Format |
|---|---|---|---|
| ID | I/O field | `ID` | 9999 |
| Status | Symbolic I/O | `Status` | `TL_PkgStatus` |
| Position | I/O field | `Position` | 999.9 % |
| Größe | Symbolic I/O | `Size` | `TL_Size` |
| Material | Symbolic I/O | `Material` | `TL_Material` |
| Gewicht | I/O field | `Weight` | 9.999 kg |
| Qualität | Symbolic I/O | `QualityOk` | `TL_Quality` |
| Ziel | Symbolic I/O | `Target` | `TL_Target` |
| Ausschussgrund | Symbolic I/O | `RejectReason` | `TL_Reason` |

Zeile 1 bauen, ganze Zeile markieren, kopieren, viermal einfügen, Index anpassen. Überschriften als Text-Felder.

## 6. Bild `03_Statistik`

Alle Felder: I/O field (Output), Variablen aus `"DB_Statistics".Statistics.…`

| Anzeige | Variable | Format |
|---|---|---|
| Pakete gesamt | `Total` | 99999 |
| Gutteile / Ausschuss / Fehler | `Good`, `Rejected`, `Errors` | 99999 |
| Ausgang 1–4 | `ExitCount[1..4]` | 99999, dazu je ein **Bar** (0 … 100) |
| Ausschussquote | `RejectRate` | 999.9 % |
| Ausschuss nach Grund 1–6 | `RejectReasonCount[1..6]` | 99999, Beschriftung wie `TL_Reason` |
| Letzte / mittlere Durchlaufzeit | `LastTransitTime`, `AvgTransitTime` | 99999 ms |
| Durchsatz | `PackagesPerMinute` | 99.9 /min |
| Taste **Zähler zurücksetzen** | `"DB_Hmi".Statistics.Reset` | *Press → SetBit* |

## 7. Bild `04_Diagnose`

Drei Bereiche nebeneinander.

**Sensoren und Aktoren** – Circles mit *Appearance* (0 grau, 1 grün), Beschriftung mit Kennung:

| Kennung | Variable |
|---|---|
| B1 Not-Halt OK, B2 Motorschutz OK | `"DB_IO".Inputs.EmergencyStopOk`, `.MotorProtectOk` |
| S1, S2, S3, S5, S6 | `"DB_IO".Inputs.Infeed`, `.SizeLarge`, `.Metal`, `.QualityOk`, `.SortEntry` |
| S7–S10 | `"DB_IO".Inputs.ExitSensor[1..4]` |
| S11/S13/S15 eingefahren, S12/S14/S16 ausgefahren | `"DB_IO".Inputs.SorterRetracted[1..3]`, `.SorterExtended[1..3]` |
| S4 Waage (Rohwert) | I/O field `"DB_IO".Inputs.WeightRaw` |
| M1, Q1–Q3, H1, H2 | `"DB_IO".Outputs.Conveyor`, `.SorterExtend[1..3]`, `.LampRun`, `.LampFault` |
| Sortierer 1–3 Zustand / Hübe | Symbolic I/O `"DB_Plant".Sorters[n].State` (`TL_SorterState`), I/O field `.StrokeCount` |
| Band-Betriebszeit | I/O field `"DB_Plant".Conveyor.RunSeconds` (s) |

**Handbetrieb** (wirkt nur im Zustand HAND):

| Element | Variable |
|---|---|
| Switch *Band EIN* | `"DB_Hmi".Manual.ConveyorRun` |
| Tipptasten *Sortierer 1/2/3* | `"DB_Hmi".Manual.SorterExtend[1..3]` – *Press SetBit, Release ResetBit* |

Optional den ganzen Bereich nur im Handbetrieb sichtbar machen: *Visibility*, Tag `"DB_Plant".State`, Bereich 3 … 3.

**Simulation:**

| Element | Variable |
|---|---|
| Switch *Zufallspakete* | `"DB_Simulation".Settings.AutoGenerate` |
| I/O field *Intervall* (Input) | `"DB_Simulation".Settings.GenerateInterval` – Eingabe in ms, 3000 … 10000 |
| Symbolic I/O (Input) *Material*, *Größe* | `"DB_Simulation".ManualPackage.Material` (`TL_Material`), `.Size` (`TL_Size`) |
| I/O field (Input) *Gewicht* | `"DB_Simulation".ManualPackage.Weight`, 9.99 kg |
| Switch *Qualität OK* | `"DB_Simulation".ManualPackage.QualityOk` |
| Taste *Paket erzeugen* | `"DB_Simulation".ManualPackage.Generate` – *Press → SetBit* |
| Switches *Störung simulieren* | `"DB_Simulation".Faults.SorterBlocked[1..3]`, `.SorterStuck[1..3]`, `.SortEntrySensorDefect`, `.MotorProtectTripped`, `.EmergencyStop`, `.ScaleDefect` |

## 8. Bild `05_Alarme` und Meldungen

**Bild:** Objekt **Alarm view** (Toolbox → Controls), fast bildfüllend. In den Eigenschaften *Display → Current alarm state* aktivieren und die Taste *Acknowledge* einblenden.

**Meldungen:** *HMI_SortingLine → HMI alarms → Discrete alarms*. Trigger: `"DB_Plant".Alarm.Latched` (Word), Quittier-Variable HMI: `"DB_Plant".Alarm.AckHmi`, Bitnummer wie beim Trigger. Klassen: Störung = *Errors* (quittierpflichtig), Warnung = *Warnings*.

| Nr. | Text | Klasse | SPS-Bit | HMI-Triggerbit* |
|---|---|---|---|---|
| 1 | Not-Halt betätigt | Errors | 0 | 8 |
| 2 | Motorschutz Förderband ausgelöst | Errors | 1 | 9 |
| 3 | Sortierer 1 nicht ausgefahren | Errors | 2 | 10 |
| 4 | Sortierer 2 nicht ausgefahren | Errors | 3 | 11 |
| 5 | Sortierer 3 nicht ausgefahren | Errors | 4 | 12 |
| 6 | Sortierer 1 nicht zurückgefahren | Errors | 5 | 13 |
| 7 | Sortierer 2 nicht zurückgefahren | Errors | 6 | 14 |
| 8 | Sortierer 3 nicht zurückgefahren | Errors | 7 | 15 |
| 9 | Sortierer Endlagen unplausibel | Errors | 8 | 0 |
| 10 | Paket nicht erkannt | Errors | 9 | 1 |
| 11 | Paket nicht am Ausgang angekommen | Errors | 10 | 2 |
| 12 | Fehlsortierung – Paket am Bandende | Warnings | 11 | 3 |
| 13 | Waage Messfehler | Warnings | 12 | 4 |

\* Bei Word-Triggervariablen zählt WinCC die Bits **byteweise vertauscht** (PLC-Bit 0 = HMI-Bit 8). Erst prüfen, welche Nummerierung der Editor in der Spalte *Trigger address* anzeigt: Steht dort für Bit 8 die Adresse des **ersten** Bytes, gilt die rechte Spalte. Im Test sicherstellen: Not-Halt (Test 13) muss *Not-Halt betätigt* zeigen, Sortierer 1 blockiert (Test 10) *Sortierer 1 nicht ausgefahren*.

## 9. Testen in der VM

1. PLC wie gewohnt in PLCSIM laden und starten.
2. `HMI_SortingLine` markieren → **Online → Simulation → Start**. Die Runtime-Simulation öffnet das Panel in einem Fenster.
3. Verbindet sich das Panel nicht mit PLCSIM (Felder zeigen `#####`): in der Verbindung `HMI_SortingLine` ↔ `PLC_SortingLine` die Schnittstelle prüfen; der Zugangspunkt für die Simulation muss auf die PLCSIM-Schnittstelle zeigen. Details beim ersten Test.
4. Mit dem Panel Tests 001–013 von Hand durchspielen und den automatischen Testablauf (`DB_Test`) parallel laufen lassen – das Panel muss alle Zustände richtig anzeigen.
