"""Portfolio-Update mit transparenten Prozentzahlen -- Allokation nach
Anlageklasse + Top-Positionen, aus den echten (selbst gepflegten) Depot-
Daten unter data/depot_2026-08.json / data/holdings_2026-08.json.

Reine Offenlegung der eigenen Aufteilung -- keine Kursziele, keine Kauf-/
Verkaufsempfehlung (siehe CLAUDE.md-Regel). Selbe visuelle Familie wie
posts/personal_portfolio_update.py (DEPOT-UPDATE, dunkles Creme/Gold).

Aufruf:
  python posts/personal_portfolio_percent_update.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "personal_portfolio_percent_update"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

BG = "#14120F"
CARD = "#211E19"
CARD_BORDER = "#3A352C"
CREAM = "#F2F0EA"
MUTED = "#9B9587"
GOLD = "#C9A24B"

OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "DEPOT-UPDATE"

# Feste Kategorie-Reihenfolge + eigene Farbe je Kategorie (kategorial, nicht zyklisch)
CATEGORY_COLORS = {
    "Einzelaktien": "#C9A24B",
    "ETFs & Fonds": "#4E8C6E",
    "Bitcoin & BTC-Treasuries": "#D98A3D",
    "Gold & Silber": "#B7B1A4",
    "Cash": "#6E645A",
}

DATA = json.loads((ROOT / "data" / "depot_2026-08.json").read_text(encoding="utf-8"))
STAND = "14.08.2026"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build_header(draw, subtitle=SERIES_TITLE):
    y = 40
    handle_font = font(B.SANS_BOLD, 19)
    title_font = font(B.SANS_BOLD, 21)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=GOLD)
    y += 30
    draw.text((B.MARGIN_LEFT, y), subtitle, font=title_font, fill=CREAM)
    y += 32
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 22


def draw_disclaimer(draw, text="Keine Anlageberatung -- nur, wie ich selbst aufgestellt bin."):
    disclaimer_font = font(B.SANS_BOLD, 24)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    dy = H - 40 - 32 * len(lines)
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 32


def slide_intro():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    build_header(draw, subtitle="NEUE FOLGE")
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    y = 420
    draw.text((B.MARGIN_LEFT, y), "Portfolio-Update.", font=font(B.SANS_BOLD, 58), fill=CREAM)
    y += 78
    draw.text((B.MARGIN_LEFT, y), "Wie ich aktuell aufgestellt bin --", font=font(B.SANS_BOLD, 30), fill=GOLD)
    y += 40
    draw.text((B.MARGIN_LEFT, y), "mit echten Prozentzahlen.", font=font(B.SANS_BOLD, 30), fill=GOLD)
    y += 56
    draw.text((B.MARGIN_LEFT, y), f"Stand: {STAND}", font=font(B.SANS_BOLD, 22), fill=MUTED)

    draw_disclaimer(draw)
    return img


def slide_allocation():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    y = build_header(draw, subtitle="ALLOKATION NACH ANLAGEKLASSE")
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    cats = DATA["categories_mit_cash"]
    max_pct = max(c["percent"] for c in cats)
    bar_left = B.MARGIN_LEFT
    bar_max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 130
    row_h = 92
    y += 30

    for c in cats:
        color = CATEGORY_COLORS.get(c["label"], GOLD)
        label_font = font(B.SANS_BOLD, 24)
        draw.text((bar_left, y), c["label"], font=label_font, fill=CREAM)
        pct_font = font(B.SANS_BOLD, 24)
        pct_text = f"{c['percent']:.1f}%"
        pw = draw.textlength(pct_text, font=pct_font)
        draw.text((W - B.MARGIN_RIGHT - pw, y), pct_text, font=pct_font, fill=color)
        by = y + 34
        bar_w = int(bar_max_w * c["percent"] / max_pct)
        draw.rounded_rectangle([bar_left, by, bar_left + bar_max_w, by + 22], radius=11, fill=CARD, outline=CARD_BORDER, width=1)
        if bar_w > 22:
            draw.rounded_rectangle([bar_left, by, bar_left + bar_w, by + 22], radius=11, fill=color)
        y += row_h

    draw_disclaimer(draw, "Prozent vom Gesamtdepot inkl. Cash -- keine Bewertung, nur Aufteilung.")
    return img


def slide_top_positions():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    y = build_header(draw, subtitle="TOP-POSITIONEN")
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    positions = DATA["top_positions"]
    max_pct = max(p["percent"] for p in positions)
    bar_left = B.MARGIN_LEFT
    bar_max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 130
    row_h = 74
    y += 24

    for p in positions:
        name_font = font(B.SANS_BOLD, 23)
        draw.text((bar_left, y), p["name"], font=name_font, fill=CREAM)
        pct_font = font(B.SANS_BOLD, 23)
        pct_text = f"{p['percent']:.1f}%"
        pw = draw.textlength(pct_text, font=pct_font)
        draw.text((W - B.MARGIN_RIGHT - pw, y), pct_text, font=pct_font, fill=GOLD)
        by = y + 30
        bar_w = int(bar_max_w * p["percent"] / max_pct)
        draw.rounded_rectangle([bar_left, by, bar_left + bar_max_w, by + 14], radius=7, fill=CARD, outline=CARD_BORDER, width=1)
        if bar_w > 14:
            draw.rounded_rectangle([bar_left, by, bar_left + bar_w, by + 14], radius=7, fill=GOLD)
        y += row_h

    draw_disclaimer(draw, "Meine groessten Einzelpositionen nach Depotanteil -- keine Kaufempfehlung.")
    return img


def slide_cta():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    build_header(draw, subtitle="ZUM SCHLUSS")
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    y = 460
    draw.text((B.MARGIN_LEFT, y), "So bin ich aktuell", font=font(B.SANS_BOLD, 44), fill=CREAM)
    y += 58
    draw.text((B.MARGIN_LEFT, y), "aufgestellt.", font=font(B.SANS_BOLD, 44), fill=CREAM)
    y += 70
    draw.text((B.MARGIN_LEFT, y), "Wie sieht deine Aufteilung aus?", font=font(B.SANS_BOLD, 28), fill=GOLD)
    y += 38
    draw.text((B.MARGIN_LEFT, y), "Schreib's in die Kommentare.", font=font(B.SANS_BOLD, 28), fill=GOLD)

    draw_disclaimer(draw)
    return img


def main():
    slides = [slide_intro(), slide_allocation(), slide_top_positions(), slide_cta()]
    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")

    for i in range(1, len(slides) + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
