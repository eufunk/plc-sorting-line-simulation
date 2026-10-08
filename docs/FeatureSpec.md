# FeatureSpec – Förderband-Sortieranlage

## 1. Ziel

Eine simulierte Förderbandanlage transportiert Pakete, erkennt ihre Eigenschaften und sortiert sie automatisch auf vier Ausgänge. Die Steuerung wird vollständig in SCL (Siemens S7, TIA Portal) umgesetzt und über ein HMI bedient und visualisiert. Es wird keine echte Hardware benötigt – alle Sensoren und Pakete werden in der SPS simuliert.

## 2. Anlagenkonzept (festgelegt)

| Bereich      | Festlegung |
|--------------|------------|
| Pakete       | max. 5 gleichzeitig auf dem Band, jedes mit eindeutiger ID |
| Material     | Metall / Kunststoff |
| Größe        | Klein / Groß |
| Gewicht      | 0,2–8,0 kg |
| Qualität     | OK / Ausschuss |
| Förderband   | konstante Geschwindigkeit, Start/Stopp, Störung, virtuelle Paketposition |
| Simulation   | Zufallsgenerierung, manuelle Paketerzeugung über HMI, einstellbare Erzeugungsrate |
| Steuerung    | Zustand je Paket statt einer globalen Schrittkette |

## 3. Anlagenaufbau

```
┌─────────┐   ┌───────────┐   ┌──► Ausgang 1 – Metall
│ Einlauf │──►│Förderband ├───┼──► Ausgang 2 – Kunststoff klein
└─────────┘   └───────────┘   ├──► Ausgang 3 – Kunststoff groß
                              └──► Ausgang 4 – Ausschuss
```

### Stationen entlang des Bandes

Die Stationen sind **ortsabhängig**: Jede Station liegt an einer festen Position auf dem Band und wirkt auf das Paket, das sich gerade dort befindet.

```
 Einlauf
    ↓
 ═══╪═════════╪═════════╪═════════╪═════════╪═════════╪══════════►
   ST1       ST2       ST3       ST4       ST5       ST6
 Erkennung   Größe    Material  Gewicht   Qualität  Sortierung
                                                       │
                              ┌──────────┬─────────────┼──────────┐
                              ↓          ↓             ↓          ↓
                          Ausgang 1  Ausgang 2     Ausgang 3  Ausgang 4
```

| Station | Aufgabe                                   |
|---------|-------------------------------------------|
| ST1     | Paket am Einlauf erkannt, ID vergeben     |
| ST2     | Größe klein / groß bestimmen              |
| ST3     | Material Metall / Kunststoff bestimmen    |
| ST4     | Gewicht prüfen                            |
| ST5     | Qualität prüfen, Ziel festlegen           |
| ST6     | Sortierer betätigen, Paket ausleiten      |

Stationen heißen `ST1`–`ST6`, damit sie nicht mit den Sensorkennungen `S1`–`S10` verwechselt werden. Positionen der Stationen in % werden mit der I/O-Liste festgelegt.

## 4. Werkstück / Paket

Datentyp `UDT_Workpiece`, gehalten in einem Array `Packages[1..5]`:

| Feld     | Typ (Vorschlag) | Wertebereich                     |
|----------|-----------------|----------------------------------|
| ID       | DINT            | fortlaufend, eindeutig           |
| Position | REAL            | 0–100 %                          |
| Speed    | REAL            | Bandgeschwindigkeit (konstant)   |
| Size     | Enum/INT        | Klein / Groß                     |
| Material | Enum/INT        | Metall / Kunststoff              |
| Weight   | REAL            | 0,2–8,0 kg                       |
| Quality  | BOOL            | TRUE = OK, FALSE = Ausschuss     |
| Target   | Enum/INT        | Ausgang 1–4                      |
| Status   | Enum/INT        | siehe Abschnitt 8                |

## 5. Sortierregeln

Ein Paket ist **Ausschuss**, wenn die Qualitätsprüfung „Ausschuss“ ergibt **oder** das Gewicht außerhalb von 0,5–5,0 kg liegt.

| Gewicht      | Bewertung              |
|--------------|------------------------|
| < 0,5 kg     | zu leicht → Ausschuss  |
| 0,5–5,0 kg   | OK                     |
| > 5,0 kg     | zu schwer → Ausschuss  |

Die Regeln werden in dieser Reihenfolge geprüft, die erste zutreffende gilt:

| Priorität | Bedingung                     | Ziel                          |
|-----------|-------------------------------|-------------------------------|
| 1         | Ausschuss (Qualität/Gewicht)  | Ausgang 4 – Ausschuss         |
| 2         | Material = Metall             | Ausgang 1 – Metall            |
| 3         | Kunststoff und klein          | Ausgang 2 – Kunststoff klein  |
| 4         | Kunststoff und groß           | Ausgang 3 – Kunststoff groß   |
| 5         | sonst (ungültig)              | Ausgang 4 – Ausschuss         |

```
WeightOk := Weight >= 0.5 AND Weight <= 5.0;

IF NOT Quality OR NOT WeightOk THEN
    Target := REJECT;
ELSIF Material = METAL THEN
    Target := METAL;
ELSIF Material = PLASTIC AND Size = SMALL THEN
    Target := PLASTIC_SMALL;
ELSIF Material = PLASTIC AND Size = LARGE THEN
    Target := PLASTIC_LARGE;
ELSE
    Target := REJECT;
END_IF;
```

## 6. Sensoren (virtuell)

| Kennung | Funktion            |
|---------|---------------------|
| S1      | Paket am Einlauf    |
| S2      | Position erreicht   |
| S3      | Höhe / Größe        |
| S4      | Metall erkannt      |
| S5      | Qualitätsprüfung    |
| S6      | Sortierposition     |
| S7      | Paket Ausgang 1     |
| S8      | Paket Ausgang 2     |
| S9      | Paket Ausgang 3     |
| S10     | Paket Ausschuss     |

Zusätzliche Signale: Not-Halt, Förderband-Störung, Sortierer-Störung.

## 7. Aktoren

| Kennung | Funktion                                     |
|---------|----------------------------------------------|
| M1      | Förderbandmotor                              |
| Q1      | Sortierer 1 (Pneumatikzylinder, Ausgang 1)   |
| Q2      | Sortierer 2 (Pneumatikzylinder, Ausgang 2)   |
| Q3      | Sortierer 3 (Pneumatikzylinder, Ausgang 3)   |
| Q4      | Ausschussklappe (Ausgang 4)                  |
| H1      | Betriebsleuchte                              |
| H2      | Störungsleuchte                              |

## 8. Paketstatus statt globaler Schrittkette

Weil bis zu fünf Pakete gleichzeitig unterwegs sind, gibt es **keine** globale Schrittkette für die Anlage. Jedes Paket hat seinen eigenen Status, der sich aus seiner Position und den passierten Stationen ergibt.

| Status     | Bedeutung                                   |
|------------|---------------------------------------------|
| WAITING    | erzeugt, noch nicht auf dem Band            |
| MOVING     | wird transportiert                          |
| DETECTED   | an ST1 erkannt, ID vergeben                 |
| INSPECTION | durchläuft ST2–ST5                          |
| SORTING    | an ST6, Sortierer wird betätigt             |
| SORTED     | an Ausgang 1–3 angekommen                   |
| REJECTED   | an Ausgang 4 angekommen                     |

Beispiel zu einem Zeitpunkt:

```
Paket 101 → ST4
Paket 102 → ST2
Paket 103 → ST1
```

Der Anlagenzustand (Betriebsart, Band läuft, Störung, Not-Halt) wird getrennt vom Paketstatus geführt.

## 9. Betriebsarten

### Automatik
Start → Pakete erzeugen → Transport → Stationen ST1–ST5 → Sortierung an ST6 → Zähler erhöhen → Platz im Array wird frei.

### Handbetrieb
Der Bediener steuert am HMI einzeln:
- Förderband EIN/AUS
- Sortierer 1, 2, 3
- Ausschussklappe
- Paket erzeugen

### Simulation
Im HMI umschaltbar zwischen zwei Modi:

**Automatisch** – zufällige Pakete mit einstellbarer Erzeugungsrate (Vorschlag: alle 3 s). Pseudozufallswerte in der SPS für Material, Größe, Gewicht (0,2–8,0 kg) und Qualität.

**Manuell** – gezielte Testpakete:

```
Material:   [Metall ▼]
Größe:      [Groß ▼]
Gewicht:    [4,5 kg]
Qualität:   [OK ▼]

            [Paket erzeugen]
```

In beiden Modi wird kein neues Paket erzeugt, solange bereits fünf Pakete aktiv sind.

## 10. Programmstruktur (SCL)

```
                FB_Main
                   │
        ┌──────────┴──────────┐
        │                     │
   Anlagensteuerung      Paketsimulation
        │                     │
   Förderband            Packages[1..5]
        │                     │
   Sortierer             Eigenschaften
        │                     │
        └──────────┬──────────┘
                   │
                HMI / DB
```

Zuordnung zu Bausteinen:

```
OB1
 └── FB_Main
      ├── FB_Simulation   – Paketerzeugung (Zufall / manuell)
      ├── FB_Conveyor     – Band, Positionsfortschritt aller Pakete
      ├── FB_Workpiece    – Paketstatus je Array-Eintrag
      ├── FB_Detection    – Stationen ST1–ST5
      ├── FB_Sorting      – Zielbestimmung, Sortierer an ST6
      ├── FB_Counters     – Statistik
      └── FB_Alarms       – Störungen
```

Datentypen: `UDT_Workpiece`, `UDT_Conveyor`, `UDT_Sorter`, `UDT_Alarm`, `UDT_Statistics` sowie die zugehörigen Instanz- und Datenbausteine.

## 11. HMI

| Bild | Name       | Inhalt |
|------|------------|--------|
| 1    | Übersicht  | Anlagenbild mit Band, Paketen und Ausgängen, Betriebsart, Bandstatus, Anzahl aktiver Pakete, Tasten START / STOPP / RESET / HAND-AUTO |
| 2    | Paketdaten | Tabelle aller aktiven Pakete: ID, Größe, Material, Gewicht, Qualität, Ziel, Position, Status |
| 3    | Statistik  | Gesamt, je Ausgang, Gutteile, Ausschussquote, Zykluszeit |
| 4    | Diagnose   | Sensoren, Aktoren, Band- und Sortiererstatus, Simulationsmodus und manuelle Paketerzeugung |
| 5    | Alarme     | Alarmliste |

## 12. Alarme

- Förderband blockiert
- Sortierer nicht zurückgefahren
- Paket nicht erkannt
- Timeout
- Not-Halt
- Sensorfehler

## 13. Testfälle

Die Testfälle 001–009 werden über die manuelle Paketerzeugung angestoßen.

| Test | Eingang                               | Erwartetes Ergebnis   |
|------|---------------------------------------|-----------------------|
| 001  | Metall, klein, 2 kg, OK               | Ausgang 1             |
| 002  | Metall, groß, 2 kg, OK                | Ausgang 1             |
| 003  | Kunststoff, klein, 2 kg, OK           | Ausgang 2             |
| 004  | Kunststoff, groß, 2 kg, OK            | Ausgang 3             |
| 005  | beliebig, Qualität Ausschuss          | Ausgang 4             |
| 006  | beliebig, OK, 0,3 kg                  | Ausgang 4 (zu leicht) |
| 007  | beliebig, OK, 6,0 kg                  | Ausgang 4 (zu schwer) |
| 008  | beliebig, OK, 0,5 kg bzw. 5,0 kg      | nach Material/Größe (Grenzwerte gelten als OK) |
| 009  | 6. Paket bei 5 aktiven Paketen        | wird nicht erzeugt    |
| 010  | Sortierer blockiert                   | Störung, Band stoppt  |
| 011  | Not-Halt                              | Anlage stoppt         |

## 14. Offene Punkte

- **Konkrete Anlagenkonfiguration:** Positionen der Stationen ST1–ST6 und der Sensoren auf dem Band, Abstände, Bandlänge und Geschwindigkeit.
- **Sensorliste angleichen:** Die Sensoren S1–S10 stammen aus dem ersten Entwurf. Für die Gewichtsstation ST4 fehlt noch ein Sensor (Waage).
- **I/O-Liste:** Adressen der virtuellen Sensoren und Aktoren.
- **Speed im Paket:** Bei konstanter Bandgeschwindigkeit ist `Speed` pro Paket redundant. Klären, ob das Feld bleibt (z. B. für spätere Staustrecken) oder entfällt.
- **Mindestabstand:** Wie nah dürfen zwei Pakete aufeinander folgen? Davon hängt ab, ob ein Sortierer schon zurückgefahren ist, wenn das nächste Paket kommt.
