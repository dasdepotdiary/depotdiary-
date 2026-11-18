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
        {"headline": "US-Boersen am Mittwoch: S&P 500 -0,23% auf 7.324, Nasdaq +0,42% auf 24.430, Dow Jones -1,11% auf 50.198.",
         "body": "Der DAX schloss 1,19% im Minus bei 25.736 Punkten, der Angstindex VIX sank um 3,5% auf 24,6."},
        {"headline": "Fed-Protokoll: Fast alle Teilnehmer hielten weitere Zinsanhebungen fuer wahrscheinlich angemessen.",
         "body": "Der Leitzins blieb im Oktober bei 3,75-4%. Viele nannten den KI-Ausbau als Inflationsrisiko (laut Berichten zum Protokoll)."},
        {"headline": "Lowe's +1,0%, Target +4,0%, TJX +8,0% am Berichtstag.",
         "body": "Bereinigter Gewinn je Aktie: Lowe's 3,10 USD, Target 2,65 USD, TJX 1,34 USD. Lowe's und Target nennen Einmaleffekte aus Zoll-Rueckerstattungen."},
        {"headline": "Disney +4,6%, Nvidia -2,9% auf 150,96 USD.",
         "body": "Nvidia gab damit den nachboerslichen Anstieg vom Dienstag wieder ab (Schlusskurs Dienstag: 155,46 USD)."},
        {"headline": "Palo Alto Networks nach Boersenschluss: Umsatz 3,44 Mrd. USD (+39%).",
         "body": "Die Umsatzprognose fuers Gesamtjahr wurde angehoben. Die Aktie lag nachboerslich bei rund 366 USD (Schlusskurs 339,92 USD)."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
