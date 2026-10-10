# Offene Punkte

## OI-001: PLCSIM läuft nicht auf dem Entwicklungs-Laptop

**Status:** Lösung gewählt (Windows-VM bei Microsoft Azure), Einrichtung ausstehend · **Erfasst:** 2026-10-09 · **Blockiert:** Tests ab Phase 3, HMI-Simulation in Phase 4

### Befund

- Laptop: Snapdragon X Plus (ARM64), Windows 11 Home
- TIA Portal V21 läuft unter x64-Emulation: Engineering, Import und Übersetzen funktionieren.
- S7-PLCSIM V21: Jede S7-1500-Instanz stürzt beim Hochfahren ab.
  - Windows-Ereignisprotokoll: `Siemens.Simatic.PlcSim.VplcHost64.exe`, fehlerhaftes Modul `Vplc1500.dll`, Ausnahmecode `0xc0000409`
  - TIA Portal meldet im Dialog „Erweitertes Laden“: *Die gewählte Schnittstelle hat keine Netzwerkverbindung.*
- Siemens unterstützt Windows auf ARM offiziell nicht.

### Verworfen: zweiter Rechner mit Intel-Prozessor (2026-10-09)

Der vorhandene Intel-Rechner (Core i3) ist für TIA Portal V21 mit PLCSIM zu langsam.

### Verworfen: TIA Portal Cloud (Siemens) (2026-10-09)

Die TIA Cloud Services sind laut Nutzungsbedingungen nur für **gewerbliche Nutzung** im Namen einer Firma zugelassen. Für ein privates Lernprojekt nicht zulässig – Bedingungen wurden nicht akzeptiert.

Ursprüngliche Bewertung:

| | |
|---|---|
| Aufwand | gering |
| Angebot | „TIA Portal V21 sofort testen, 21 Tage kostenlos“, Siemens-Beitrag **109772248** (Link auf der Trial-Downloadseite 109989774) |
| Vorteil | läuft auf Siemens-Servern mit Intel/AMD-Hardware, keine Installation |
| Zu prüfen | ob **S7-PLCSIM** und die **WinCC-Runtime-Simulation** in der Cloud enthalten sind |
| Hinweis | Erst aktivieren, wenn getestet werden soll – die 21 Tage laufen ab Aktivierung. Die Quellen aus `src/` lassen sich dort genauso importieren. |

Aus dem Siemens-Beitrag 109772248 (gelesen 2026-10-09):

| Punkt | Bedeutung für uns |
|---|---|
| Aktivierung im TIA Cloud Services Hub: https://tiacloudservices.siemens.com/tia-portal-cloud/trials | Dort steht vermutlich, welche Pakete je Trial-Variante enthalten sind |
| „Hauptpakete von TIA Portal sowie die wichtigsten Optionspakete“ | PLCSIM wird **nicht ausdrücklich** genannt – noch offen |
| Kostenloser Cloud-Speicher (TIA Cloud Storage, 42 GB) | Projektarchiv vom Laptop hochladen und wieder herunterladen |
| Session-Dauer max. **1 Stunde**, Instanz wird danach **gelöscht** | Jede Session startet frisch: Projekt aus dem Cloud-Speicher öffnen, laden, testen. Änderungen vor Ablauf in den Cloud-Speicher sichern. |
| Kein Online-Zugriff auf lokale Hardware | Für uns egal, wir simulieren |
| Nicht in allen Ländern verfügbar: https://tiacloudservices.siemens.com/rolled-out | Prüfen, ob Deutschland freigeschaltet ist |
| Schritt-für-Schritt-Anleitung: Beitrag **109823581**, Applikationshandbuch: Beitrag **110000000** | Dort nach PLCSIM suchen |

### Gewählte Lösung: gemietete Windows-VM bei Microsoft Azure (2026-10-09)

Einrichten erst, wenn alle Bausteine auf dem Laptop fehlerfrei übersetzen – so laufen weder VM-Kosten noch die 21-Tage-Trial unnötig.

| Punkt | Plan |
|---|---|
| Anbieter | **Microsoft Azure** (gewählt 2026-10-09): Windows-Standardfall, Portal auf Deutsch, RDP-Datei per Klick, eingebautes Auto-Shutdown. AWS wäre möglich, ist aber umständlicher (Schlüsselpaar für das Windows-Passwort, Konsole teils nur Englisch). Aktuelle Preise und Startguthaben für Neukunden beim Einrichten prüfen. |
| Image | **Windows Server 2022 Datacenter** – Windows-Lizenz im Preis enthalten (Windows 11 bräuchte in Azure eine eigene, passende Lizenz). Vorher in der Liesmich der TIA-ISO prüfen, ob Windows Server 2022 unterstützt wird. |
| Größe | z. B. **D4s_v5**: 4 vCPU, 16 GB RAM; 128 GB SSD |
| Kostenschutz | **Auto-Shutdown** beim Erstellen aktivieren (z. B. täglich 22:00, VM wird dabei freigegeben) und ein **Budget mit E-Mail-Alarm** anlegen (z. B. 20 €) |
| Zugriff | Remotedesktop (RDP) vom Laptop – läuft auch auf ARM |
| Software | TIA Portal V21 + S7-PLCSIM V21 (ISOs per Download direkt in der VM), eigene 21-Tage-Trial |
| Projekt übertragen | Archiv `.zap21` über OneDrive oder Kopieren per RDP; entpacken in der VM nach `C:\TIA\` |
| Kosten sparen | VM nach jedem Test **stoppen und freigeben** (deallocate) – dann fällt nur der Speicher an |
| Zu prüfen | PLCSIM V21 startet in der VM (virtuelle CPU) – erster Test direkt nach der Installation |

### Weitere Optionen (nicht gewählt)

| Option | Bewertung |
|---|---|
| **Gemietete Windows-VM** mit Intel/AMD-Prozessor (z. B. Microsoft Azure, AWS) | Privat nutzbar, Windows-Lizenz im Mietpreis enthalten. Empfehlung: 4 vCPU, 16 GB RAM, 128 GB SSD. Kosten fallen nur an, solange die VM läuft (nach dem Test **stoppen/freigeben**); dazu ein kleiner Betrag für den Speicher. TIA Portal + PLCSIM dort installieren, eigene 21-Tage-Trial. |
| **Siemens SCE** über eine Bildungseinrichtung | Nur, falls die Weiterbildung über Schule, Hochschule oder Bildungsträger läuft |
| **Leistungsstärkerer Intel/AMD-PC** (geliehen, Kurs, Bekannte) | Keine laufenden Kosten, abhängig von Verfügbarkeit |

### Vorgehen bis zur Lösung

Lokal ohne Simulation weiterarbeiten: Konstanten, UDTs und DBs importieren und übersetzen, Phase-3-Bausteine schreiben und fehlerfrei übersetzen.

## OI-002: TIA Portal Openness auf dem Laptop blockiert

**Status:** zurückgestellt · **Erfasst:** 2026-10-10 · **Blockiert:** nichts (Import und Übersetzen weiter von Hand)

### Ziel

Build-Skript über TIA Portal Openness: Quellen aus `src/` automatisch importieren, übersetzen, Fehler als Text ausgeben.

### Stand

- Openness-DLLs vorhanden: `C:\Program Files\Siemens\Automation\Portal V21\PublicAPI\V21\net48\`
- Benutzer ist in der Gruppe **Siemens TIA Openness** (eingerichtet 2026-10-10)
- Testprogramm [`tools/openness/TiaProbe.cs`](../tools/openness/TiaProbe.cs) übersetzt als x64 mit `tools/openness/build.cmd`
- Ausführung blockiert:
  1. **McAfee** stellt die `.exe` unter Quarantäne → Datei-Ausnahme eingerichtet
  2. **Intelligente App-Steuerung** (Smart App Control) von Windows 11 ist aktiv und blockiert unsignierte Programme. Keine Ausnahmen möglich, nur komplettes Ausschalten – und das ist ohne Neuinstallation nicht umkehrbar. **Nicht ausschalten.**

### Weiteres Vorgehen

In der Azure-VM (OI-001) läuft weder McAfee noch die intelligente App-Steuerung – dort kann Openness erneut getestet werden.

Aufräumen auf dem Laptop: Die McAfee-Ausnahme für `TiaProbe.exe` wird nicht mehr gebraucht und kann entfernt werden.
