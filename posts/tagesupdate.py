"""Taegliches Marktupdate: Indizes, Rohstoffe, Sentiment, Krypto -- Liste
untereinander, Werte rechts daneben. Zweite Version (2026-09-09,
Nutzer-Feedback "ganze Seite voll, groesser, Design rumspielen"):
deutlich mehr Assets (KOSPI, Hang Seng als China-Proxy, Oel/WTI, VIX,
CNN Fear & Greed Index, Solana dazu), groessere Schrift/Zeilen, pro
Kategorie eine eigene Akzentfarbe inkl. farbigem Rand-Streifen je Zeile
statt einer einzigen Gold-Linie ueberall.

Echte Werte via Yahoo Finance Chart API (Indizes/Rohstoffe/VIX/Krypto)
und CNN's oeffentlicher Fear-&-Greed-Graphdata-Endpunkt (braucht
Referer-Header, sonst 418-Bot-Block).

Aufruf:
  python posts/tagesupdate.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "tagesupdate"
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
GREEN = "#4E8C6E"
RED = "#B5453A"

CAT_GOLD = "#C9A239"
CAT_COPPER = "#C77D3B"
CAT_RUST = "#C2573B"
CAT_VIOLET = "#8B7FE8"

OWN_HANDLE = "@DASDEPOTDIARY"

DATE_LABEL = date.today().strftime("%d.%m.%Y")
GROUPS = [
    {"label": "INDIZES", "color": CAT_GOLD, "rows": [
        ("S&P 500", "7.673,52", -0.16),
        ("Nasdaq", "26.421,41", +0.19),
        ("DAX", "26.006,50", +0.14),
        ("KOSPI", "6.954,52", +1.74),
        ("Hang Seng (China)", "25.317,18", -0.05),
    ]},
    {"label": "ROHSTOFFE", "color": CAT_COPPER, "rows": [
        ("Gold (USD/oz)", "4.397,30", +0.71),
        ("Silber (USD/oz)", "66,23", +2.32),
        ("Oel WTI (USD/Barrel)", "94,27", +3.58),
    ]},
    {"label": "SENTIMENT", "color": CAT_RUST, "rows": [
        ("VIX (Volatilitaet)", "15,72", +3.42),
        ("Fear & Greed Index", "40,8 -- Fear", None),
    ]},
    {"label": "KRYPTO", "color": CAT_VIOLET, "rows": [
        ("Bitcoin", "78.497,78", -1.47),
        ("Ethereum", "2.485,95", +1.22),
        ("Solana", "103,39", +1.41),
    ]},
]


def font(path, size):
    return ImageFont.truetype(path, size)


def build_header(draw, y=36):
    handle_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=CREAM)
    y += 28
    title_font = font(B.SANS_BOLD, 26)
    draw.text((B.MARGIN_LEFT, y), "TAGESUPDATE", font=title_font, fill=CREAM)
    y += 34
    date_font = font(B.SANS_BOLD, 16)
    draw.text((B.MARGIN_LEFT, y), f"Stand {DATE_LABEL}, US-Vorboerse/Schlusskurse.", font=date_font, fill=MUTED)
    y += 28
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 18


def draw_row(draw, x, y, w, name, value, change, accent):
    row_h = 66
    draw.rounded_rectangle([x, y, x + w, y + row_h], radius=9, fill=CARD, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([x, y, x + 6, y + row_h], radius=3, fill=accent)

    name_font = font(B.SANS_BOLD, 23)
    draw.text((x + 24, y + row_h / 2 - 14), name, font=name_font, fill=CREAM)

    value_font = font(B.SANS_BOLD, 24)
    vw = draw.textlength(value, font=value_font)
    if change is None:
        draw.text((x + w - 20 - vw, y + row_h / 2 - 12), value, font=value_font, fill=accent)
    else:
        change_font = font(B.SANS_BOLD, 17)
        change_color = GREEN if change >= 0 else RED
        change_text = f"{change:+.2f}%"
        cw = draw.textlength(change_text, font=change_font)
        draw.text((x + w - 20 - vw, y + 9), value, font=value_font, fill=CREAM)
        draw.text((x + w - 20 - cw, y + 36), change_text, font=change_font, fill=change_color)
    return row_h


def draw_footer(draw, text="Keine Anlageberatung -- nur Kurse, die ich mir angeschaut habe."):
    disclaimer_font = font(B.SANS_BOLD, 17)
    words = text.split()
    lines, cur = [], ""
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=disclaimer_font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    divider_y = H - 30 - 23 * len(lines) - 10
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 10
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 23


def gradient_background(top_rgb, bottom_rgb, w=W, h=H):
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((w, h))


def add_radial_glow(img, cx, cy, radius, color, strength=70):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.6))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def draw_candlestick_field(img):
    """Zweiter Design-Versuch (der helle Stil mit Kurve kam nicht gut an):
    ein ganzes Feld abstrakter Candlesticks quer ueber den Hintergrund --
    sehr niedriger Kontrast/dunkel-auf-dunkel, damit die Karten vorne
    lesbar bleiben, aber ein echtes 'Trading-Screen'-Gefuehl statt eines
    einfachen Verlaufs. Prozedural generiert (kein Foto/Stock-Clip)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    import random
    random.seed(11)
    n_cols = 34
    col_w = W / n_cols
    up_color = (78, 140, 110, 46)
    down_color = (181, 69, 58, 46)
    wick_color = (255, 255, 255, 22)
    y_center = H * 0.5
    trend = 0
    for i in range(n_cols):
        cx = col_w * i + col_w / 2
        trend += random.uniform(-1, 1.1)
        trend = max(-1, min(1, trend))
        body_h = random.uniform(40, 150)
        body_y = y_center - trend * H * 0.28 + random.uniform(-60, 60)
        wick_h = body_h + random.uniform(30, 90)
        is_up = random.random() < 0.52
        color = up_color if is_up else down_color
        ldraw.line([(cx, body_y - wick_h / 2), (cx, body_y + wick_h / 2)], fill=wick_color, width=2)
        ldraw.rectangle([cx - col_w * 0.28, body_y - body_h / 2, cx + col_w * 0.28, body_y + body_h / 2], fill=color)
    img.paste(layer, (0, 0), layer)


def slide_update():
    img = gradient_background((22, 18, 14), (12, 10, 8))
    draw_candlestick_field(img)
    add_radial_glow(img, W // 2, -80, 560, (120, 95, 40), strength=45)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=CAT_GOLD)

    y = build_header(draw)

    group_label_font = font(B.SANS_BOLD, 16)
    row_gap = 6
    group_gap = 16
    for group in GROUPS:
        draw.text((B.MARGIN_LEFT, y), group["label"], font=group_label_font, fill=group["color"])
        y += 24
        for name, value, change in group["rows"]:
            row_h = draw_row(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, name, value, change, group["color"])
            y += row_h + row_gap
        y += group_gap - row_gap

    draw_footer(draw)
    return img


def main():
    img = slide_update()
    img.save(IG_DIR / "slide_1.png")

    canvas = Image.new("RGB", B.STORY_SIZE, BG)
    x = (B.STORY_SIZE[0] - img.width) // 2
    y = (B.STORY_SIZE[1] - img.height) // 2
    canvas.paste(img, (x, y))
    canvas.save(TT_DIR / "slide_1.png")

    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
