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
        {"headline": "US-Boersen am Dienstag: S&P 500 -1,03% auf 7.341, Nasdaq -0,74% auf 24.328, Dow Jones -1,64% auf 50.759.",
         "body": "Der DAX schloss 2,08% im Minus bei 26.045 Punkten, der Angstindex VIX stieg um 11% auf 25,5."},
        {"headline": "US-Einzelhandelsumsaetze Oktober: +0,2% zum Vormonat.",
         "body": "Das entsprach der Erwartung (September: +0,8%). Ohne Autos, Benzin, Baumaterial und Gastronomie: +0,6%."},
        {"headline": "Home Depot -2,4%, Disney -1,5%, JD.com -7,7% am Berichtstag.",
         "body": "Home Depot: bereinigter Gewinn je Aktie 3,86 USD, Umsatz 43,4 Mrd. USD. Disney: 1,77 USD, Umsatz 25,95 Mrd. USD."},
        {"headline": "Nvidia nach Boersenschluss: Umsatz 115,8 Mrd. USD, Gewinn je Aktie 2,68 USD (bereinigt).",
         "body": "Der Konsens lag bei 2,49 USD. Ausblick fuers naechste Quartal: rund 130 Mrd. USD Umsatz (+/-3%)."},
        {"headline": "Nvidia-Aktie nachboerslich rund +3% auf etwa 160 USD.",
         "body": "Schlusskurs im regulaeren Handel: 155,46 USD (-0,4%). Quellen: Unternehmensmitteilung, Yahoo Finance."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
