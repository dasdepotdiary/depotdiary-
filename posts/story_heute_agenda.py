"""Taegliches Morgen-Story-Format "WAS STEHT HEUTE AN" -- Gegenstueck zu
story_tagesereignisse.py (das ist der Abend-Rueckblick, das hier ist der
Morgen-Ausblick): recherchierte Termine/Ereignisse, die HEUTE anstehen
(Zentralbank-Termine, bekannte Earnings, ggf. eigene Posts des Tages als
Cross-Promo). Rein faktisch, keine Prognosen/Kursziele.

Eigene visuelle Identitaet: Morgendaemmerungs-Verlauf (warmes Orange oben,
tiefes Navy unten) statt der bisherigen Paletten (Schwarz/Creme/Bordeaux/Gruen).

Input: Liste von Dicts mit time (str, z.B. "HEUTE" oder "09:00"), headline,
body (1 Satz).

Aufruf (Prototyp/Test):
  python posts/story_heute_agenda.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

NAME = "story_heute_agenda"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
DAWN_TOP = (232, 148, 82)
DAWN_MID = (94, 74, 110)
DAWN_BOTTOM = (18, 20, 42)
INK = "#FBF3EA"
SUBTEXT = "#C9C3D8"
GOLD = "#F2B872"
CARD = "#22203A"
CARD_BORDER = "#3A3660"
DIVIDER = "#3A3660"

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def slide_agenda(items):
    """v3 (2026-10-05): depotdiary-Foto-Schema (Skyline-Foto, Verlauf, rotierende
    Akzentfarbe) statt Morgenroete-Verlauf. Schnittstelle unveraendert."""
    entries = [{"tag": it["time"], "headline": it["headline"], "body": it["body"]} for it in items]
    return S.draw_list_story(
        "agenda-" + DATE_LABEL, "TAGES-AGENDA",
        ["WAS STEHT", "HEUTE AN."], entries,
        "Keine Anlageberatung -- nur Termine, die ich mir angeschaut habe.", DATE_LABEL[:6])


def main():
    items = [
        {"time": "VOR US-BOERSENSTART", "headline": "Home Depot, Disney und JD.com legen Zahlen vor.",
         "body": "Konsens-Schaetzung Gewinn je Aktie: Home Depot 3,87 USD, Disney 1,67 USD, JD.com 0,88 USD."},
        {"time": "14:30 UHR", "headline": "US-Einzelhandelsumsaetze fuer Oktober.",
         "body": "Erwartet wird laut Vorschauen ein Plus von 0,2% zum Vormonat (September: +0,8%)."},
        {"time": "NACH BOERSENSCHLUSS", "headline": "Nvidia berichtet erstmals seit dem Ruecktritt von CEO Jensen Huang.",
         "body": "Konsens-Schaetzung Gewinn je Aktie: 2,49 USD."},
    ]
    img = slide_agenda(items)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
