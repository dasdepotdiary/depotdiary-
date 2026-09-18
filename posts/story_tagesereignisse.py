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
SKYLINE_PHOTO = ROOT / "assets" / "skyline_day_still.png"
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


def draw_header(draw, y):
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + DATE_LABEL, font=eyebrow_font, fill=SUBTEXT)
    y += 44
    title_font = font(B.SERIF_BOLD, 56)
    draw.text((B.MARGIN_LEFT, y), "Was ist heute", font=title_font, fill=INK)
    y += 66
    draw.text((B.MARGIN_LEFT, y), "passiert.", font=title_font, fill=INK)
    y += 78
    draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=OCHRE)
    return y + 50


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


def skyline_day_background():
    img = Image.open(SKYLINE_PHOTO).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H))
    # Weisser Verlaufs-Scrim von unten (staerker, wo der Text steht) fuer
    # Lesbarkeit -- oberer Himmelsbereich bleibt weitgehend klar sichtbar.
    scrim = Image.new("L", (W, H), 0)
    sdraw = ImageDraw.Draw(scrim)
    for yy in range(H):
        t = yy / H
        alpha = int(max(0, (t - 0.28)) / 0.72 * 235)
        sdraw.line([(0, yy), (W, yy)], fill=min(235, alpha))
    white = Image.new("RGB", (W, H), (255, 255, 255))
    img = Image.composite(white, img, scrim)
    return img


def slide_tagesereignisse(events):
    img = skyline_day_background()
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=OCHRE)

    header_end_y = draw_header(draw, 70)
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
        {"headline": "Bank of Japan hebt Leitzins auf 1,25% an.",
         "body": "Der Schritt kommt einen Tag nach der Fed-Zinserhoehung und beeinflusst weltweit die Erwartungen an die Geldpolitik."},
        {"headline": "S&P 500 und Nasdaq 100 hatten ihren besten Tag seit Anfang August.",
         "body": "Die Rallye setzte sich in Asien fort -- der MSCI-Asien-Index stieg um 0,8%."},
        {"headline": "Micron-Aktie springt um weitere 5,5% auf 977,50 USD.",
         "body": "Nach dem Kurssprung vom Vortag geht die Rallye bei Speicherchip-Werten weiter."},
        {"headline": "Samsung und SK Hynix legen deutlich zu.",
         "body": "Die asiatischen Chiphersteller profitieren von einem optimistischen Ausblick von Nvidia."},
        {"headline": "Ein Stratege empfiehlt, wieder etwas in Anleihen umzuschichten.",
         "body": "Nach der Fed-Zinserhoehung rät Chef-Aktienstratege Julian Emanuel zu etwas mehr Balance zwischen Aktien und festverzinslichen Wertpapieren."},
    ]
    img = slide_tagesereignisse(events)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
