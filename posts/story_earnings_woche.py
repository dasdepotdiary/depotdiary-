"""Woechentliches Story-Format "EARNINGS-WOCHE" -- alle Berichtstermine der
Woche auf EINER Slide (Nutzerwunsch 2026-09-22: "alle infos auf eine slide
und als story", kein mehrseitiges Karussell mehr fuer dieses Format).
Layout/Aufbau uebernommen von story_tagesereignisse.py (nummerierte Liste,
Zeitungs-Masthead), nur Titel und Inhalt sind Earnings-spezifisch.

Input: Liste von Dicts mit headline, body (1-2 Saetze, reine Fakten,
keine Kursziele/Bewertungen).

Aufruf:
  python posts/story_earnings_woche.py <post_name>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent

W, H = B.STORY_SIZE
BG = "#F2F0EA"
INK = B.INK
SUBTEXT = B.SUBTEXT
DIVIDER = B.DIVIDER
ACCENT = B.GREEN
MASTHEAD_H = 340
INK_DARK = "#16181C"


def slide_earnings_woche(events, date_label):
    """v2 (2026-10-05): depotdiary-Foto-Schema (Skyline-Foto, Glas-Karte, rotierende
    Akzentfarbe) statt Creme-Flaeche mit Masthead. Schnittstelle unveraendert."""
    entries = [{"tag": f"{i:02d}", "headline": e["headline"], "body": e["body"]}
               for i, e in enumerate(events, 1)]
    return S.draw_list_story(
        "earnings-" + date_label, "DIE WOCHE IM UEBERBLICK",
        ["EARNINGS-", "WOCHE."], entries,
        "Keine Anlageberatung -- nur Zahlen/Fakten, die ich mir angeschaut habe.", date_label[:6])


EVENTS = [
    {"headline": "General Mills -- Mittwoch, 23.9., vor US-Boersenoeffnung.",
     "body": "Kurs 35,41 USD (21.9.), Marktkap. 18,9 Mrd. USD. Analysten rechnen mit rund 0,72 USD Gewinn je Aktie."},
    {"headline": "Cracker Barrel -- Mittwoch, 23.9., vor US-Boersenoeffnung.",
     "body": "Kurs 44,87 USD (21.9.), Marktkap. 1,0 Mrd. USD. Analysten rechnen mit rund 0,20 USD Gewinn je Aktie."},
    {"headline": "Costco -- Donnerstag, 24.9., nach US-Boersenschluss.",
     "body": "Kurs 898,48 USD (21.9.), Marktkap. 420,3 Mrd. USD. Analysten rechnen mit rund 6,48 USD Gewinn je Aktie."},
]


def main():
    post_name = sys.argv[1] if len(sys.argv) > 1 else "earnings_woche_2026-09-21"
    date_label = sys.argv[2] if len(sys.argv) > 2 else "21.09.2026"
    output = ROOT / "output" / post_name
    tt_dir = output / "tiktok_9x16"
    tt_dir.mkdir(parents=True, exist_ok=True)

    # Optionales Input-JSON posts/inputs/<post_name>.json: {"events": [...]}
    input_path = ROOT / "posts" / "inputs" / f"{post_name}.json"
    events = EVENTS
    if input_path.exists():
        events = json.loads(input_path.read_text(encoding="utf-8"))["events"]

    img = slide_earnings_woche(events, date_label)
    img.save(tt_dir / "slide_1.png")
    img.save(output / "uebersicht.png")
    print(f"Fertig: {output / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
