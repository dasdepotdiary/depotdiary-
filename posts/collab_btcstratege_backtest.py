"""Collab mit @btcstratege -- zweite grosse Ueberarbeitung auf
Nutzerwunsch vom 2026-09-08: mehr Beispiele (Gold, Silber, Aktienindex,
Einzelaktie Apple, Sparbuch -- alle gegen Bitcoin ueber 10 Jahre), echte
Mini-Kurscharts statt nur Stat-Boxen, komplett neuer Verlaufs-Hintergrund
(Gradient + Glow) statt der sonst im Account ueberall gleichen flachen
dunklen Flaeche.

WICHTIG zur Compliance: "Koenig der Kryptowaehrungen" ist ein tatsaechlich
gebraeuchlicher, verifizierbarer Spitzname fuer Bitcoin (nicht meine
eigene Bewertung) -- bewusst NICHT als "Bitcoin ist die beste Anlage"
formuliert, das waere eine Bewertung/Empfehlung und damit ein Verstoss
gegen die Account-Regel (vgl. die abgelehnte "HOT-Rating"-Idee bei
collab_aktienanalyst.py). Die Ueberperformance wird als reiner,
einmaliger historischer Rueckblick praesentiert (echte Kurse/echter
Sparbuch-Durchschnittszins, ein fest gewaehlter Zeitraum), explizit mit
Volatilitaets-Hinweis im Fazit -- nicht als Kaufargument. Sparbuch-Zins
(~0,4% p.a. ueber 10 Jahre) recherchiert (tagesgeldvergleich.net/raisin.com),
als synthetische Zinseszins-Reihe fuer den Mini-Chart nachgebildet (keine
Marktdaten fuer ein Sparbuch verfuegbar).

Aufruf:
  python posts/collab_btcstratege_backtest.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "collab_btcstratege_backtest"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

CREAM = "#F2F0EA"
MUTED = "#9B9587"
GREEN = B.GREEN_MID
BTC_ORANGE = "#F7931A"
GOLD_COLOR = "#D4AF37"
SILVER_COLOR = "#C0C0C8"
SPARBUCH_COLOR = "#7A8FA6"
CARD_BORDER = (58, 50, 38)

OWN_HANDLE = "@DASDEPOTDIARY"

DATA = json.loads((ROOT / "posts" / "inputs" / "collab_btcstratege_backtest.json").read_text(encoding="utf-8"))["meta"]

ASSET_COLORS = {
    "GOLD": GOLD_COLOR, "SILBER": SILVER_COLOR, "AKTIEN (S&P 500)": GREEN,
    "EINZELAKTIE (APPLE)": "#A78BFA", "SPARBUCH": SPARBUCH_COLOR,
}


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


def gradient_background(top_rgb, bottom_rgb, w=W, h=H):
    """Vertikaler Verlauf statt der sonst im Account ueberall gleichen
    flachen dunklen Flaeche -- bewusst anders fuer diesen einen Collab."""
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((w, h))


def add_radial_glow(img, cx, cy, radius, color, strength=140):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.55))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def base_slide():
    img = gradient_background((26, 17, 8), (11, 9, 7))
    add_radial_glow(img, W // 2, -80, 520, BTC_ORANGE, strength=95)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=BTC_ORANGE)
    return img, draw


def build_header(draw, y=40):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {DATA['partner_handle']}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=BTC_ORANGE)
    y += 30
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 22


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- reiner Rueckblick, keine Prognose."):
    disclaimer_font = font(B.SANS_BOLD, 17)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 34 - 23 * len(lines) - 10
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 10
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 23
    page_font = font(B.SANS_BOLD, 17)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 10), page_text, font=page_font, fill=MUTED)


def draw_crown(draw, cx, top_y, w=140, h=64):
    left = cx - w / 2
    right = cx + w / 2
    base_y = top_y + h
    band_h = h * 0.32
    points = [
        (left, base_y),
        (left, base_y - band_h),
        (left, top_y + h * 0.15),
        (left + w * 0.25, base_y - band_h - h * 0.3),
        (left + w * 0.5, top_y),
        (left + w * 0.75, base_y - band_h - h * 0.3),
        (right, top_y + h * 0.15),
        (right, base_y - band_h),
        (right, base_y),
    ]
    draw.polygon(points, fill=GOLD_COLOR, outline=CREAM)
    draw.rectangle([left, base_y - band_h, right, base_y], fill=GOLD_COLOR, outline=CREAM)
    for jx in (left, left + w * 0.25, left + w * 0.5, left + w * 0.75, right):
        r = 7
        oy = top_y + h * 0.15 if jx in (left, right) else 0
        draw.ellipse([jx - r, top_y - r + oy, jx + r, top_y + r + oy], fill=CREAM)


def draw_logo_circle(img, draw, cx, cy, r, logo_path, ring_color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=ring_color, width=3)
    logo = Image.open(ROOT / "assets" / logo_path).convert("RGBA")
    target = int(r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def draw_asset_icon(img, cx, cy, r, kind, color):
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=color, width=3)
    if kind == "bar":
        bw, bh = r * 1.1, r * 0.7
        draw.polygon([(cx - bw / 2, cy + bh / 2), (cx + bw / 2, cy + bh / 2),
                      (cx + bw / 2 - 6, cy - bh / 2), (cx - bw / 2 + 6, cy - bh / 2)],
                     fill=color, outline=(60, 50, 20))
    elif kind == "chart":
        pts = [(cx - r * 0.55, cy + r * 0.35), (cx - r * 0.2, cy - r * 0.05),
               (cx + r * 0.1, cy + r * 0.15), (cx + r * 0.5, cy - r * 0.45)]
        draw.line(pts, fill=color, width=6, joint="curve")
        draw.polygon([(cx + r * 0.5, cy - r * 0.45), (cx + r * 0.32, cy - r * 0.45),
                      (cx + r * 0.5, cy - r * 0.2)], fill=color)
    elif kind == "flat":
        draw.line([(cx - r * 0.55, cy + r * 0.1), (cx + r * 0.55, cy - r * 0.05)],
                   fill=color, width=6)
        euro_font = font(B.SANS_BOLD, int(r * 0.7))
        tw = draw.textlength("€", font=euro_font)
        draw.text((cx - tw / 2, cy - r * 0.75), "€", font=euro_font, fill=color)


def mini_chart(img, draw, x, y, w, h, prices_key, line_color, fill_color):
    prices = json.loads((ROOT / "data" / f"demo_{prices_key}_prices.json").read_text(encoding="utf-8"))
    closes = [p["close"] for p in prices]
    lo, hi = min(closes), max(closes)
    span = max(hi - lo, 1e-9)

    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(0, 0, 0, 0), outline=CARD_BORDER, width=1)

    def px(i):
        return x + w * i / (len(closes) - 1)

    def py(v):
        return y + h - h * (v - lo) / span

    points = [(px(i), py(c)) for i, c in enumerate(closes)]
    fill_poly = points + [(points[-1][0], y + h), (points[0][0], y + h)]
    draw.polygon(fill_poly, fill=fill_color)
    draw.line(points, fill=line_color, width=3, joint="curve")


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 96), "COLLAB · 10 JAHRE ZURUECKGEBLICKT", font=eyebrow_font, fill=BTC_ORANGE)

    logo_r = 76
    logo_cx = W // 2
    crown_top = 148
    draw_crown(draw, logo_cx, crown_top, w=148, h=68)
    logo_cy = crown_top + 68 + 16 + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, "btc_logo_icon.png", BTC_ORANGE)
    draw = ImageDraw.Draw(img)

    y = logo_cy + logo_r + 28
    title_font = font(B.SANS_BOLD, 38)
    lines = wrap_text(draw, DATA["title"], title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 46

    y += 8
    sub_font = font(B.SANS_BOLD, 21)
    sub_lines = wrap_text(draw, DATA["subtitle"], sub_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 60)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=BTC_ORANGE)
        y += 28

    y += 20
    row_font = font(B.SANS_BOLD, 17)
    labels = ["GOLD", "SILBER", "AKTIEN", "APPLE", "SPARBUCH"]
    chip_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 4 * 12) / 5
    for i, label in enumerate(labels):
        cx0 = B.MARGIN_LEFT + i * (chip_w + 12)
        draw.rounded_rectangle([cx0, y, cx0 + chip_w, y + 40], radius=10, outline=BTC_ORANGE, width=1)
        tw = draw.textlength(label, font=row_font)
        draw.text((cx0 + chip_w / 2 - tw / 2, y + 11), label, font=row_font, fill=CREAM)
    y += 60

    note_font = font(B.SANS_BOLD, 18)
    note_lines = wrap_text(draw, DATA["asof"], note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, y), line, font=note_font, fill=MUTED)
        y += 25

    draw_footer(draw, 1, 7)
    return img


def slide_row(row, idx, n_total):
    img, draw = base_slide()
    y = build_header(draw)

    color = ASSET_COLORS[row["label"]]

    headline_font = font(B.SANS_BOLD, 28)
    label_title = row["label"].split(" (")[0].title()
    draw.text((B.MARGIN_LEFT, y + 10), f"{label_title} gegen Bitcoin.", font=headline_font, fill=CREAM)
    y += 74

    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 40) / 2
    left_x = B.MARGIN_LEFT
    right_x = B.MARGIN_LEFT + col_w + 40
    icon_r = 34

    draw_asset_icon(img, int(left_x + icon_r + 4), y + icon_r, icon_r, row["kind"], color)
    draw = ImageDraw.Draw(img)
    draw_logo_circle(img, draw, int(right_x + icon_r + 4), y + icon_r, icon_r, "btc_logo_icon.png", BTC_ORANGE)
    draw = ImageDraw.Draw(img)

    label_font = font(B.SANS_BOLD, 15)
    val_font = font(B.SANS_BOLD, 21)
    text_x_l = left_x + icon_r * 2 + 18
    text_x_r = right_x + icon_r * 2 + 18
    draw.text((text_x_l, y + 4), row["label"], font=label_font, fill=color)
    draw.text((text_x_r, y + 4), "BITCOIN", font=label_font, fill=BTC_ORANGE)
    lines_l = wrap_text(draw, row["asset_value"], val_font, col_w - icon_r * 2 - 18)
    ly = y + 26
    for line in lines_l:
        draw.text((text_x_l, ly), line, font=val_font, fill=CREAM)
        ly += 26
    lines_r = wrap_text(draw, row["btc_value"], val_font, col_w - icon_r * 2 - 18)
    ry = y + 26
    for line in lines_r:
        draw.text((text_x_r, ry), line, font=val_font, fill=CREAM)
        ry += 26

    y += icon_r * 2 + 24

    chart_h = 190
    mini_chart(img, draw, left_x, y, col_w, chart_h, row["prices"], color, _fill_for(color))
    mini_chart(img, draw, right_x, y, col_w, chart_h, row["btc_prices"], BTC_ORANGE, _fill_for(BTC_ORANGE))
    y += chart_h + 24

    note_font = font(B.SANS_BOLD, 16)
    note_lines = wrap_text(draw, DATA["note"], note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines[:3]:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=MUTED)
        y += 22

    draw_footer(draw, idx, n_total)
    return img


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _fill_for(color_hex_or_name):
    if isinstance(color_hex_or_name, tuple):
        r, g, b = color_hex_or_name
    else:
        r, g, b = _hex_to_rgb(color_hex_or_name)
    return (int(r * 0.28), int(g * 0.28), int(b * 0.28))


def slide_fazit():
    img, draw = base_slide()
    y = build_header(draw)

    y += 16
    title_font = font(B.SANS_BOLD, 34)
    lines = wrap_text(draw, "Starke Vergangenheits-Rendite,", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 42
    draw.text((B.MARGIN_LEFT, y), "aber auch starke Schwankungen.", font=title_font, fill=CREAM)
    y += 60

    body_font = font(B.SANS_BOLD, 22)
    lines2 = wrap_text(draw, DATA["cta"], body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=BTC_ORANGE)
        y += 30

    y += 26
    note_font = font(B.SANS_BOLD, 22)
    note_lines = wrap_text(draw, f"Schau bei {DATA['partner_handle']} vorbei fuer die Bitcoin-Perspektive "
                                  "auf dieselben Zahlen.", note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=CREAM)
        y += 30

    y += 26
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=BTC_ORANGE, width=3)
    y += 22
    draw.text((B.MARGIN_LEFT, y), "Keine Anlageberatung, keine Prognose --", font=font(B.SANS_BOLD, 21), fill=CREAM)
    y += 29
    draw.text((B.MARGIN_LEFT, y), "nur echte Zahlen aus der Vergangenheit.", font=font(B.SANS_BOLD, 21), fill=CREAM)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_intro]
    for i, row in enumerate(DATA["rows"], start=2):
        slides.append(lambda r=row, i=i: slide_row(r, i, 7))
    slides.append(slide_fazit)

    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, (11, 9, 7))
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 4
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
