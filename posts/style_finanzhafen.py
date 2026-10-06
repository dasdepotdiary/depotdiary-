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
    ROOT / "assets" / "sk_nyc_wtc_sunset_still.jpg",
    ROOT / "assets" / "sk_dubai_burj_sunset_still.jpg",
    ROOT / "assets" / "sk_philadelphia_clouds_still.jpg",
    ROOT / "assets" / "sk_chicago_pink_still.jpg",
    ROOT / "assets" / "sk_frankfurt_dusk_still.jpg",
    ROOT / "assets" / "sk_frankfurt_main_sunset_still.jpg",
    ROOT / "assets" / "sk_frankfurt_night_still.jpg",
    ROOT / "assets" / "sk_chicago_blue_still.jpg",
    ROOT / "assets" / "sk_singapore_dusk_still.jpg",
    ROOT / "assets" / "sk_london_golden_still.jpg",
    ROOT / "assets" / "wallstreet_bull_still.jpg",
    ROOT / "assets" / "nyse_flag_still.jpg",
    ROOT / "assets" / "frankfurt_dusk_still.jpg",
    ROOT / "assets" / "skyscraper_up_still.jpg",
] + sorted((ROOT / "assets" / "new_sk").glob("sk2_*.jpg"))

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


def glass(img, boxes, radius=22, alpha=176):
    """Halbtransparente dunkle Karten ("Glas") ueber dem Foto -- gut lesbar,
    Foto bleibt in den Zwischenraeumen sichtbar. Gibt ein NEUES Bild zurueck
    (danach ImageDraw.Draw neu anlegen)."""
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for (x0, y0, x1, y1) in boxes:
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(8, 8, 10, alpha),
                            outline=(255, 255, 255, 46), width=1)
    return Image.alpha_composite(base, overlay).convert("RGB")


def draw_list_story(key, label, title_lines, entries, footer_text, date_label=None):
    """Generische Story fuer nummerierte/getaktete Eintraege (Tagesereignisse,
    Heute-Agenda): Skyline-Foto, Caps-Titel, Eintraege auf einer Glas-Karte
    (Foto bleibt sichtbar), Akzent-Tag + Headline + Fliesstext, automatisch auf die
    verfuegbare Hoehe skaliert.
    entries: [{"tag": "01" | "14:30 UHR", "headline": str, "body": str}]"""
    accent = accent_for(key)
    meas = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tf = font(80)
    title_h = len(title_lines) * 90
    title_y = SAFE_TOP + 110
    y0 = title_y + title_h + 70
    y_max = SAFE_BOTTOM - 130
    max_w = SW - 200

    for hs, bs in ((30, 23), (28, 22), (26, 20), (24, 19), (22, 17)):
        hf, bf = font(hs), font(bs)
        laid, total = [], 0
        for e in entries:
            hl = wrap_text(meas, e["headline"], hf, max_w)
            bl = wrap_text(meas, e["body"], bf, max_w) if e.get("body") else []
            h = 32 + len(hl) * int(hs * 1.22) + (8 + len(bl) * int(bs * 1.32) if bl else 0)
            laid.append((e, hl, bl, h))
            total += h + 30
        if total - 30 <= y_max - y0:
            break
    content_h = total - 30

    img = story_background(photo_for(key), scrim_from=0.55, scrim_len=0.30)
    card = (50, y0 - 36, SW - 50, y0 + content_h + 36)
    img = glass(img, [card], radius=26, alpha=186)
    draw = ImageDraw.Draw(img)
    draw_top(draw, accent, label, date_label)
    for line in title_lines:
        for dx, dy in ((3, 3), (2, 2)):
            draw.text((80 + dx, title_y + dy), line, font=tf, fill=(0, 0, 0))
        draw.text((80, title_y), line, font=tf, fill=CREAM)
        title_y += 90
    draw.rectangle([80, title_y + 6, 80 + 110, title_y + 12], fill=accent)

    y = y0
    for i, (e, hl, bl, h) in enumerate(laid):
        draw.text((90, y), e["tag"], font=font(22), fill=accent)
        yy = y + 32
        for line in hl:
            draw.text((90, yy), line, font=hf, fill=CREAM)
            yy += int(hs * 1.22)
        if bl:
            yy += 8
            for line in bl:
                draw.text((90, yy), line, font=bf, fill=SOFT)
                yy += int(bs * 1.32)
        y += h + 30
        if i < len(laid) - 1:
            draw.line([(90, y - 15), (SW - 90, y - 15)], fill=(95, 95, 98), width=1)

    footer_y = max(card[3] + 40, 1380)
    draw.text((80, SAFE_BOTTOM - 62), footer_text, font=font(20), fill=SOFT)
    draw_wordmark(img)
    return img


def draw_cta_story(key, label, title_lines, body, cta, note):
    """Call-to-Action-Story im Foto-Schema: Caps-Titel, kurzer Text, Akzent-CTA."""
    accent = accent_for(key)
    img = story_background(photo_for(key), scrim_from=0.22, scrim_len=0.30)
    draw = ImageDraw.Draw(img)
    draw_top(draw, accent, label)
    max_w = SW - 160
    meas = draw
    tf, tlines = fit_lines(draw, " ".join(title_lines), max_w, len(title_lines) + 1, 104, 60)
    # Zeilenumbrueche wie angegeben beibehalten, solange sie in die Breite passen
    tf = font(96)
    while any(draw.textlength(l, font=tf) > max_w for l in title_lines) and tf.size > 56:
        tf = font(tf.size - 4)
    bf = font(36)
    blines = wrap_text(draw, body, bf, max_w)
    cf = font(44)
    clines = wrap_text(draw, cta, cf, max_w)
    total = len(title_lines) * int(tf.size * 1.1) + 36 + len(blines) * 50 + 50 + len(clines) * 56
    y = 1420 - total
    for line in title_lines:
        draw.text((80, y), line, font=tf, fill=CREAM)
        y += int(tf.size * 1.1)
    y += 36
    for line in blines:
        draw.text((80, y), line, font=bf, fill=SOFT)
        y += 50
    y += 50
    draw.rectangle([80, y - 24, 80 + 90, y - 18], fill=accent)
    for line in clines:
        draw.text((80, y), line, font=cf, fill=accent)
        y += 56
    draw.text((80, SAFE_BOTTOM - 62), note, font=font(20), fill=MUTED)
    draw_wordmark(img)
    return img
