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
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

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
    """v2 (2026-10-06): depotdiary-Foto-Schema (Skyline-Foto, Glas-Kacheln, rotierende
    Akzentfarbe) statt Violett-Flaeche. Schnittstelle (candidates, week_label) unveraendert."""
    key = "deepdive-" + week_label
    accent = S.accent_for(key)
    meas = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = S.SW - 160
    title = ["WELCHE AKTIE SOLL", "NAECHSTE WOCHE EINEN", "DEEP DIVE BEKOMMEN?"]
    tsize = 84
    while tsize > 52 and any(meas.textlength(l, font=S.font(tsize)) > max_w for l in title):
        tsize -= 4
    tf = S.font(tsize)
    title_y = S.SAFE_TOP + 110
    sub_y = title_y + len(title) * int(tsize * 1.12) + 24
    sf = S.font(26)
    sub = f"Diese Woche im Aktien-Check & auf meiner Watchlist ({week_label}):"
    sub_lines = S.wrap_text(meas, sub, sf, max_w)
    tiles_y = sub_y + len(sub_lines) * 36 + 30
    tile_h, tile_gap = 84, 16
    boxes = [(50, tiles_y + i * (tile_h + tile_gap), S.SW - 50, tiles_y + i * (tile_h + tile_gap) + tile_h)
             for i in range(len(candidates))]

    img = S.story_background(S.photo_for(key), scrim_from=0.30, scrim_len=0.30)
    img = S.glass(img, boxes, radius=20, alpha=180)
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, "DEEP-DIVE-ABSTIMMUNG")
    ty = title_y
    for line in title:
        draw.text((82, ty + 3), line, font=tf, fill=(0, 0, 0))
        draw.text((80, ty), line, font=tf, fill=S.CREAM)
        ty += int(tsize * 1.12)
    yy = sub_y
    for line in sub_lines:
        draw.text((80, yy), line, font=sf, fill=S.SOFT)
        yy += 36
    nf, kf = S.font(32), S.font(22)
    for (x0, y0, x1, y1), c in zip(boxes, candidates):
        draw.rectangle([x0, y0 + 10, x0 + 6, y1 - 10], fill=accent)
        draw.text((x0 + 34, y0 + (tile_h - 36) // 2), c["name"], font=nf, fill=S.CREAM)
        tw = draw.textlength(c["ticker"], font=kf)
        draw.text((x1 - 34 - tw, y0 + (tile_h - 24) // 2), c["ticker"], font=kf, fill=accent)

    cy = (boxes[-1][3] if boxes else tiles_y) + 44
    cf = S.font(36)
    for line in S.wrap_text(draw, "Schreib deinen Favoriten per DM oder Kommentar.", cf, max_w):
        draw.text((82, cy + 2), line, font=cf, fill=(0, 0, 0))
        draw.text((80, cy), line, font=cf, fill=accent)
        cy += 46
    fy = S.SAFE_BOTTOM - 84
    for line in S.wrap_text(draw, "Keine Anlageberatung -- der Sieger wird naechste Woche im Deep Dive vorgestellt.", S.font(19), 700):
        draw.text((80, fy), line, font=S.font(19), fill=S.SOFT)
        fy += 26
    S.draw_wordmark(img)
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
