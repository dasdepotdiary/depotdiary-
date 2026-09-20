"""Einzelbild-Post "WOCHENRUECKBLICK -- MEIN DEPOT" (neu, 2026-09-20): eine
einzelne Slide, nur fuer den eigenen Account -- wie sich das eigene Depot
diese Woche performancemaessig entwickelt hat + welche Kaeufe/Verkaeufe
getaetigt wurden. Kein Marktueberblick (das macht der bestehende
depotdiary-wochenrueckblick-Task), sondern rein die persoenliche Perspektive.

Rein faktisch (Performance in %, tatsaechliche Kaeufe/Verkaeufe zu den vom
Nutzer genannten Preisen) + eigene kurze Einordnung -- keine Kursziele,
keine Kauf-/Verkaufsempfehlung.

Input: performance_pct, buys (Liste von {label, ticker, price, note}),
sells (Liste, leer wenn keine).

Aufruf (Prototyp/Test):
  python posts/format_wochenrueckblick_depot.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "format_wochenrueckblick_depot"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "posts"
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
GREEN = "#5FB88A"
RED = "#C0392B"

OWN_HANDLE = "@DASDEPOTDIARY"
DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


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


def add_glow(img, cx, cy, radius, color, strength=45):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.55))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def draw_buy_row(draw, x, y, w, entry):
    row_h = 92
    draw.rounded_rectangle([x, y, x + w, y + row_h], radius=14, fill=CARD, outline=CARD_BORDER, width=1)
    pad = 22
    label_font = font(B.SANS_BOLD, 26)
    draw.text((x + pad, y + 16), entry["label"], font=label_font, fill=CREAM)
    sub_font = font(B.SANS_BOLD, 18)
    draw.text((x + pad, y + 52), entry["note"], font=sub_font, fill=MUTED)
    if entry.get("price"):
        price_text = f"{entry['price']}"
        price_font = font(B.SANS_BOLD, 24)
        pw = draw.textlength(price_text, font=price_font)
        draw.text((x + w - pad - pw, y + 32), price_text, font=price_font, fill=GOLD)
    return row_h


def main(performance_pct, buys, sells):
    img = Image.new("RGB", (W, H), BG)
    add_glow(img, W * 0.5, -80, 620, (60, 46, 16), strength=45)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    y = 56
    handle_font = font(B.SANS_BOLD, 22)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=MUTED)
    y += 34
    title_font = font(B.SANS_BOLD, 30)
    draw.text((B.MARGIN_LEFT, y), "WOCHENRUECKBLICK -- MEIN DEPOT", font=title_font, fill=GOLD)
    y += 38
    date_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), DATE_LABEL, font=date_font, fill=MUTED)
    y += 60

    perf_color = GREEN if performance_pct >= 0 else RED
    perf_font = font(B.SANS_BOLD, 108)
    perf_text = f"{'+' if performance_pct >= 0 else ''}{performance_pct:.2f}".replace(".", ",") + " %"
    draw.text((B.MARGIN_LEFT, y), perf_text, font=perf_font, fill=perf_color)
    y += 128
    sub_font = font(B.SANS_BOLD, 26)
    draw.text((B.MARGIN_LEFT, y), "So hat sich mein Depot diese Woche entwickelt.", font=sub_font, fill=CREAM)
    y += 66

    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    section_font = font(B.SANS_BOLD, 22)
    draw.text((B.MARGIN_LEFT, y), "KAEUFE DIESE WOCHE", font=section_font, fill=GOLD)
    y += 38
    for b in buys:
        row_h = draw_buy_row(draw, B.MARGIN_LEFT, y, content_w, b)
        y += row_h + 14

    y += 10
    draw.text((B.MARGIN_LEFT, y), "VERKAEUFE", font=section_font, fill=GOLD)
    y += 38
    sells_font = font(B.SANS_BOLD, 24)
    sells_text = "Keine Verkaeufe diese Woche." if not sells else ", ".join(sells)
    draw.text((B.MARGIN_LEFT, y), sells_text, font=sells_font, fill=CREAM)

    disclaimer_font = font(B.SANS_BOLD, 20)
    disclaimer = "Keine Anlageberatung -- nur, was ich selbst gemacht habe."
    lines = wrap_text(draw, disclaimer, disclaimer_font, content_w)
    dy = H - 40 - len(lines) * 26
    draw.line([(B.MARGIN_LEFT, dy - 20), (W - B.MARGIN_RIGHT, dy - 20)], fill=CARD_BORDER, width=1)
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 26

    return img


if __name__ == "__main__":
    buys = [
        {"label": "Sparplan (regulaer)", "note": "Wie jeden Monat -- automatische Ausfuehrung.", "price": ""},
        {"label": "Broadcom (AVGO)", "note": "Einzelkauf diesen Monat.", "price": "297 USD"},
        {"label": "Vistra (VST)", "note": "Einzelkauf diesen Monat.", "price": "301 USD"},
        {"label": "Uber (UBER)", "note": "Bereits letzte Woche gekauft.", "price": "400 USD"},
    ]
    sells = []
    img = main(1.61, buys, sells)
    img.save(IG_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    feed_w, feed_h = B.FEED_SIZE
    story = Image.new("RGB", B.STORY_SIZE, BG)
    x = (B.STORY_SIZE[0] - feed_w) // 2
    yoff = (B.STORY_SIZE[1] - feed_h) // 2
    story.paste(img, (x, yoff))
    story.save(TT_DIR / "slide_1.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")
