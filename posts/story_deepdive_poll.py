"""Woechentliche Story "DEEP DIVE ABSTIMMUNG" (neu, 2026-09-19): fragt Follower,
welche der diese Woche im Aktien-Check/Watchlist gezeigten Aktien naechste
Woche einen ausfuehrlichen Deep-Dive-Post bekommen soll. Instagram Graph API
unterstuetzt keine echten interaktiven Umfrage-Sticker (geprueft 2026-09-16,
siehe story_depotfrage_cta.py) -- deshalb wie dort eine CTA-Story mit
Abstimmung per DM/Kommentar statt nativem Sticker.

Eigene visuelle Identitaet (Design-Rotationsprinzip): tiefes Violett/Indigo,
keine der bisher genutzten Akzentfarben (Gold/Blau/Rosegold/Orange/Skyblue).

Input: candidates (Liste von {name, ticker}), optional week_label.

Aufruf (Prototyp/Test):
  python posts/story_deepdive_poll.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "story_deepdive_poll"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (36, 24, 58)
BG_BOTTOM = (16, 11, 26)
CREAM = "#F2F0EA"
MUTED = "#B3A8C4"
VIOLET = "#A78BFA"
OWN_HANDLE = "@DASDEPOTDIARY"


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


def gradient_background(top_rgb, bottom_rgb):
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_radial_glow(img, cx, cy, radius, color, strength=55):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def main(candidates, week_label):
    img = gradient_background(BG_TOP, BG_BOTTOM)
    add_radial_glow(img, W // 2, H * 0.2, 480, (70, 40, 110), strength=55)
    draw = ImageDraw.Draw(img)

    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, 60), OWN_HANDLE, font=handle_font, fill=MUTED)

    y = H * 0.20
    label_font = font(B.SANS_BOLD, 28)
    label = "DEEP DIVE ABSTIMMUNG"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=VIOLET)
    y += 56

    title_font = font(B.SANS_BOLD, 44)
    for line in ["WELCHE AKTIE SOLL", "NAECHSTE WOCHE EINEN", "DEEP DIVE BEKOMMEN?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 52

    y += 30
    sub_font = font(B.SANS_BOLD, 22)
    sub = f"Diese Woche im Aktien-Check & auf meiner Watchlist ({week_label}):"
    sub_lines = wrap_text(draw, sub, sub_font, W - 160)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 30

    y += 20
    card_h = 76
    gap = 18
    card_w = W - 140
    cx = 70
    name_font = font(B.SANS_BOLD, 30)
    ticker_font = font(B.SANS_BOLD, 20)
    for c in candidates:
        draw.rounded_rectangle([cx, y, cx + card_w, y + card_h], radius=14,
                                fill="#241833", outline=VIOLET, width=1)
        draw.text((cx + 28, y + 16), c["name"], font=name_font, fill=CREAM)
        tick_text = c["ticker"]
        tw = draw.textlength(tick_text, font=ticker_font)
        draw.text((cx + card_w - 28 - tw, y + 26), tick_text, font=ticker_font, fill=VIOLET)
        y += card_h + gap

    y += 20
    cta_font = font(B.SANS_BOLD, 32)
    cta = "Schreib deinen Favoriten per DM oder Kommentar."
    cta_lines = wrap_text(draw, cta, cta_font, W - 140)
    for line in cta_lines:
        tw = draw.textlength(line, font=cta_font)
        draw.text((W / 2 - tw / 2, y), line, font=cta_font, fill=VIOLET)
        y += 38

    note_font = font(B.SANS_BOLD, 18)
    note = "Keine Anlageberatung -- der Sieger wird naechste Woche im Deep Dive vorgestellt."
    note_lines = wrap_text(draw, note, note_font, W - 140)
    ny = H - 30 - len(note_lines) * 24
    for line in note_lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, ny), line, font=note_font, fill=MUTED)
        ny += 24

    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    candidates = [
        {"name": "SAP", "ticker": "SAP"},
        {"name": "Alphabet", "ticker": "GOOGL"},
        {"name": "Costco", "ticker": "COST"},
        {"name": "GE Vernova", "ticker": "GEV"},
    ]
    main(candidates, "15.-19.09.")
