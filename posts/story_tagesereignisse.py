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
        {"headline": "US-Boersen am Dienstag: S&P 500 -0,50% auf 7.201, Nasdaq -1,48% auf 23.734, Dow Jones +0,85% auf 50.019.",
         "body": "Der Dow schloss ueber 50.000 Punkten. Der DAX verlor 1,3% auf 25.018. Laut Berichten fiel der Halbleiter-Index um 7,9%."},
        {"headline": "Nvidia -5,9% auf 155,38 USD.",
         "body": "Am Montag hatte die Aktie nach der Rueckkehr von Jensen Huang als CEO 31,5% zugelegt."},
        {"headline": "US-Verbrauchervertrauen im November: 103,3 Punkte.",
         "body": "Erwartet worden waren laut Berichten 92,2 Punkte (Conference Board)."},
        {"headline": "Dell nach Boersenschluss: Umsatz 54,9 Mrd. USD (+103%), bereinigter Gewinn je Aktie 9,45 USD.",
         "body": "Die Jahresprognose wurde auf rund 202 Mrd. USD Umsatz angehoben. Die Aktie schloss vor der Meldung bei 295,28 USD (-11,8%)."},
        {"headline": "Workday und Autodesk legen Zahlen vor und heben Prognosen an.",
         "body": "Workday: Umsatz 2,705 Mrd. USD (+11,2%). Autodesk: Umsatz 2,16 Mrd. USD (+17%), nachboerslich laut Bericht -3,6%."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
