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
| Förderband   | 10 m, konstant 0,5 m/s, Start/Stopp, Störung, virtuelle Paketposition |
| Paketabstand | mindestens 1,5 m (3 s) |
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
| ST6     | Sortierstrecke: Sortierer Q1–Q3, Ausschuss am Bandende |

Stationen heißen `ST1`–`ST6`, damit sie nicht mit den Sensorkennungen `S1`–`S16` verwechselt werden. Positionen, Sensoren und Zeiten stehen in der [Anlagenkonfiguration](Anlagenkonfiguration.md).

## 4. Werkstück / Paket

Datentyp `UDT_Workpiece`, gehalten in einem Array `Packages[1..5]`:

| Feld     | Typ (Vorschlag) | Wertebereich                     |
|----------|-----------------|----------------------------------|
| ID       | DINT            | fortlaufend, eindeutig           |
| Position | REAL            | 0–100 %                          |
| Size     | Enum/INT        | Klein / Groß                     |
| Material | Enum/INT        | Metall / Kunststoff              |
| Weight   | REAL            | 0,2–8,0 kg                       |
| Quality  | BOOL            | TRUE = OK, FALSE = Ausschuss     |
| Target   | Enum/INT        | Ausgang 1–4                      |
| Status   | Enum/INT        | siehe Abschnitt 8                |

Ein eigenes Geschwindigkeitsfeld je Paket entfällt: Das Band läuft mit konstanter Geschwindigkeit, die Position ergibt sich daraus.

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

## 6. Sensoren

Vollständige Liste mit Typ, Signal und Adresse: [Anlagenkonfiguration, Abschnitt 3 und 5](Anlagenkonfiguration.md#3-sensoren).

Kurzfassung: S1–S6 an den Stationen, S4 als analoge Waage, S7–S10 an den Ausgängen, S11–S16 als Endlagen der Sortierer, dazu B1 Not-Halt und B2 Motorschutz.

## 7. Aktoren

| Kennung | Funktion                                     |
|---------|----------------------------------------------|
| M1      | Förderbandmotor                              |
| Q1      | Sortierer 1 (Pneumatikzylinder, Ausgang 1)   |
| Q2      | Sortierer 2 (Pneumatikzylinder, Ausgang 2)   |
| Q3      | Sortierer 3 (Pneumatikzylinder, Ausgang 3)   |
| H1      | Betriebsleuchte                              |
| H2      | Störungsleuchte                              |

Ausgang 4 (Ausschuss) liegt am Bandende und braucht keinen Aktor. Alles, was nicht ausgeschleust wird, landet dort (Fail-safe).

## 8. Paketstatus statt globaler Schrittkette

Weil bis zu fünf Pakete gleichzeitig unterwegs sind, gibt es **keine** globale Schrittkette für die Anlage. Jedes Paket hat seinen eigenen Status, der sich aus seiner Position und den passierten Stationen ergibt.

| Status     | Bedeutung                                   |
|------------|---------------------------------------------|
| EMPTY      | Platz im Array frei                         |
| WAITING    | erzeugt, noch nicht auf dem Band            |
| MOVING     | wird transportiert                          |
| DETECTED   | an ST1 erkannt                              |
| INSPECTION | durchläuft ST2–ST5                          |
| SORTING    | Ziel bestimmt, auf der Sortierstrecke       |
| SORTED     | an Ausgang 1–3 angekommen                   |
| REJECTED   | an Ausgang 4 angekommen                     |
| ERROR      | Paketverfolgung verloren                    |

Zustandsdiagramme für Pakete und Anlage: [Anlagenkonfiguration, Abschnitt 6 und 7](Anlagenkonfiguration.md#6-anlagenzustand).

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
      ├── FB_InputMapping – Eingänge aus %I oder Simulation nach DB_IO
      ├── FB_Simulation   – Paketerzeugung (Zufall / manuell), simulierte Sensoren
      ├── FB_Conveyor     – Band, Positionsfortschritt aller Pakete
      ├── FB_Workpiece    – Paketstatus je Array-Eintrag
      ├── FB_Detection    – Stationen ST1–ST5
      ├── FB_Sorting      – Zielbestimmung, Sortierer an ST6
      ├── FB_Counters     – Statistik
      ├── FB_Alarms       – Störungen
      └── FB_OutputMapping – DB_IO nach %Q

OB30 (100 ms) – Positionsfortschritt der Pakete und Simulationstakt
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

Alarmliste mit Auslöser und Reaktion: [Anlagenkonfiguration, Abschnitt 8](Anlagenkonfiguration.md#8-alarme). Für Tests lassen sich Störungen in der Simulation gezielt auslösen (Abschnitt 9 dort).

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
| 010  | Sortierer blockiert (simuliert)       | Alarm, Band stoppt    |
| 011  | Sortierer klemmt beim Zurückfahren    | Alarm, Band stoppt    |
| 012  | Lichtschranke S6 defekt (simuliert)   | Paket → ERROR, Band stoppt |
| 013  | Not-Halt                              | Band aus, Sortierer fahren zurück |

## 14. Offene Punkte

- **CPU-Typ:** S7-1200 oder S7-1500. Hängt von der TIA-Portal-Lizenz ab (STEP 7 Basic oder Professional). Die I/O-Adressen passen auf beide.
