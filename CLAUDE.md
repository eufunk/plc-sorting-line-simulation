# CLAUDE.md

## Git-Regeln

- **Commit** nur nach umfangreichen Änderungen – keine Commits für Kleinigkeiten.
- **Push** erst, wenn ein Thema abgeschlossen ist, das im aktuellen Plan unter `docs/Planung/` als erledigt markiert wurde.

## TIA Portal und Repository

- Das TIA-Portal-Projekt liegt **außerhalb** des Repositorys und außerhalb von OneDrive (z. B. `C:\TIA\SortingLine\`).
- Ins Repository kommen nur exportierte Textquellen unter `src/`: SCL-Bausteine (`.scl`), UDTs (`.udt`), Datenbausteine (`.db`) und PLC-Konstanten (`.csv`).
- Änderungen werden zwischen TIA-Projekt und `src/` per Export/Import der Quellen übertragen.

## Planung (`docs/Planung/`)

- Jeden Tag wird ein neuer Plan angelegt: `docs/Planung/Plan_JJJJ-MM-TT.md`.
- Die fachliche Spezifikation steht in `docs/FeatureSpec.md`.
- Der Plan vom Vortag wird als **erledigt** markiert.
- Bausteine aus dem alten Plan, die noch nicht erledigt waren, werden in den neuen Plan übernommen.
