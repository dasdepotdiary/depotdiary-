"""CTA-Story "Wie war deine Woche?" (neu, 2026-09-20): allgemeine
Engagement-Frage zur Boersenwoche, nicht aktienspezifisch -- Follower
antworten per DM/Kommentar (Graph API unterstuetzt keine echten
Umfrage-Sticker, gleiche Einschraenkung wie story_depotfrage_cta.py und
story_deepdive_poll.py). Eigene Farbidentitaet: warmes Terrakotta statt
Gold/Blau/Violett/Rosegold, die die anderen CTA-/Poll-Formate schon nutzen.

Aufruf:
  python posts/story_wochencheck_cta.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "story_wochencheck_cta"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (46, 26, 20)
BG_BOTTOM = (20, 12, 10)
CREAM = "#F2F0EA"
MUTED = "#C9AFA3"
TERRACOTTA = "#E0714F"
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


def main(week_label):
    img = gradient_background(BG_TOP, BG_BOTTOM)
    add_radial_glow(img, W // 2, H * 0.22, 480, (110, 56, 30), strength=55)
    draw = ImageDraw.Draw(img)

    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, 60), OWN_HANDLE, font=handle_font, fill=MUTED)

    y = H * 0.24
    label_font = font(B.SANS_BOLD, 28)
    label = "WOCHEN-CHECK"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=TERRACOTTA)
    y += 58

    title_font = font(B.SANS_BOLD, 52)
    for line in ["WIE WAR DEINE", "WOCHE?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 62

    y += 30
    sub_font = font(B.SANS_BOLD, 28)
    sub = f"Meins: {week_label}. Und bei dir -- Plus, Minus oder unveraendert?"
    for line in wrap_text(draw, sub, sub_font, W - 160):
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 38

    y += 50
    cta_font = font(B.SANS_BOLD, 34)
    cta = "Schreib's mir per DM oder Kommentar."
    tw = draw.textlength(cta, font=cta_font)
    draw.text((W / 2 - tw / 2, y), cta, font=cta_font, fill=TERRACOTTA)

    note_font = font(B.SANS_BOLD, 20)
    note = "Keine Anlageberatung -- reine Community-Frage."
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, H - 60), note, font=note_font, fill=MUTED)

    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main("+1,61 %")
