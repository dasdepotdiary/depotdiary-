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
from story_aktiencheck import font

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


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


MASTHEAD_H = 340
INK_DARK = "#16181C"


def draw_masthead(img):
    """v6 (2026-09-18): kein Foto mehr (drei Versuche verworfen), aber die
    reine Creme-Flaeche fand der Nutzer "etwas fad" -- stattdessen ein
    dunkles Zeitungs-Masthead oben (analog echter Zeitungs-Kopfzeilen) fuer
    mehr visuellen Kontrast, darunter die gewohnte Creme-Flaeche."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MASTHEAD_H], fill=INK_DARK)
    return draw


def draw_header(draw, y):
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + DATE_LABEL, font=eyebrow_font, fill="#9B9587")
    y += 44
    title_font = font(B.SERIF_BOLD, 56)
    draw.text((B.MARGIN_LEFT, y), "Was ist heute", font=title_font, fill="#F5F2EA")
    y += 66
    draw.text((B.MARGIN_LEFT, y), "passiert.", font=title_font, fill="#F5F2EA")
    y += 78
    draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=OCHRE)
    return y + 46


def draw_event_entry(draw, x, y, w, num, event):
    num_font = font(B.SERIF_BOLD, 44)
    num_text = f"{num:02d}"
    draw.text((x, y), num_text, font=num_font, fill=OCHRE)
    nw = draw.textlength(num_text, font=num_font)
    text_x = x + nw + 32

    headline_font = font(B.SANS_BOLD, 27)
    body_font = font(B.SANS_BOLD, 20)
    headline_lines = wrap_text(draw, event["headline"], headline_font, w - nw - 32)
    body_lines = wrap_text(draw, event["body"], body_font, w - nw - 32)

    ty = y - 2
    for line in headline_lines:
        draw.text((text_x, ty), line, font=headline_font, fill=INK)
        ty += 34
    ty += 8
    for line in body_lines:
        draw.text((text_x, ty), line, font=body_font, fill=SUBTEXT)
        ty += 27

    entry_h = max(52, ty - y)
    return entry_h


def slide_tagesereignisse(events):
    img = Image.new("RGB", (W, H), BG)
    draw = draw_masthead(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=OCHRE)

    header_end_y = draw_header(draw, 56)
    header_end_y = max(header_end_y, MASTHEAD_H + 40)
    entry_gap = 44
    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    heights = []
    tmp = Image.new("RGB", (10, 10))
    tmp_draw = ImageDraw.Draw(tmp)
    for i, event in enumerate(events, 1):
        num_font = font(B.SERIF_BOLD, 44)
        nw = tmp_draw.textlength(f"{i:02d}", font=num_font)
        headline_lines = wrap_text(tmp_draw, event["headline"], font(B.SANS_BOLD, 27), content_w - nw - 32)
        body_lines = wrap_text(tmp_draw, event["body"], font(B.SANS_BOLD, 20), content_w - nw - 32)
        heights.append(max(52, len(headline_lines) * 34 + 8 + len(body_lines) * 27))
    block_h = sum(heights) + entry_gap * (len(events) - 1)
    footer_top = H - 140
    y = header_end_y + max(30, (footer_top - header_end_y - block_h) // 2)
    for i, event in enumerate(events, 1):
        entry_h = draw_event_entry(draw, B.MARGIN_LEFT, y, content_w, i, event)
        y += entry_h + entry_gap / 2
        if i < len(events):
            draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=DIVIDER, width=1)
        y += entry_gap / 2

    text = "Keine Anlageberatung -- nur Ereignisse, die ich mir angeschaut habe."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=DIVIDER, width=1)
    draw.text((B.MARGIN_LEFT, H - 68), text, font=disclaimer_font, fill=SUBTEXT)

    return img


def main():
    events = [
        {"headline": "Freitag: Dow -0,18%, S&P 500 +0,2%, Nasdaq +0,7%.",
         "body": "Gemischter Wochenschluss -- fuer den Dow war es die dritte Verlustwoche in Folge."},
        {"headline": "Rekordverdaechtiger 'Triple Witching': rund 7 Billionen USD an Optionen liefen aus.",
         "body": "Der zweitgroesste Verfallstermin der Geschichte -- Options-, Futures- und Aktienkontrakte laufen gleichzeitig aus."},
        {"headline": "Verlierer des Tages: IBM -3,2%, Disney -2,7%, Nike -2,3%.",
         "body": "Drei grosse Namen mit deutlichen Abschlaegen zum Wochenschluss."},
        {"headline": "Gewinner des Tages: Amgen +1,5%, Nvidia +1,3%, Caterpillar +1,2%.",
         "body": "Auf der anderen Seite legten diese drei Standardwerte zu."},
        {"headline": "10-Jahres-Rendite zieht wieder an.",
         "body": "Anhaltende Unsicherheit ueber die Oelversorgung aus dem Nahen Osten trieb Treibstoff- und Gaspreise -- und damit die Rendite -- nach oben."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
