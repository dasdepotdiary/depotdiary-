"""Portfolio-Update mit transparenten Prozentzahlen -- Allokation nach
Anlageklasse + Top-Positionen, aus den echten (selbst gepflegten) Depot-
Daten unter data/depot_2026-08.json.

v3 (2026-09-26, Nutzerwunsch: "mach bitte bei meiner Allokation den
Vermoegensingenieur-Design anwenden"): visuelle Sprache von
posts/collab_vermoegensingenieur_10k.py uebernommen -- stark abgedunkeltes
echtes Foto (naechtliche Skyline), fette weisse Grossbuchstaben-Headlines,
Teal/Cyan-Akzent mit Pinselstrich-Unterstreichung. Eigenstaendig zugeschnitten,
nicht 1:1 kopiert.

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

CREAM = (245, 245, 242)
MUTED = (185, 185, 182)
TEAL = (46, 214, 199)
TRACK = (255, 255, 255, 40)

OWN_HANDLE = "@DASDEPOTDIARY"

# Feste Kategorie-Reihenfolge -- eine Akzentfarbe (Teal) fuer alle Balken,
# konsistent mit dem Vermoegensingenieur-Stil (eine Signalfarbe, nicht bunt).
DATA = json.loads((ROOT / "data" / "depot_2026-08.json").read_text(encoding="utf-8"))
STAND = "26.09.2026"

_SKYLINE_SRC = Image.open(ROOT / "assets" / "skyline_still_1.png").convert("RGB")


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


def photo_background(seed=1):
    src = _SKYLINE_SRC
    sw, sh = src.size
    scale = max(W / sw, H / sh)
    resized = src.resize((int(sw * scale), int(sh * scale)))
    x_off = int((resized.width - W) * (0.3 + 0.1 * (seed % 3)))
    y_off = int((resized.height - H) * 0.2)
    cropped = resized.crop((x_off, y_off, x_off + W, y_off + H))
    darkened = ImageEnhance.Brightness(cropped).enhance(0.42)
    darkened = ImageEnhance.Contrast(darkened).enhance(1.15)
    img = darkened.convert("RGB")
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, W, 260], fill=180)
    vdraw.rectangle([0, H - 220, W, H], fill=180)
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    black = Image.new("RGB", (W, H), (5, 6, 8))
    img.paste(black, (0, 0), vignette)
    return img


def base_slide(seed=1):
    img = photo_background(seed)
    draw = ImageDraw.Draw(img)
    return img, draw


def brush_underline(draw, x, y, w, color=TEAL, thickness=8):
    draw.line([(x, y), (x + w, y)], fill=color, width=thickness)


def build_header(draw, y=40):
    handle_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=CREAM)
    return y + 44


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- nur, wie ich selbst aufgestellt bin."):
    disclaimer_font = font(B.SANS_BOLD, 18)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    dy = H - 36 - 24 * len(lines)
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 24
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 36 - 24 * len(lines)), page_text, font=page_font, fill=MUTED)


def bar_row(img, draw, x, y, w, label, pct, max_pct, bar_h=20):
    label_font = font(B.SANS_BOLD, 25)
    draw.text((x, y), label, font=label_font, fill=CREAM)
    pct_font = font(B.SANS_BOLD, 25)
    pct_text = f"{pct:.1f}%"
    pw = draw.textlength(pct_text, font=pct_font)
    draw.text((x + w - pw, y), pct_text, font=pct_font, fill=TEAL)
    by = y + 34
    track = Image.new("RGBA", (w, bar_h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(track)
    tdraw.rounded_rectangle([0, 0, w, bar_h], radius=bar_h // 2, fill=TRACK)
    img.paste(track, (int(x), int(by)), track)
    bar_w = max(bar_h, int(w * pct / max_pct))
    draw.rounded_rectangle([x, by, x + bar_w, by + bar_h], radius=bar_h // 2, fill=TEAL)
    return by + bar_h


def slide_intro():
    img, draw = base_slide(seed=1)
    y = build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), "NEUE FOLGE", font=eyebrow_font, fill=TEAL)
    y += 60

    draw.text((B.MARGIN_LEFT, y), "PORTFOLIO-", font=font(B.SANS_BOLD, 70), fill=CREAM)
    y += 80
    draw.text((B.MARGIN_LEFT, y), "UPDATE.", font=font(B.SANS_BOLD, 70), fill=CREAM)
    y += 78
    brush_underline(draw, B.MARGIN_LEFT, y, 170, thickness=9)
    y += 50

    sub_font = font(B.SANS_BOLD, 26)
    for line in wrap_text(draw, "Wie ich aktuell aufgestellt bin -- mit echten Prozentzahlen.",
                           sub_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT):
        draw.text((B.MARGIN_LEFT, y), line, font=sub_font, fill=MUTED)
        y += 34
    y += 20
    draw.text((B.MARGIN_LEFT, y), f"Stand: {STAND}", font=font(B.SANS_BOLD, 21), fill=MUTED)

    draw_footer(draw, 1, 4)
    return img


def slide_allocation():
    img, draw = base_slide(seed=2)
    y = build_header(draw)

    label_font = font(B.SANS_BOLD, 22)
    draw.text((B.MARGIN_LEFT, y), "ALLOKATION NACH ANLAGEKLASSE", font=label_font, fill=TEAL)
    y += 34
    brush_underline(draw, B.MARGIN_LEFT, y, 100, thickness=6)
    y += 46

    cats = DATA["categories_mit_cash"]
    max_pct = max(c["percent"] for c in cats)
    bar_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    for c in cats:
        y = bar_row(img, draw, B.MARGIN_LEFT, y, bar_w, c["label"].upper(), c["percent"], max_pct)
        draw = ImageDraw.Draw(img)
        y += 58

    draw_footer(draw, 2, 4, "Prozent vom Gesamtdepot inkl. Cash -- keine Bewertung, nur Aufteilung.")
    return img


def slide_top_positions():
    img, draw = base_slide(seed=3)
    y = build_header(draw)

    label_font = font(B.SANS_BOLD, 22)
    draw.text((B.MARGIN_LEFT, y), "TOP-POSITIONEN", font=label_font, fill=TEAL)
    y += 34
    brush_underline(draw, B.MARGIN_LEFT, y, 100, thickness=6)
    y += 42

    positions = DATA["top_positions"]
    max_pct = max(p["percent"] for p in positions)
    bar_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    for p in positions:
        y = bar_row(img, draw, B.MARGIN_LEFT, y, bar_w, p["name"].upper(), p["percent"], max_pct, bar_h=14)
        draw = ImageDraw.Draw(img)
        y += 40

    draw_footer(draw, 3, 4, "Meine groessten Einzelpositionen nach Depotanteil -- keine Kaufempfehlung.")
    return img


def slide_cta():
    img, draw = base_slide(seed=4)
    y = build_header(draw)
    y += 80

    title_font = font(B.SANS_BOLD, 48)
    for line in ["WIE SIEHT DEINE", "AUFTEILUNG AUS?"]:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 58
    brush_underline(draw, B.MARGIN_LEFT, y + 4, 170, thickness=9)
    y += 60

    sub_font = font(B.SANS_BOLD, 26)
    draw.text((B.MARGIN_LEFT, y), "Schreib's in die Kommentare.", font=sub_font, fill=TEAL)

    draw_footer(draw, 4, 4)
    return img


def main():
    slides = [slide_intro(), slide_allocation(), slide_top_positions(), slide_cta()]
    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")

    for i in range(1, len(slides) + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, (8, 8, 10))
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (12, 12, 14))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
