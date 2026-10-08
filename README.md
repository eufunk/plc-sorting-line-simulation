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
| 2 – Datenmodell | UDTs und Datenbausteine | ⬜ offen |
| 3 – SPS | Simulation, Förderband, Erkennung, Sortierung, Betriebsarten, Alarme | ⬜ offen |
| 4 – HMI | Übersicht, Bedienung, Paketdaten, Statistik, Diagnose, Alarme | ⬜ offen |
| 5 – Test | Testfälle, Fehlerfälle, Dokumentation, Release v1.0 | ⬜ offen |

Der aktuelle Arbeitsstand steht im neuesten Plan unter [docs/Planung/](docs/Planung/).

## Dokumentation

- [FeatureSpec](docs/FeatureSpec.md) – Ziel, Sortierregeln, Betriebsarten, Programmstruktur, HMI, Testfälle
- [Anlagenkonfiguration](docs/Anlagenkonfiguration.md) – Bandgeometrie, Stationspositionen, I/O-Liste, Zustandsdiagramme, Alarme
