"""Portfolio-Update mit transparenten Prozentzahlen -- Allokation nach
Anlageklasse + Top-Positionen, aus den echten (selbst gepflegten) Depot-
Daten unter data/depot_2026-08.json.

v2 (2026-09-26, Nutzer-Feedback zu v1 "nein das Design -- wie bei ihm im
Glas-Design mit schoenem Bild"): komplett neu im Skyline-Foto+Glas-Karten-
Stil von format_wochenrueckblick_depot_skyline.py (vom Nutzer bereits
freigegeben) statt der frueheren flachen dunklen Creme/Gold-Flaeche.

Reine Offenlegung der eigenen Aufteilung -- keine Kursziele, keine Kauf-/
Verkaufsempfehlung (siehe CLAUDE.md-Regel).

Aufruf:
  python posts/personal_portfolio_percent_update.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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

INK = "#16181C"
CREAM = "#F2F0EA"
MUTED_LIGHT = "#C9C4B6"
GOLD = "#B08A2E"
CARD = (16, 16, 14, 172)
CARD_BORDER = "#D8D2C2"
BAR_TRACK = (255, 255, 255, 40)

OWN_HANDLE = "@DASDEPOTDIARY"

# Feste Kategorie-Reihenfolge + eigene Farbe je Kategorie (kategorial, nicht zyklisch)
CATEGORY_COLORS = {
    "Einzelaktien": "#D9B25C",
    "ETFs & Fonds": "#7FBF9E",
    "Bitcoin & BTC-Treasuries": "#E0A15C",
    "Gold & Silber": "#D8D2C2",
    "Cash": "#9B9587",
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


def skyline_background():
    photo = Image.open(ROOT / "assets" / "skyline_day_still.png").convert("RGB")
    photo = photo.resize((W, H)) if photo.size != (W, H) else photo
    img = ImageEnhance.Brightness(photo).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, W, 170], fill=90)
    vdraw.rectangle([0, H - 140, W, H], fill=110)
    vignette = vignette.filter(ImageFilter.GaussianBlur(70))
    white = Image.new("RGB", (W, H), (245, 243, 236))
    img = Image.composite(white, img, vignette)
    return img


def card(img, draw, x, y, w, h, radius=20):
    overlay = Image.new("RGBA", (w, h), CARD)
    img.paste(overlay, (x, y), overlay)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=CARD_BORDER, width=1)


def header(draw, y=56):
    handle_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=INK)
    return y + 32


def footer(draw, idx, n_total, text="Keine Anlageberatung -- nur, wie ich selbst aufgestellt bin."):
    disclaimer_font = font(B.SANS_BOLD, 18)
    tw = draw.textlength(text, font=disclaimer_font)
    draw.text((W / 2 - tw / 2, H - 56), text, font=disclaimer_font, fill=INK)
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, 56), page_text, font=page_font, fill=INK)


def slide_intro(n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 620, W - 120, 320
    card(img, draw, cx, cy, cw, ch)
    ty = cy + 40
    title_font = font(B.SERIF_BOLD, 52)
    for line in ["Portfolio-Update.", "Wie ich aufgestellt bin."]:
        draw.text((cx + 40, ty), line, font=title_font, fill=CREAM)
        ty += 62
    ty += 10
    sub_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, ty), f"Stand: {STAND} -- mit echten Prozentzahlen.", font=sub_font, fill=GOLD)

    footer(draw, 1, n_total)
    return img


def bar_row(img, draw, x, y, w, label, pct, max_pct, color, bar_h=20):
    label_font = font(B.SANS_BOLD, 23)
    draw.text((x, y), label, font=label_font, fill=CREAM)
    pct_font = font(B.SANS_BOLD, 23)
    pct_text = f"{pct:.1f}%"
    pw = draw.textlength(pct_text, font=pct_font)
    draw.text((x + w - pw, y), pct_text, font=pct_font, fill=color)
    by = y + 32
    track = Image.new("RGBA", (w, bar_h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(track)
    tdraw.rounded_rectangle([0, 0, w, bar_h], radius=bar_h // 2, fill=BAR_TRACK)
    img.paste(track, (int(x), int(by)), track)
    bar_w = max(bar_h, int(w * pct / max_pct))
    draw.rounded_rectangle([x, by, x + bar_w, by + bar_h], radius=bar_h // 2, fill=color)
    return by + bar_h


def slide_allocation(idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cats = DATA["categories_mit_cash"]
    cx, cy, cw, ch = 60, 380, W - 120, 560
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 32), "ALLOKATION NACH ANLAGEKLASSE", font=label_font, fill=GOLD)

    max_pct = max(c["percent"] for c in cats)
    row_y = cy + 90
    row_gap = 82
    for c in cats:
        color = CATEGORY_COLORS.get(c["label"], GOLD)
        bottom = bar_row(img, draw, cx + 40, row_y, cw - 80, c["label"], c["percent"], max_pct, color)
        draw = ImageDraw.Draw(img)
        row_y += row_gap

    footer(draw, idx, n_total, "Prozent vom Gesamtdepot inkl. Cash -- keine Bewertung, nur Aufteilung.")
    return img


def slide_top_positions(idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    positions = DATA["top_positions"]
    cx, cy, cw, ch = 60, 260, W - 120, 780
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 32), "TOP-POSITIONEN", font=label_font, fill=GOLD)

    max_pct = max(p["percent"] for p in positions)
    row_y = cy + 90
    row_gap = 68
    for p in positions:
        bar_row(img, draw, cx + 40, row_y, cw - 80, p["name"], p["percent"], max_pct, GOLD, bar_h=14)
        draw = ImageDraw.Draw(img)
        row_y += row_gap

    footer(draw, idx, n_total, "Meine groessten Einzelpositionen nach Depotanteil -- keine Kaufempfehlung.")
    return img


def slide_cta(idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 700, W - 120, 320
    card(img, draw, cx, cy, cw, ch)
    ty = cy + 40
    title_font = font(B.SERIF_BOLD, 42)
    for line in ["Wie sieht deine", "Aufteilung aus?"]:
        draw.text((cx + 40, ty), line, font=title_font, fill=CREAM)
        ty += 54
    ty += 14
    sub_font = font(B.SANS_BOLD, 24)
    draw.text((cx + 40, ty), "Schreib's in die Kommentare.", font=sub_font, fill=GOLD)

    footer(draw, idx, n_total)
    return img


def main():
    n = 4
    slides = [
        slide_intro(n),
        slide_allocation(2, n),
        slide_top_positions(3, n),
        slide_cta(4, n),
    ]
    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")

    for i in range(1, len(slides) + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, (245, 243, 236))
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = min(4, n)
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (240, 238, 232))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
