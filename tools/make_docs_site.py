"""Erzeugt aus docs/*.md, den Tagesplänen und den Quellen unter src/ eine einzelne
HTML-Seite mit der gesamten Projektdokumentation.

Aufruf:  python tools/make_docs_site.py [Zieldatei] [--offline]
  --offline: Diagramm-Bibliothek einbetten, damit die Datei ohne Internet läuft
Standard-Ziel: C:\\TIA\\Doku\\Sortieranlage_Doku.html (außerhalb des Repositorys)
"""

import base64
import csv
import html
import re
import sys
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DelphiLexer

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
SRC = REPO / "src"
DEFAULT_TARGET = Path(r"C:\TIA\Doku\Sortieranlage_Doku.html")

# Abschnitte der Seite: (id, Navigationstitel, Quelle)
SECTIONS = [
    ("start", "Überblick", REPO / "README.md"),
    ("spezifikation", "Spezifikation", DOCS / "FeatureSpec.md"),
    ("anlage", "Anlagenkonfiguration", DOCS / "Anlagenkonfiguration.md"),
    ("programm", "Programm", SRC / "README.md"),
    ("test", "Test", DOCS / "Testanleitung.md"),
    ("hmi", "Bedienpanel", DOCS / "HMI.md"),
    ("umgebung", "Testumgebung", DOCS / "Anleitung_Azure-VM.md"),
    ("offen", "Offene Punkte", DOCS / "OpenIssues.md"),
    ("verlauf", "Projektverlauf", None),
]
DOC_TO_SECTION = {src.name: sid for sid, _, src in SECTIONS if src}
DOC_TO_SECTION["README.md"] = "start"


def slug(text):
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def img_data_uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def code_blocks():
    """Alle Quellbausteine: Name -> (Ordner, Datei, Titel, Kopfkommentar, HTML-Code, Zeilen)."""
    blocks = {}
    for folder in ["OB", "FB", "FC", "UDT", "DB"]:
        for f in sorted((SRC / folder).glob("*.*")):
            text = f.read_text(encoding="utf-8")
            title = re.search(r"^TITLE = (.*)$", text, re.M)
            comment = []
            for line in text.splitlines()[1:]:
                if line.startswith("//"):
                    comment.append(line[2:].strip())
                elif comment and not line.startswith("//"):
                    break
            code = highlight(text, DelphiLexer(), HtmlFormatter(nowrap=True))
            blocks[f.stem] = (folder, f.name, title.group(1) if title else "", comment, code,
                              len(text.splitlines()))
    return blocks


BLOCKS = code_blocks()


def rewrite_links(html_text, section_id):
    """Links auf andere Dokumente und Quellen auf Abschnitte der Seite umbiegen."""
    def repl(m):
        href = m.group(1)
        if href.startswith("http"):
            return f'href="{href}" target="_blank" rel="noopener"'
        path, _, anchor = href.partition("#")
        name = Path(path).name if path else ""
        stem = Path(path).stem if path else ""
        if not path:
            return f'href="#{section_id}" data-anchor="{section_id}--{anchor}"'
        if name in DOC_TO_SECTION:
            sid = DOC_TO_SECTION[name]
            target = f"{sid}--{anchor}" if anchor else ""
            return f'href="#{sid}" data-anchor="{target}"'
        if name.startswith("Plan_"):
            return f'href="#verlauf" data-anchor="plan-{stem}"'
        if stem in BLOCKS:
            return f'href="#programm" data-anchor="code-{stem}"'
        if stem in ("Constants", "IoTags"):
            return f'href="#programm" data-anchor="ordner-{"Constants" if stem == "Constants" else "Tags"}"'
        folder = path.rstrip("/").split("/")[-1]
        if folder in FOLDERS:
            return f'href="#programm" data-anchor="ordner-{folder}"'
        if path.rstrip("/").endswith(("Planung", "Planung/")):
            return 'href="#verlauf"'
        return 'href="#programm"'
    return re.sub(r'href="([^"]*)"', repl, html_text)


def md_to_html(text, section_id):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": lambda v, s: f"{section_id}--{slug(v)}"}})
    out = md.convert(text)
    # Mermaid-Diagramme rendert die Seite selbst
    out = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                 lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', out, flags=re.S)
    # Tabellen und Code horizontal scrollbar machen
    out = out.replace("<table>", '<div class="scroll"><table>').replace("</table>", "</table></div>")
    out = re.sub(r"<pre><code", '<pre class="code"><code', out)
    return rewrite_links(out, section_id)


def strip_first_h1(text):
    return re.sub(r"\A\s*# .*\n", "", text, count=1)


# Ordner unter src/: Überschrift und kurze Erklärung im Abschnitt "Programm"
FOLDERS = {
    "Constants": ("PLC-Konstanten", "Anwenderkonstanten: Codes für Zustände und Ziele, Positionen am Band, Zeiten und Grenzwerte. Angelegt per Excel-Import."),
    "UDT": ("Datentypen", "PLC-Datentypen: Aufbau von Paket, Sortierer, Förderband, Alarmen, Statistik und Ein-/Ausgangsabbild."),
    "DB": ("Datenbausteine", "Globale Datenbausteine mit dem Zustand der Anlage. IDB_Main ist der Instanz-Datenbaustein von FB_Main."),
    "Tags": ("E/A-Variablen", "PLC-Variablen mit Hardware-Adressen (%I, %IW, %Q) – die Ein-/Ausgangsliste der Anlage."),
    "FC": ("Funktionen", "Funktionen ohne eigenes Gedächtnis: Zufallszahlen, Testprotokoll, Anzeigewerte für das Bedienpanel."),
    "FB": ("Funktionsbausteine", "Funktionsbausteine mit eigenen Instanzdaten: Simulation, Steuerlogik und automatischer Testablauf."),
    "OB": ("Organisationsbausteine", "Einstiegspunkte des Betriebssystems: OB30 ruft im 100-ms-Takt FB_Main auf, OB1 bleibt leer."),
}
CSV_FILES = {
    "Constants": (SRC / "Constants" / "Constants.csv", ["Name", "Datentyp", "Wert", "Kommentar"]),
    "Tags": (SRC / "Tags" / "IoTags.csv", ["Name", "Datentyp", "Adresse", "Kommentar"]),
}


def section_program():
    intro = md_to_html(strip_first_h1((SRC / "README.md").read_text(encoding="utf-8")), "programm")
    # Ordnernamen in der Übersichtstabelle verlinken
    for folder in FOLDERS:
        intro = intro.replace(f"<td><code>{folder}/</code></td>",
                              f'<td><a class="folder-link" href="#programm" data-anchor="ordner-{folder}">'
                              f'<code>{folder}/</code></a></td>')
    parts = [intro, '<h2 id="programm--bausteine">Ordner und Bausteine</h2>']
    back = '<p class="back"><a href="#programm" data-anchor="">↑ zur Ordnerübersicht</a></p>'
    for folder, (label, text) in FOLDERS.items():
        if folder in CSV_FILES:
            path, cols = CSV_FILES[folder]
            with open(path, encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f, delimiter=";"))
            body = "".join("<tr>" + "".join(f"<td>{html.escape(r[c])}</td>" for c in cols) + "</tr>" for r in rows)
            head = "".join(f"<th>{c}</th>" for c in cols)
            parts.append(f'<div class="folder" id="ordner-{folder}"><h3><code>src/{folder}/</code> {label} '
                         f'<span class="count">{len(rows)} Einträge</span></h3><p class="fdesc">{text}</p>'
                         f'<details class="block" open><summary><span class="bname">{path.name}</span>'
                         f'<span class="btitle">{label}</span><span class="blines">{len(rows)} Einträge</span></summary>'
                         f'<div class="scroll"><table class="data"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
                         f'</details>{back}</div>')
            continue
        items = [(n, b) for n, b in BLOCKS.items() if b[0] == folder]
        parts.append(f'<div class="folder" id="ordner-{folder}"><h3><code>src/{folder}/</code> {label} '
                     f'<span class="count">{len(items)} Dateien</span></h3><p class="fdesc">{text}</p>')
        for name, (_, fname, title, comment, code, lines) in items:
            desc = html.escape(" ".join(comment[:3]))
            parts.append(
                f'<details class="block" id="code-{name}"><summary>'
                f'<span class="bname">{html.escape(name)}</span>'
                f'<span class="btitle">{html.escape(title)}</span>'
                f'<span class="blines">{lines} Zeilen</span></summary>'
                f'<p class="bdesc">{desc}</p>'
                f'<pre class="code src"><code>{code}</code></pre></details>')
        parts.append(back + "</div>")
    return "\n".join(parts)


def section_history():
    plans = sorted((DOCS / "Planung").glob("Plan_*.md"), reverse=True) + \
            sorted((DOCS / "Planung" / "Archiv").glob("Plan_*.md"), reverse=True)
    parts = ['<p class="lead">Jeden Arbeitstag gibt es einen Plan. Erledigtes wird abgehakt, Offenes in den nächsten Plan übernommen, der alte Plan wandert ins Archiv.</p>']
    for i, p in enumerate(plans):
        text = p.read_text(encoding="utf-8")
        date = p.stem.replace("Plan_", "")
        status = "offen" if "**Status:** offen" in text else "erledigt"
        body = md_to_html(strip_first_h1(text), f"plan-{date}")
        parts.append(f'<details class="block plan" id="plan-{p.stem}"{" open" if i == 0 else ""}><summary>'
                     f'<span class="bname">{date}</span><span class="btitle">Tagesplan</span>'
                     f'<span class="pill {status}">{status}</span></summary><div class="plan-body">{body}</div></details>')
    return "\n".join(parts)


def section_start():
    text = strip_first_h1((REPO / "README.md").read_text(encoding="utf-8"))
    body = md_to_html(text, "start")
    figs = (f'<div class="figs"><figure><img src="{img_data_uri(DOCS / "img" / "hmi_uebersicht.png")}" '
            f'alt="Übersichtsbild des Bedienpanels in der Simulation: fünf Pakete auf dem Band, Zustand AUTOMATIK">'
            f'<figcaption>Bedienpanel TP1200 Comfort in der Runtime-Simulation</figcaption></figure>'
            f'<figure><img src="{img_data_uri(DOCS / "img" / "plcsim_run.png")}" '
            f'alt="S7-PLCSIM V21 mit der CPU PLC_SortingLine im Zustand RUN">'
            f'<figcaption>S7-PLCSIM V21: die simulierte CPU in RUN</figcaption></figure></div>')
    return body + figs


def build():
    nav, sections = [], []
    for sid, label, src in SECTIONS:
        nav.append(f'<a href="#{sid}" data-sec="{sid}">{label}</a>')
        if sid == "start":
            content = section_start()
        elif sid == "programm":
            content = section_program()
        elif sid == "verlauf":
            content = section_history()
        else:
            content = md_to_html(strip_first_h1(src.read_text(encoding="utf-8")), sid)
        sections.append(f'<section class="doc" id="{sid}"><p class="eyebrow">{label}</p>'
                        f'<h1>{label if sid != "start" else "Förderband-Sortieranlage"}</h1>{content}</section>')
    stats = {
        "SCL-Zeilen": sum(b[5] for n, b in BLOCKS.items() if b[0] in ("OB", "FB", "FC")),
        "Bausteine": sum(1 for b in BLOCKS.values() if b[0] in ("OB", "FB", "FC")),
        "Datentypen": sum(1 for b in BLOCKS.values() if b[0] == "UDT"),
        "Tests bestanden": "13/13",
    }
    stat_html = "".join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for k, v in stats.items())
    return TEMPLATE.replace("{{NAV}}", "\n".join(nav)).replace("{{SECTIONS}}", "\n".join(sections)) \
                   .replace("{{STATS}}", stat_html)


TEMPLATE = r"""<title>Sortieranlage Dokumentation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: feste Seitenleiste wie ein Schaltschrank-Register, rechts eine Lesespalte; oben ein Band mit Stationsmarken */
:root {
  --bg: #F3F4F0; --surface: #FBFBF8; --ink: #14212E; --text: #34414D; --muted: #64707C;
  --line: #D8DCD4; --accent: #0B7372; --accent-soft: #DCEBEA; --signal: #A9580D; --signal-soft: #F6E7D6;
  --code-bg: #EBEDE7; --k: #0B5F8A; --c: #6B7A6B; --s: #9A4A0B; --n: #7A3FA0;
  --f-display: "IBM Plex Sans Condensed", "Arial Narrow", Arial, sans-serif;
  --f-body: "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
  --f-mono: "IBM Plex Mono", Consolas, "Courier New", monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0F1821; --surface: #15212C; --ink: #E8EDEF; --text: #C3CED6; --muted: #8B99A5;
  --line: #263646; --accent: #4FC1BF; --accent-soft: #163A3E; --signal: #F0A050; --signal-soft: #3A2A18;
  --code-bg: #0B131A; --k: #7CC4F0; --c: #7F8F86; --s: #F0B07A; --n: #C9A2E6; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0F1821; --surface: #15212C; --ink: #E8EDEF; --text: #C3CED6; --muted: #8B99A5;
  --line: #263646; --accent: #4FC1BF; --accent-soft: #163A3E; --signal: #F0A050; --signal-soft: #3A2A18;
  --code-bg: #0B131A; --k: #7CC4F0; --c: #7F8F86; --s: #F0B07A; --n: #C9A2E6; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font: 16px/1.6 var(--f-body); }
a { color: var(--accent); }
a:focus-visible, summary:focus-visible { outline: 2px solid var(--signal); outline-offset: 2px; }
.shell { display: grid; grid-template-columns: 250px minmax(0, 1fr); min-height: 100vh; }
.side { position: sticky; top: env(safe-area-inset-top, 0px); align-self: start; height: 100vh; overflow-y: auto;
  background: var(--ink); color: var(--bg); padding-block: 28px; padding-inline: 20px; display: flex; flex-direction: column; gap: 20px; }
.brand { font: 600 22px/1.15 var(--f-display); color: var(--bg); letter-spacing: .01em; }
.brand small { display: block; font: 400 13px/1.4 var(--f-mono); color: color-mix(in srgb, var(--bg) 65%, transparent); margin-top: 6px; letter-spacing: .04em; text-transform: uppercase; }
nav { display: flex; flex-direction: column; gap: 2px; }
nav a { color: color-mix(in srgb, var(--bg) 78%, transparent); text-decoration: none; padding: 7px 10px; border-radius: 4px; font: 500 15px/1.3 var(--f-body); display: flex; gap: 10px; align-items: baseline; }
nav a::before { content: attr(data-tag); font: 500 11px var(--f-mono); color: color-mix(in srgb, var(--bg) 45%, transparent); width: 30px; flex: none; }
nav a:hover { background: color-mix(in srgb, var(--bg) 10%, transparent); color: var(--bg); }
nav a.active { background: var(--accent); color: #F3F4F0; }
nav a.active::before { color: #F3F4F0; }
.side-foot { margin-top: auto; font: 12px/1.5 var(--f-mono); color: color-mix(in srgb, var(--bg) 55%, transparent); }
main { min-width: 0; padding-block: 0 80px; padding-inline: 48px; }
.belt { position: relative; height: 66px; margin-inline: -48px; margin-bottom: 36px; background: var(--surface); border-bottom: 1px solid var(--line); }
.belt .track { position: absolute; left: 48px; right: 48px; top: 40px; height: 8px; border-radius: 4px; background: var(--ink); }
.belt .st { position: absolute; top: 12px; transform: translateX(-50%); font: 500 11px var(--f-mono); color: var(--muted); }
.belt .st::after { content: ""; position: absolute; left: 50%; top: 18px; width: 2px; height: 10px; background: var(--muted); }
.belt .st.q { color: var(--signal); }
.belt .st.q::after { background: var(--signal); }
.belt .pkg { position: absolute; top: 32px; width: 16px; height: 12px; border-radius: 2px; background: var(--accent); animation: run 18s linear infinite; }
@keyframes run { from { left: 48px; } to { left: calc(100% - 64px); } }
@media (prefers-reduced-motion: reduce) { .belt .pkg { animation: none; left: 30%; } }
.doc { max-width: 920px; }
.doc[hidden] { display: none; }
.eyebrow { font: 500 12px var(--f-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 6px; }
h1 { font: 600 44px/1.08 var(--f-display); color: var(--ink); margin: 0 0 24px; text-wrap: balance; }
h2 { font: 600 28px/1.2 var(--f-display); color: var(--ink); margin: 44px 0 12px; padding-top: 14px; border-top: 1px solid var(--line); text-wrap: balance; }
h3 { font: 600 20px/1.3 var(--f-display); color: var(--ink); margin: 28px 0 8px; }
h4 { font: 600 16px/1.4 var(--f-body); color: var(--ink); margin: 20px 0 6px; }
p, li { max-width: 72ch; }
.lead { font-size: 18px; color: var(--ink); }
code { font: 14px var(--f-mono); background: var(--code-bg); padding: 1px 5px; border-radius: 3px; }
pre.code { background: var(--code-bg); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; overflow-x: auto; font: 13.5px/1.55 var(--f-mono); }
pre.code code { background: none; padding: 0; font: inherit; }
pre.mermaid { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px; overflow-x: auto; text-align: center; }
.scroll { overflow-x: auto; margin: 14px 0; }
table { border-collapse: collapse; font-size: 15px; min-width: 50%; }
th { text-align: left; font: 600 13px/1.3 var(--f-body); text-transform: uppercase; letter-spacing: .05em; color: var(--muted); border-bottom: 2px solid var(--ink); padding: 8px 12px; }
td { border-bottom: 1px solid var(--line); padding: 8px 12px; vertical-align: top; font-variant-numeric: tabular-nums; }
table.data td:first-child { font-family: var(--f-mono); font-size: 13.5px; white-space: nowrap; }
blockquote { margin: 16px 0; padding: 10px 16px; background: var(--signal-soft); border-left: 3px solid var(--signal); color: var(--ink); }
blockquote p { margin: 6px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 32px 0; }
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin: 0 0 28px; }
.stat { background: var(--surface); padding: 14px 16px; display: flex; flex-direction: column; gap: 2px; }
.stat b { font: 600 30px/1 var(--f-display); color: var(--ink); font-variant-numeric: tabular-nums; }
.stat span { font: 12px var(--f-mono); color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
.figs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; margin-top: 32px; }
figure { margin: 0; }
figure img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--ink); display: block; }
figcaption { font: 13px var(--f-mono); color: var(--muted); margin-top: 6px; }
details.block { border: 1px solid var(--line); border-radius: 6px; background: var(--surface); margin: 8px 0; }
details.block summary { cursor: pointer; list-style: none; display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: baseline; padding: 10px 14px; }
details.block summary::-webkit-details-marker { display: none; }
details.block summary::before { content: "▸"; color: var(--accent); width: 10px; }
details.block[open] summary::before { content: "▾"; }
.bname { font: 500 15px var(--f-mono); color: var(--ink); }
.btitle { color: var(--text); flex: 1; min-width: 12ch; }
.blines { font: 12px var(--f-mono); color: var(--muted); }
.bdesc { margin: 0 14px 10px; color: var(--muted); font-size: 14.5px; }
details.block pre.code { margin: 0 14px 14px; }
.plan-body { padding: 0 18px 12px; }
.plan-body h2 { font-size: 22px; margin-top: 24px; }
.count { font: 12px var(--f-mono); color: var(--muted); font-weight: 400; }
.folder { margin-top: 28px; padding-top: 4px; scroll-margin-top: 16px; }
.folder h3 { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline; }
.folder h3 code { font-size: 15px; background: var(--accent-soft); color: var(--accent); }
.fdesc { color: var(--muted); margin: 0 0 10px; }
.folder.flash { animation: flash 1.6s ease-out; }
@keyframes flash { from { background: var(--accent-soft); } to { background: transparent; } }
@media (prefers-reduced-motion: reduce) { .folder.flash { animation: none; } }
.folder-link { text-decoration: none; }
.folder-link code { color: var(--accent); border-bottom: 1px dashed var(--accent); }
.folder-link:hover code { background: var(--accent-soft); }
.back { margin: 6px 0 0; font-size: 14px; }
.back a { text-decoration: none; }
.pill { font: 500 11px var(--f-mono); text-transform: uppercase; letter-spacing: .06em; padding: 2px 8px; border-radius: 10px; }
.pill.erledigt { background: var(--accent-soft); color: var(--accent); }
.pill.offen { background: var(--signal-soft); color: var(--signal); }
.code .k, .code .kd, .code .kr, .code .kt, .code .nb { color: var(--k); font-weight: 500; }
.code .c, .code .c1, .code .cm { color: var(--c); font-style: italic; }
.code .s, .code .s1, .code .s2, .code .sa { color: var(--s); }
.code .mi, .code .mf, .code .m, .code .mh { color: var(--n); }
.theme-btn { background: none; border: 1px solid color-mix(in srgb, var(--bg) 30%, transparent); color: var(--bg); font: 12px var(--f-mono); padding: 6px 10px; border-radius: 4px; cursor: pointer; align-self: start; }
@media (max-width: 900px) {
  .shell { grid-template-columns: minmax(0, 1fr); }
  .side { position: sticky; height: auto; z-index: 5; padding-block: 12px; padding-inline: 16px; gap: 10px; }
  .brand small, .side-foot, .theme-btn { display: none; }
  nav { flex-direction: row; overflow-x: auto; gap: 4px; }
  nav a { white-space: nowrap; }
  nav a::before { display: none; }
  main { padding-inline: 16px; }
  .belt { margin-inline: -16px; }
  .belt .track { left: 16px; right: 16px; }
  .belt .st { display: none; }
  h1 { font-size: 34px; }
  .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .figs { grid-template-columns: minmax(0, 1fr); }
}
</style>
<div class="shell">
  <aside class="side">
    <div class="brand">Förderband-<br>Sortieranlage<small>S7-1500 · SCL · WinCC</small></div>
    <nav id="nav">
{{NAV}}
    </nav>
    <button class="theme-btn" id="theme" type="button">Hell / Dunkel</button>
    <div class="side-foot">TIA Portal V21<br>S7-PLCSIM V21<br>TP1200 Comfort</div>
  </aside>
  <main>
    <div class="belt" aria-hidden="true">
      <div class="track"></div>
      <span class="st" style="left:calc(48px + (100% - 96px) * .02)">ST1</span>
      <span class="st" style="left:calc(48px + (100% - 96px) * .15)">ST2</span>
      <span class="st" style="left:calc(48px + (100% - 96px) * .25)">ST3</span>
      <span class="st" style="left:calc(48px + (100% - 96px) * .35)">ST4</span>
      <span class="st" style="left:calc(48px + (100% - 96px) * .45)">ST5</span>
      <span class="st" style="left:calc(48px + (100% - 96px) * .55)">S6</span>
      <span class="st q" style="left:calc(48px + (100% - 96px) * .65)">Q1</span>
      <span class="st q" style="left:calc(48px + (100% - 96px) * .75)">Q2</span>
      <span class="st q" style="left:calc(48px + (100% - 96px) * .85)">Q3</span>
      <span class="pkg"></span>
    </div>
    <div class="stats" id="stats">{{STATS}}</div>
{{SECTIONS}}
  </main>
</div>
<script>
(function () {
  var tags = { start: "00", spezifikation: "01", anlage: "02", programm: "03", test: "04", hmi: "05", umgebung: "06", offen: "07", verlauf: "08" };
  var links = document.querySelectorAll("#nav a");
  links.forEach(function (a) { a.setAttribute("data-tag", tags[a.dataset.sec] || ""); });
  var stats = document.getElementById("stats");
  function show(id, anchor) {
    var sec = document.getElementById(id);
    if (!sec || !sec.classList.contains("doc")) { id = "start"; sec = document.getElementById(id); }
    document.querySelectorAll("section.doc").forEach(function (s) { s.hidden = s !== sec; });
    links.forEach(function (a) { a.classList.toggle("active", a.dataset.sec === id); });
    stats.hidden = id !== "start";
    var target = anchor ? document.getElementById(anchor) : null;
    if (target) {
      if (target.tagName === "DETAILS") target.open = true;
      var parent = target.closest("details"); if (parent) parent.open = true;
      target.scrollIntoView({ block: "start" });
      if (target.classList.contains("folder")) {
        target.classList.remove("flash"); void target.offsetWidth; target.classList.add("flash");
      }
    } else { window.scrollTo(0, 0); }
    // Offline-Fassung: Diagramme erst zeichnen, wenn ihr Abschnitt sichtbar ist
    if (window.mermaid && sec.querySelector("pre.mermaid:not([data-processed])")) {
      window.mermaid.run({ querySelector: "#" + id + " pre.mermaid:not([data-processed])" });
    }
    try { localStorage.setItem("doku-sec", id); } catch (e) {}
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href^='#']");
    if (!a) return;
    e.preventDefault();
    var id = a.getAttribute("href").slice(1);
    show(id, a.dataset.anchor || "");
    if (history.replaceState) history.replaceState(null, "", "#" + id);
  });
  var start = (location.hash || "").slice(1);
  if (!start) { try { start = localStorage.getItem("doku-sec") || ""; } catch (e) {} }
  show(start || "start", "");
  document.getElementById("theme").addEventListener("click", function () {
    var root = document.documentElement;
    var dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
  });
})();
</script>
"""


MERMAID_LIB = Path(r"C:\TIA\Doku\lib\mermaid-10.9.1.min.js")


def offline(page):
    """Diagramm-Bibliothek in die Seite packen, damit sie ohne Internet läuft
    (auf claude.ai zeichnet der Viewer die Diagramme selbst)."""
    if not MERMAID_LIB.exists():
        sys.exit(f"Fehlt: {MERMAID_LIB} – einmalig von "
                 "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js herunterladen")
    lib = MERMAID_LIB.read_text(encoding="utf-8").replace("</script", "<\\/script")
    init = ('<script>mermaid.initialize({ startOnLoad: false, theme: '
            'matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default" });</script>')
    page = page.replace("<script>\n(function () {", f"<script>{lib}</script>\n{init}\n<script>\n(function () {{", 1)
    # Als eigenständige Datei braucht die Seite ein vollständiges HTML-Gerüst (auf claude.ai ergänzt es der Viewer)
    head, _, body = page.partition("</style>")
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'{head}body {{ margin: 0; }}\n</style>\n</head>\n<body>{body}</body>\n</html>\n')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else DEFAULT_TARGET
    page = build()
    if "--offline" in sys.argv:
        page = offline(page)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    print(f"{len(SECTIONS)} Abschnitte, {len(BLOCKS)} Bausteine -> {target} ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
