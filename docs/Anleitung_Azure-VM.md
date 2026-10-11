# Anleitung: Test-VM in Microsoft Azure

Ziel: Eine Windows-VM mit Intel/AMD-Prozessor, auf der TIA Portal V21 und S7-PLCSIM V21 laufen, um das SPS-Programm zu testen (Hintergrund: [OI-001](OpenIssues.md#oi-001-plcsim-läuft-nicht-auf-dem-entwicklungs-laptop)).

> **Kosten:** Eine laufende VM kostet pro Stunde. Gestoppt (und freigegeben) kosten nur noch Festplatte und öffentliche IP, deutlich weniger. Deshalb: **Budget-Alarm** und **Auto-Shutdown** einrichten und die VM nach jedem Test **beenden**. Aktuelle Preise zeigt Azure beim Anlegen der VM an.
>
> Stand 10.10.2026 (Germany West Central):
>
> | Posten | Kosten ca. | fällt an |
> |---|---|---|
> | VM D4as_v6 inkl. Windows-Lizenz | 0,40 $/Std. | nur während die VM läuft |
> | Standard-SSD 128 GiB | 8–10 $/Monat | immer, auch gestoppt |
> | Öffentliche IP | 3–4 $/Monat | immer, auch gestoppt |
>
> Die Monatspreise im Größen-Auswahldialog gelten für Dauerbetrieb (730 h) – real zählen nur die Laufstunden.

---

## 1. Azure-Konto anlegen

1. https://azure.microsoft.com/de-de/free/ öffnen → **Kostenlos starten** bzw. **Konto erstellen**.
2. Mit einem Microsoft-Konto anmelden (z. B. dem, mit dem du auch Windows nutzt).
3. Angaben ausfüllen, Kreditkarte hinterlegen (Identitätsprüfung). Die aktuellen Bedingungen zu Startguthaben und Abrechnung auf der Seite lesen.
4. Danach öffnet sich das **Azure-Portal**: https://portal.azure.com

## 2. Budget mit E-Mail-Alarm

1. Im Portal oben in die Suche **„Budgets“** eingeben → **Kostenverwaltung + Abrechnung → Budgets**.
2. **Hinzufügen**: Name `TIA-Test`, Zeitraum **monatlich**, Betrag z. B. **20 €**.
3. Warnungen: bei **50 %**, **80 %** und **100 %** eine E-Mail an deine Adresse.

Das Budget stoppt nichts automatisch – es warnt nur. Darum zusätzlich Auto-Shutdown (Schritt 3).

## 3. VM erstellen

Portal → **Virtuelle Computer** → **Erstellen → Virtueller Azure-Computer**.

### Register „Grundlagen“

| Feld | Eingabe |
|---|---|
| Ressourcengruppe | **Neu erstellen:** `rg-tia-test` |
| Name des virtuellen Computers | `vm-tia` |
| Region | **(Europe) Germany West Central** |
| Verfügbarkeitsoptionen | Keine Infrastrukturredundanz erforderlich |
| Sicherheitstyp | VMs mit vertrauenswürdigem Start (Standardwert) |
| Image | **See all images** → Kachel **Windows Server** (Herausgeber Microsoft, *nicht* Drittanbieter-Kacheln mit Aufpreis) → **Windows Server 2022 Datacenter: Azure Edition – x64 Gen 2** (ohne „Core“, „smalldisk“, „Hotpatch“) |
| VM architecture | **x64** |
| Größe | **D4as_v6** (4 vCPU, 16 GiB). Varianten mit 8 GiB (D4als, D4ls) sind zu knapp |
| Mit Azure Spot-Rabatt ausführen | kein Haken (Spot-VMs kann Azure jederzeit abschalten) |
| Benutzername | z. B. `tiaadmin` |
| Kennwort | sicheres Kennwort, notieren |
| Öffentliche Eingangsports | **Ausgewählte Ports zulassen** → **RDP (3389)** |
| Lizenzierung | Haken nicht setzen (Windows-Lizenz ist im Preis enthalten) |

> **„Kontingent reicht nicht aus: Limit für Familie“:** Neue Abos haben für manche VM-Familien 0 vCPUs Kontingent (bei uns DSv5). Dann im Größendialog Filter **vCPUs = 4** setzen und eine Größe außerhalb der Gruppe „Kontingent reicht nicht aus“ wählen – oder unter **Kontingente → Compute** eine Erhöhung beantragen.

> Laut Liesmich der TIA-V21-ISO (`Documents\Readme\Deutsch\de-DE\index.html`) unterstützt TIA Portal V21 **Windows Server 2022 Standard** und **2025 Standard** (jeweils Vollinstallation, nicht Core) sowie den Betrieb als Gast unter **Microsoft Hyper-V** – Azure-VMs laufen auf Hyper-V. Datacenter/Azure Edition ist dasselbe Betriebssystem mit anderer Lizenz. Die PLCSIM-ISO enthält keine eigene Liesmich mit Systemvoraussetzungen.

### Register „Datenträger“

| Feld | Eingabe |
|---|---|
| Verschlüsselung auf dem Host | kein Haken |
| Größe des Betriebssystemdatenträgers | Standardwert des Images (127 GiB) |
| Typ des Betriebssystemdatenträgers | **SSD Standard** (Premium kostet ca. doppelt so viel, auch bei gestoppter VM) |
| Mit VM löschen | Haken |
| Weitere Datenträger | keine |

### Register „Networking“

Standardwerte übernehmen (neues VNet, öffentliche IP `vm-tia-ip`, NIC-Netzwerksicherheitsgruppe Basic, RDP 3389). Zusätzlich:

| Feld | Eingabe |
|---|---|
| Löschen der öffentlichen IP-Adresse und NIC beim Löschen des virtuellen Computers | **Haken setzen** |

Nach dem Erstellen wird der RDP-Zugang auf deine eigene IP-Adresse beschränkt (Schritt 4).

### Register „Verwaltung“

| Feld | Eingabe |
|---|---|
| **Automatisches Herunterfahren aktivieren** | **Ja** |
| Uhrzeit | z. B. **22:00** |
| Zeitzone | **(UTC+01:00) Amsterdam, Berlin, …** |
| Benachrichtigung vor dem Herunterfahren | Ja, an deine E-Mail-Adresse |
| Sicherung, Notfallwiederherstellung | kein Haken (kostet extra; das Projekt liegt als Archiv auf dem Laptop) |

### Register „Überwachung“

Startdiagnose mit verwaltetem Speicherkonto (Standardwert) lassen, sonst nichts aktivieren.

Dann **Überprüfen und erstellen** → Preis prüfen (D4as_v6: 0,404 $/Std.) → **Erstellen**. Die Bereitstellung dauert einige Minuten.

Danach prüfen: VM → **Vorgänge → Automatisches Herunterfahren** ist aktiviert.

## 4. RDP-Zugang absichern

Offenes RDP aus dem ganzen Internet ist ein bekanntes Angriffsziel. Deshalb nur die eigene IP-Adresse zulassen:

1. VM `vm-tia` öffnen → **Netzwerk** (bzw. **Netzwerkeinstellungen**).
2. Eingangsportregel **RDP** anklicken.
3. **Quelle:** *Meine IP-Adresse* → **Speichern**.

Ändert sich deine IP-Adresse (bei vielen Anbietern über Nacht, nach einem Router-Neustart, in einem anderen WLAN), die Regel hier erneut auf „Meine IP-Adresse“ setzen. Erkennbar: RDP verbindet nicht, **Verbinden → Zugriff überprüfen** zeigt keinen grünen Haken. Deshalb nach jedem Start der VM zuerst **Zugriff überprüfen**.

## 5. Verbinden

Die von Azure angebotene RDP-Datei (**Verbinden → RDP-Datei herunterladen**) blockiert Windows Smart App Control, weil sie aus dem Internet stammt. Deshalb die Verbindung selbst anlegen:

1. Azure-Portal → VM → **Verbinden**: öffentliche IP-Adresse der VM ablesen (Stand 10.10.2026: `51.116.181.4`; kann sich nach Stopp/Start ändern). Optional **Zugriff überprüfen** → „Port 3389 ist erreichbar“.
2. Laptop: Startmenü → **Remotedesktopverbindung** → **Optionen einblenden**.
3. **Allgemein:** Computer = IP der VM, Benutzername `.\tiaadmin`.
4. **Lokale Ressourcen → Weitere… → Laufwerke** aufklappen → **Lokaler Datenträger (C:)** anhaken → **OK**. Damit ist das Laptop-Laufwerk in der VM als `\\tsclient\C` erreichbar. Drucker abwählen.
5. **Allgemein → Speichern unter…** → `C:\TIA\vm-tia.rdp`. Diese selbst erzeugte Datei blockiert Smart App Control nicht.
6. **Verbinden** → Kennwort → Zertifikatswarnung „vm-tia“ mit **Ja** bestätigen (selbstsigniertes Zertifikat der neuen VM).

Fehlt `\\tsclient\C` in der VM („The network name cannot be found“), wurde ohne Laufwerksfreigabe verbunden → trennen, Schritt 4 prüfen, neu verbinden.

Die Uhr der VM läuft auf UTC; das Auto-Shutdown rechnet trotzdem in der eingestellten Zeitzone.

## 6. TIA Portal und PLCSIM in der VM installieren

In der VM:

1. Die beiden ISOs übertragen – entweder in der VM neu herunterladen (Siemens-Beitrag 109989774, Anmeldung nötig; schnell) oder vom Laptop kopieren (über den eigenen Upload, dauert entsprechend). Zum Kopieren **nicht den Explorer** verwenden – bei großen Dateien über `\\tsclient` friert die RDP-Sitzung ein. Stattdessen in der VM in PowerShell:

   ```
   robocopy \\tsclient\C\Users\funke\Downloads C:\Install S7-PLCSIM_V21.iso TIA_Portal_STEP7_Safety_WinCC_V21.iso /Z /R:5 /W:10
   ```

   `/Z` setzt nach einem Abbruch an derselben Stelle fort – bei Problemen einfach neu verbinden und denselben Befehl erneut starten. Danach Vollständigkeit prüfen:

   ```
   Get-FileHash C:\Install\*.iso -Algorithm SHA256 | Select-Object Hash, Path
   ```

   | Datei | Bytes | SHA256 |
   |---|---|---|
   | `S7-PLCSIM_V21.iso` | 2730958848 | `E0E72A875B9906E0035D798E5EAEA7ED4FE7FA0B4A0082AD2A278C23DA8F634E` |
   | `TIA_Portal_STEP7_Safety_WinCC_V21.iso` | 8739749888 | `B75C947AE242C626B9C92C7221B3B150AEE562CBCFC2EDCBACC3BC7973E6ACC8` |

2. **TIA Portal:** ISO doppelklicken → `Start.exe` → Komponenten wie auf dem Laptop: **STEP 7 Professional**, **WinCC Basic/Comfort/Advanced** inkl. **Simulation**; Unified, Professional und Projekt-Server abwählen.
3. Neustart.
4. **PLCSIM:** `S7-PLCSIM_V21.iso` → `Start.exe` → nur **S7-PLCSIM** (Advanced abwählen).
5. Neustart.
6. TIA Portal starten → Trial-Lizenz **STEP 7 Professional** aktivieren (eigene 21 Tage in der VM).

## 7. Projekt übertragen

1. **Laptop:** TIA Portal → Projekt `SortingLine` öffnen → **Projekt → Archivieren** → Ziel `C:\TIA\Archiv\SortingLine.zap21`.
2. **VM:** in PowerShell `robocopy \\tsclient\C\TIA\Archiv C:\TIA SortingLine.zap21 /Z` (legt `C:\TIA\` an).
3. **VM:** TIA Portal → **Projekt → Dearchivieren** → Ziel `C:\TIA\`.

## 8. Erster Test: PLCSIM

1. `PLC_SortingLine` markieren → **Online → Simulation → Starten**.
2. Im Dialog **Erweitertes Laden**: **PN/IE** / **PLCSIM** → **Suche starten** → **Laden** → **Alle starten** → **Fertig stellen**.
3. PLCSIM zeigt die CPU in **RUN** → die Testumgebung steht.

Startet die Simulation nicht, das Windows-Ereignisprotokoll prüfen (wie auf dem Laptop, OI-001).

## 9. Nach jedem Test

- TIA Portal: Projekt speichern; wurde in der VM etwas geändert → archivieren und auf den Laptop kopieren.
- Azure-Portal → VM → **Beenden** (Status muss **„Beendet (Zuordnung aufgehoben)“** zeigen – nur dann läuft keine Rechenzeit mehr).

## 10. Nach Projektende

Azure-Portal → **Ressourcengruppen** → `rg-tia-test` → **Ressourcengruppe löschen**. Damit sind VM, Festplatte und Netzwerk weg und es fallen keine Kosten mehr an.
