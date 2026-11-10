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
        {"headline": "US-Boersen am Dienstag: S&P 500 -0,38% auf 7.521, Nasdaq -0,74% auf 25.066, Dow Jones -0,30% auf 52.232.",
         "body": "Der DAX schloss 0,31% im Plus bei 26.347 Punkten."},
        {"headline": "US-Inflation im Oktober: Verbraucherpreise +0,4% zum Vormonat (erwartet +0,3%), Kernrate +0,3% (erwartet +0,2%).",
         "body": "Die Rendite 10-jaehriger US-Staatsanleihen stieg auf rund 4,98%."},
        {"headline": "Nvidia verliert 5,5% auf rund 169 USD.",
         "body": "Am Montag hatte der Verwaltungsrat die Untersuchung zu CEO Jensen Huang bekannt gegeben."},
        {"headline": "Fed-Gouverneur Waller hatte laut Berichten gesagt, bei einer Kerninflation ab 0,3% sei eine Zinsanhebung um 0,5 Punkte zu erwaegen.",
         "body": "Die naechste Zinsentscheidung der Fed steht am 9. Dezember an."},
        {"headline": "Gold -1,86% auf 4.038 USD, Bitcoin -1,7% auf 73.920 USD.",
         "body": "Der Oelpreis (WTI) lag stabil bei rund 86 USD."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
