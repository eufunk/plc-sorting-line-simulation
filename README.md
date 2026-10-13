# plc-sorting-line-simulation

Entwicklung einer simulierten Förderband-Sortieranlage mit Siemens S7 und SCL. Das Projekt umfasst die Steuerung, Werkstückerkennung, automatische Sortierung, Fehlerbehandlung sowie eine HMI-Visualisierung für Bedienung und Diagnose.

Es wird keine echte Hardware benötigt: Pakete, Sensoren und Aktoren werden in der SPS simuliert und mit S7-PLCSIM und der WinCC-Runtime-Simulation getestet.

## Anlage

```
┌─────────┐   ┌────────────────────────────────────┐   ┌──► Ausgang 1 – Metall
│ Einlauf │──►│ Förderband 10 m · 0,5 m/s          ├───┼──► Ausgang 2 – Kunststoff klein
└─────────┘   │ ST1 Erkennung → ST2 Größe →        │   ├──► Ausgang 3 – Kunststoff groß
              │ ST3 Material → ST4 Gewicht →       │   └──► Ausgang 4 – Ausschuss (Bandende)
              │ ST5 Qualität → ST6 Sortierstrecke  │
              └────────────────────────────────────┘
```

**ST** steht für **Station**: eine feste Stelle entlang des Bandes, an der mit dem Paket etwas passiert. Die Position ist in Prozent der Bandlänge angegeben.

| Station | Position | Aufgabe | Sensor dort |
|---|---|---|---|
| **ST1** Erkennung | 2 % | Paket kommt aufs Band, bekommt eine ID | Lichtschranke S1 |
| **ST2** Größe | 15 % | klein oder groß | S2 |
| **ST3** Material | 25 % | Metall oder Kunststoff | S3 (induktiver Sensor) |
| **ST4** Gewicht | 35 % | wiegen | S4 (Waage, analog) |
| **ST5** Qualität | 45 % | OK oder Ausschuss, danach steht das Ziel fest | S5 |
| **ST6** Sortierstrecke | ab 55 % | Ausschleusen mit den Sortierern Q1–Q3 (bei 65/75/85 %), Rest fällt am Bandende in Ausgang 4 | S6 am Anfang als Kontrolle |

Die Bezeichnungen ST und S sind absichtlich verschieden:

- **ST1–ST6** sind **Stationen**, also Orte und Aufgaben.
- **S1–S16** sind **Sensoren**, also einzelne Geräte mit einem Eingang an der SPS.

Jedes Paket hat Material, Größe, Gewicht und Qualität. Es durchläuft die Prüfstationen und wird an der Sortierstrecke von einem pneumatischen Sortierer ausgeschleust. Pakete, die nicht ausgeschleust werden, laufen am Bandende in den Ausschuss.

| Bedingung | Ziel |
|---|---|
| Qualität „Ausschuss“ oder Gewicht < 0,5 kg / > 5,0 kg | Ausgang 4 – Ausschuss |
| Metall | Ausgang 1 |
| Kunststoff, klein | Ausgang 2 |
| Kunststoff, groß | Ausgang 3 |

## Funktionen

- Bis zu 5 Pakete gleichzeitig auf dem Band, jedes mit eigenem Status und eigener Positionsverfolgung
- Betriebsarten Automatik und Hand
- Simulation mit zufälligen Paketen oder gezielter manueller Paketerzeugung über das HMI
- Simulierte Störungen (blockierter Sortierer, defekter Sensor, Not-Halt) für Fehlertests
- Alarme mit definierter Reaktion, Statistik je Ausgang und Ausschussquote
- HMI mit Übersicht, Paketdaten, Statistik, Diagnose und Alarmen

## Software

| Komponente | Version |
|---|---|
| TIA Portal – STEP 7 Professional | V21 |
| S7-PLCSIM | V21 |
| WinCC Advanced (Comfort Panel) | V21 |
| Programmiersprache | SCL |

## Repository-Struktur

```
├── docs/
│   ├── FeatureSpec.md            Fachliche Spezifikation
│   ├── Anlagenkonfiguration.md   Stationen, Sensoren, Aktoren, I/O-Liste, Zustände, Alarme
│   └── Planung/                  Tagespläne (Plan_JJJJ-MM-TT.md)
├── src/                          Exportierte SCL-Quellen und UDTs (ab Phase 2)
├── CLAUDE.md                     Arbeitsregeln für das Projekt
└── README.md
```

Das TIA-Portal-Projekt selbst liegt **nicht** im Repository. Versioniert werden nur die exportierten Textquellen (`.scl`, `.udt`). Sie werden in TIA Portal über *Externe Quellen → Bausteine aus Quelle generieren* importiert und nach Änderungen über *Quelle aus Bausteinen generieren* wieder exportiert.

## Projektstand

| Phase | Inhalt | Status |
|---|---|---|
| 1 – Planung | Konzept, Spezifikation, Anlagenkonfiguration, I/O-Liste | ✅ abgeschlossen |
| 2 – Datenmodell | Konstanten, UDTs und Datenbausteine | ✅ abgeschlossen |
| 3 – SPS | Simulation, Förderband, Erkennung, Sortierung, Betriebsarten, Alarme | ✅ abgeschlossen – 13 von 13 Funktionstests in PLCSIM bestanden ([Testanleitung](docs/Testanleitung.md)) |
| 4 – HMI | Übersicht, Bedienung, Paketdaten, Statistik, Diagnose, Alarme | ⬜ offen |
| 5 – Test | Testfälle, Fehlerfälle, Dokumentation, Release v1.0 | ⬜ offen |

Der aktuelle Arbeitsstand steht im neuesten Plan unter [docs/Planung/](docs/Planung/).

## Dokumentation

- [Einführung](docs/Einfuehrung.md) – das Projekt in einfachen Worten: was die Anlage macht, wie sie getestet und dokumentiert wurde
- [FeatureSpec](docs/FeatureSpec.md) – Ziel, Sortierregeln, Betriebsarten, Programmstruktur, HMI, Testfälle
- [Anlagenkonfiguration](docs/Anlagenkonfiguration.md) – Bandgeometrie, Stationspositionen, I/O-Liste, Zustandsdiagramme, Alarme
- [Programmablaufplan](docs/Programmablauf.md) – Aufrufhierarchie, Ablauf eines Zyklus, Datenfluss, Sensoren und Aktoren, Lebenslauf eines Pakets
