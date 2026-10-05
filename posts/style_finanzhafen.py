"""Gemeinsames Foto-Schema fuer Stories (Nutzerwunsch 2026-10-05: "alle
einfaerbigen Designs spannender machen, ein Schema das zum Account passt und
zum Finanzhafen-Stil des Feeds").

Das Schema ("depotdiary-Foto-Schema"):
  1. Vollflaechiges, starkes Finanz-/Stadtfoto (Pool, rotiert per Datum/Name)
  2. Dunkler Verlauf von unten (Text bleibt lesbar, Foto bleibt oben sichtbar)
  3. Eine grelle Akzentfarbe pro Post (Pool, rotiert) fuer Label + Schluesselwoerter
  4. Fette Caps-Headline linksbuendig, Fliesstext in Off-White
  5. Fester Anker: depotdiary-Wortmarke unten rechts (statt Avatar)
  6. Story-Safe-Zones: oben ~260 px und unten ~340 px werden von der
     Instagram-UI ueberdeckt -- dort steht nichts Wichtiges.

Nur Hilfsfunktionen, keine Seiteneffekte beim Import.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
SW, SH = B.STORY_SIZE
SAFE_TOP = 270
SAFE_BOTTOM = SH - 340

CREAM = "#F5F3EE"
SOFT = "#D8D5CE"
MUTED = "#A9A59C"

PHOTOS = [
    ROOT / "assets" / "wallstreet_bull_still.jpg",
    ROOT / "assets" / "nyse_flag_still.jpg",
    ROOT / "assets" / "frankfurt_dusk_still.jpg",
    ROOT / "assets" / "chart_screen_still.jpg",
    ROOT / "assets" / "skyscraper_up_still.jpg",
    ROOT / "assets" / "gold_bars_still.jpg",
    ROOT / "assets" / "nyse_columns_still.jpg",
    ROOT / "assets" / "crypto_coins_still.jpg",
    ROOT / "assets" / "downtown_street_still.png",
]

ACCENTS = ["#4CC9F0", "#FF3EA5", "#B6FF3D", "#FFDD3D", "#7B5CFF"]

WORDMARK = ROOT / "assets" / "logo_depotdiary_stacked_transparent.png"


def _digest(key, salt=""):
    return int(hashlib.md5((key + salt).encode("utf-8")).hexdigest(), 16)


def photo_for(key):
    return PHOTOS[_digest(key, "photo") % len(PHOTOS)]


def accent_for(key):
    return ACCENTS[_digest(key, "accent") % len(ACCENTS)]


def font(size, path=None):
    return ImageFont.truetype(path or B.SANS_BOLD, size)


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, max_w, max_lines, start, minimum, path=None):
    """Groesste Schrift (start..minimum), bei der text in max_lines passt."""
    size = start
    while size >= minimum:
        f = font(size, path)
        lines = wrap_text(draw, text, f, max_w)
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 4
    f = font(minimum, path)
    return f, wrap_text(draw, text, f, max_w)


def story_background(photo_path, scrim_from=0.34, scrim_len=0.34):
    """Foto auf 9:16 (cover), leicht abgedunkelt, dunkler Verlauf von unten."""
    photo = Image.open(photo_path).convert("RGB")
    ratio = SW / SH
    if photo.width / photo.height > ratio:
        nw = int(photo.height * ratio)
        x0 = (photo.width - nw) // 2
        photo = photo.crop((x0, 0, x0 + nw, photo.height))
    else:
        nh = int(photo.width / ratio)
        y0 = int((photo.height - nh) * 0.30)
        photo = photo.crop((0, y0, photo.width, y0 + nh))
    photo = photo.resize((SW, SH), Image.LANCZOS)
    img = ImageEnhance.Brightness(photo).enhance(0.82)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(0.92)

    scrim = Image.new("L", (SW, SH), 0)
    sd = ImageDraw.Draw(scrim)
    for y in range(SH):
        t = y / SH
        top = 175 if t < 0.15 else (int(175 * (1 - (t - 0.15) / 0.17)) if t < 0.32 else 0)
        bottom = int(242 * min(1.0, max(0.0, (t - scrim_from) / scrim_len)))
        sd.line([(0, y), (SW, y)], fill=max(top, bottom))
    black = Image.new("RGB", (SW, SH), (6, 5, 5))
    return Image.composite(black, img, scrim)


def light_wordmark(height):
    """Wortmarke ist dunkle Tinte auf transparentem Grund -- auf Foto-Hintergruenden
    unsichtbar. Hier: Alpha-Maske uebernehmen, Rand abschneiden, in Off-White faerben."""
    logo = Image.open(WORDMARK).convert("RGBA")
    alpha = logo.split()[3]
    box = alpha.getbbox()
    if box:
        alpha = alpha.crop(box)
    light = Image.new("RGBA", alpha.size, (245, 243, 238, 255))
    light.putalpha(alpha)
    return light.resize((max(1, int(light.width * height / light.height)), height), Image.LANCZOS)


def draw_wordmark(img, bottom=None, height=88):
    try:
        logo = light_wordmark(height)
        bottom = SAFE_BOTTOM - 14 if bottom is None else bottom
        img.paste(logo, (SW - logo.width - 70, bottom - logo.height), logo)
    except FileNotFoundError:
        pass


def draw_top(draw, accent, label, date_label=None):
    """Handle + Label im oberen Safe-Bereich (unterhalb der IG-UI), mit weichem Schatten
    damit es auch auf hellen Fotos lesbar bleibt."""
    handle = "@DASDEPOTDIARY" + (f"   {date_label}" if date_label else "")
    for dx, dy in ((3, 3), (2, 2)):
        draw.text((80 + dx, SAFE_TOP + dy), handle, font=font(24), fill=(0, 0, 0))
        draw.text((80 + dx, SAFE_TOP + 44 + dy), label, font=font(30), fill=(0, 0, 0))
    draw.text((80, SAFE_TOP), handle, font=font(24), fill=CREAM)
    draw.text((80, SAFE_TOP + 44), label, font=font(30), fill=accent)
