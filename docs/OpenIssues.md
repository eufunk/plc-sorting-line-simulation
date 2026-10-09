# Offene Punkte

## OI-001: PLCSIM läuft nicht auf dem Entwicklungs-Laptop

**Status:** Lösung gewählt (Intel-Rechner), Umsetzung läuft · **Erfasst:** 2026-10-09 · **Blockiert:** Tests ab Phase 3, HMI-Simulation in Phase 4

### Befund

- Laptop: Snapdragon X Plus (ARM64), Windows 11 Home
- TIA Portal V21 läuft unter x64-Emulation: Engineering, Import und Übersetzen funktionieren.
- S7-PLCSIM V21: Jede S7-1500-Instanz stürzt beim Hochfahren ab.
  - Windows-Ereignisprotokoll: `Siemens.Simatic.PlcSim.VplcHost64.exe`, fehlerhaftes Modul `Vplc1500.dll`, Ausnahmecode `0xc0000409`
  - TIA Portal meldet im Dialog „Erweitertes Laden“: *Die gewählte Schnittstelle hat keine Netzwerkverbindung.*
- Siemens unterstützt Windows auf ARM offiziell nicht.

### Gewählte Lösung: zweiter Rechner mit Intel-Prozessor (2026-10-09)

- **Laptop:** Repository, Quellen schreiben, in TIA importieren und übersetzen, Projekt archivieren (*Projekt → Archivieren*)
- **Intel-Rechner (Core i3):** TIA Portal V21 + S7-PLCSIM V21, archiviertes Projekt dearchivieren und testen
- Systemvoraussetzungen des Intel-Rechners noch zu prüfen (RAM, SSD, Windows-Edition)
- S7-PLCSIM V21 auf dem Laptop deinstalliert (2026-10-09). TIA Portal, Automation License Manager und Npcap bleiben installiert.

### Ausweichoption: TIA Portal Cloud (Siemens)

| | |
|---|---|
| Aufwand | gering |
| Angebot | „TIA Portal V21 sofort testen, 21 Tage kostenlos“, Siemens-Beitrag **109772248** (Link auf der Trial-Downloadseite 109989774) |
| Vorteil | läuft auf Siemens-Servern mit Intel/AMD-Hardware, keine Installation |
| Zu prüfen | ob **S7-PLCSIM** und die **WinCC-Runtime-Simulation** in der Cloud enthalten sind |
| Hinweis | Erst aktivieren, wenn getestet werden soll – die 21 Tage laufen ab Aktivierung. Die Quellen aus `src/` lassen sich dort genauso importieren. |

Weitere Alternativen, falls die Cloud nicht passt: anderer PC mit Intel/AMD-Prozessor, oder gemietete Windows-VM (Azure, AWS).

### Vorgehen bis zur Lösung

Lokal ohne Simulation weiterarbeiten: Konstanten, UDTs und DBs importieren und übersetzen, Phase-3-Bausteine schreiben und fehlerfrei übersetzen.
