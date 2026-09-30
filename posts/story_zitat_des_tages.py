"""Neues Story-Format "Zitat des Tages" (2026-09-30, Nutzerwunsch: "ueberleg
dir noch ein weiteres Format fuer die Stories").

Echte, historische Zitate bekannter Investoren (Buffett, Bogle, etc.) mit
deutscher Uebersetzung + korrekter Namensnennung + einer kurzen, rein
erklaerenden Einordnung. KEINE eigene Bewertung/Empfehlung -- die Zitate
selbst sind historische Aussagen Dritter, keine aktuelle Kauf-/Verkaufs-
empfehlung von depotdiary. Evergreen, kein Tagesbezug notwendig -- gut
vorproduzierbar wie Fachbegriff des Tages.

Eigene Farbidentitaet: dunkles Waldgruen + warmes Gold -- noch nicht
verwendete Kombination (siehe Design-Rotation-Regel).

Input: term-artiges Dict mit quote/author/context.

Aufruf (Prototyp/Test):
  python posts/story_zitat_des_tages.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font as _font

NAME = "story_zitat_des_tages"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
BG_TOP = (14, 30, 24)
BG_BOTTOM = (7, 16, 13)
INK = "#F2F0E6"
SUBTEXT = "#B9C9BE"
GOLD = "#D4AF6A"
DIVIDER = "#2C4238"

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def font(path, size):
    return ImageFont.truetype(path, size)


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


def gradient_background():
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_glow(img, cx, cy, radius, color, strength=45):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.6))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def center_text(draw, text, fnt, y, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((W / 2 - tw / 2, y), text, font=fnt, fill=fill)


def slide_zitat(entry):
    img = gradient_background()
    add_glow(img, W * 0.5, H * 0.28, 560, (70, 100, 60), strength=35)
    draw = ImageDraw.Draw(img)

    eyebrow_font = font(B.SANS_BOLD, 18)
    center_text(draw, "@DASDEPOTDIARY  --  " + DATE_LABEL, eyebrow_font, 64, SUBTEXT)

    label_font = font(B.SANS_BOLD, 22)
    center_text(draw, "ZITAT DES TAGES", label_font, 122, GOLD)

    badge_font = font(B.SERIF_BOLD, 120)
    center_text(draw, "„", badge_font, 188, GOLD)

    quote_font = font(B.SERIF_BOLD_ITALIC, 46)
    content_w = W - 2 * 100
    quote_lines = wrap_text(draw, entry["quote"], quote_font, content_w)

    author_font = font(B.SANS_BOLD, 26)
    context_font = font(B.SANS_BOLD, 22)
    context_lines = wrap_text(draw, entry.get("context", ""), context_font, content_w) if entry.get("context") else []

    block_h = len(quote_lines) * 58 + 50 + 34
    if context_lines:
        block_h += 40 + len(context_lines) * 30
    footer_top = H - 140
    by = 340 + max(0, (footer_top - 340 - block_h) // 2)

    for line in quote_lines:
        center_text(draw, line, quote_font, by, INK)
        by += 58
    by += 20
    author_text = f"— {entry['author']}"
    center_text(draw, author_text, author_font, by, GOLD)
    by += 50

    if context_lines:
        line_w = 70
        draw.line([(W / 2 - line_w / 2, by), (W / 2 + line_w / 2, by)], fill=GOLD, width=3)
        by += 26
        for line in context_lines:
            center_text(draw, line, context_font, by, SUBTEXT)
            by += 30

    text = "Historisches Zitat -- keine Anlageberatung, keine aktuelle Empfehlung."
    disclaimer_font = font(B.SANS_BOLD, 17)
    draw.line([(90, H - 90), (W - 90, H - 90)], fill=DIVIDER, width=1)
    center_text(draw, text, disclaimer_font, H - 68, SUBTEXT)

    return img


def main():
    entry = {
        "quote": "Preis ist, was du bezahlst. Wert ist, was du bekommst.",
        "author": "Warren Buffett",
        "context": "Eine der bekanntesten Unterscheidungen im Value-Investing -- Kurs und Unternehmenswert sind nicht automatisch dasselbe.",
    }
    img = slide_zitat(entry)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
