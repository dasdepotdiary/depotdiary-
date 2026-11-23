"""Taegliches Story-Format "WAS IST HEUTE PASSIERT" -- echte Markt-
/Wirtschafts-Schlagzeilen des Tages (recherchiert, nicht nur Kurszahlen wie
tagesupdate.py). Rein faktisch, keine Bewertung, keine Kaufempfehlung.

Input: Liste von Dicts mit headline, body (1-2 Saetze, reine Fakten).

Aufruf (Prototyp/Test):
  python posts/story_tagesereignisse.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent
NAME = "story_tagesereignisse"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
# v2 (2026-09-16, Nutzer: "Layout ist gleich wie Aktien-Check, mach andere"):
# bewusst helle editorial Optik statt dunkler Karten -- grosse nummerierte
# Schlagzeilen, keine Boxen.
# v3 (2026-09-18, Nutzer: "mach das auf helle Skyline, neues Pexels-Tagesfoto"):
# statt flacher Creme-Flaeche ein echtes Tageslicht-Skyline-Foto (klarer
# blauer Himmel oben, Gebaeude unten) mit einem weissen Verlaufs-Scrim fuer
# Lesbarkeit -- bewusst ANDERES Foto als das Nacht-Skyline-Bild, das schon im
# Vermoegensingenieur-Collab und bei "Damals investiert" verwendet wird.
BG = "#F2F0EA"
SKYLINE_PHOTO = ROOT / "assets" / "downtown_street_still.png"
INK = B.INK
SUBTEXT = B.SUBTEXT
DIVIDER = B.DIVIDER
OCHRE = "#2E86AB"  # sky-blau statt Ochre/Gelb -- Nutzerwunsch 2026-09-18, siehe feedback_depotdiary_design_experimentation
GREEN = B.GREEN

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def slide_tagesereignisse(events):
    """v7 (2026-10-05): depotdiary-Foto-Schema (Skyline-Foto, Verlauf, rotierende
    Akzentfarbe) statt Creme-Flaeche mit Masthead -- Nutzerwunsch "langweilige
    Einfarb-Story-Designs aendern, nimm Skylines". Schnittstelle unveraendert."""
    entries = [{"tag": f"{i:02d}", "headline": e["headline"], "body": e["body"]}
               for i, e in enumerate(events, 1)]
    return S.draw_list_story(
        "tagesereignisse-" + DATE_LABEL, "DER TAG IM RUECKBLICK",
        ["WAS IST HEUTE", "PASSIERT."], entries,
        "Keine Anlageberatung -- nur Ereignisse, die ich mir angeschaut habe.", DATE_LABEL[:6])


def main():
    events = [
        {"headline": "US-Boersen am Montag: S&P 500 +4,73% auf 7.237, Nasdaq +6,51% auf 24.090, Dow Jones +3,01% auf 49.595.",
         "body": "Laut CNN der beste Tag seit April 2025 fuer S&P 500 und Nasdaq. DAX +2,2% auf 25.337, VIX -26% auf 26,6."},
        {"headline": "Nvidia +31,5% auf 165,05 USD.",
         "body": "Laut Berichten hat der Verwaltungsrat Jensen Huang wieder als CEO eingesetzt. Vor einer Woche hatte er das Amt niedergelegt."},
        {"headline": "Abstand zu den Hochs vom 6. Oktober: S&P 500 -7,4%, Nasdaq -12,7%.",
         "body": "Am Freitag lag der S&P 500 noch mehr als 10% unter dem Hoch (Quelle: Yahoo Finance)."},
        {"headline": "Zoom nach Boersenschluss: bereinigter Gewinn je Aktie 1,59 USD, Umsatz 1,29 Mrd. USD.",
         "body": "Erste Quartalsdividende angekuendigt: 0,25 USD je Aktie. Die Aktie lag nachboerslich ungefaehr unveraendert (Schlusskurs 86,03 USD)."},
        {"headline": "HPE: Ausblick naechstes Quartal 1,54-1,57 USD Gewinn je Aktie, Umsatz 8-8,15 Mrd. USD.",
         "body": "Die Aktie schloss +17,4% bei 48,02 USD und lag nachboerslich bei rund 44,7 USD."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
