"""Collab mit @btcstrategie -- ueberarbeitet auf Nutzerwunsch vom
2026-09-08: Bitcoin als "Koenig" mit Krone auf der Titelseite, danach
1.000 EUR vor 10 Jahren angelegt in Gold/Silber/Aktien (S&P 500) jeweils
gegen Bitcoin im selben Zeitraum.

WICHTIG zur Compliance: "Koenig der Kryptowaehrungen" ist ein tatsaechlich
gebraeuchlicher, verifizierbarer Spitzname fuer Bitcoin (nicht meine
eigene Bewertung) -- bewusst NICHT als "Bitcoin ist die beste Anlage"
formuliert, das waere eine Bewertung/Empfehlung und damit ein Verstoss
gegen die Account-Regel (siehe CLAUDE.md, vgl. die abgelehnte "HOT-Rating"-
Idee bei collab_aktienanalyst.py). Die Ueberperformance wird als reiner,
einmaliger historischer Rueckblick praesentiert (echte Kurse, ein fest
gewaehlter Zeitraum), explizit mit Volatilitaets-Hinweis im Fazit --
nicht als Kaufargument.

Aufruf:
  python posts/collab_btcstrategie_backtest.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "collab_btcstrategie_backtest"
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
GREEN = B.GREEN_MID
BTC_ORANGE = "#F7931A"
GOLD_COLOR = "#D4AF37"
SILVER_COLOR = "#C0C0C8"

OWN_HANDLE = "@DASDEPOTDIARY"

DATA = json.loads((ROOT / "posts" / "inputs" / "collab_btcstrategie_backtest.json").read_text(encoding="utf-8"))["meta"]

ASSET_COLORS = {"GOLD": GOLD_COLOR, "SILBER": SILVER_COLOR, "AKTIEN (S&P 500)": GREEN}


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


def build_header(draw, y=40):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {DATA['partner_handle']}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=BTC_ORANGE)
    y += 30
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 22


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- reiner Rueckblick, keine Prognose."):
    disclaimer_font = font(B.SANS_BOLD, 18)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 40 - 26 * len(lines) - 12
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 12
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 26
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 12), page_text, font=page_font, fill=MUTED)


def base_slide():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=BTC_ORANGE)
    return img, draw


def draw_crown(draw, cx, top_y, w=140, h=64):
    """Einfache Kronen-Silhouette (Gold) -- sitzt ueber dem Bitcoin-Logo auf
    der Titelseite, passend zum "Koenig der Kryptowaehrungen"-Spitznamen."""
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
        draw.ellipse([jx - r, top_y - r + (h * 0.15 if jx in (left, right) else 0),
                      jx + r, top_y + r + (h * 0.15 if jx in (left, right) else 0)], fill=CREAM)


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


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 96), "COLLAB · 10 JAHRE ZURUECKGEBLICKT", font=eyebrow_font, fill=BTC_ORANGE)

    logo_r = 78
    logo_cx = W // 2
    crown_top = 150
    draw_crown(draw, logo_cx, crown_top, w=150, h=70)
    logo_cy = crown_top + 70 + 18 + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, "btc_logo_icon.png", BTC_ORANGE)
    draw = ImageDraw.Draw(img)

    y = logo_cy + logo_r + 30
    title_font = font(B.SANS_BOLD, 40)
    lines = wrap_text(draw, DATA["title"], title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 48

    y += 10
    sub_font = font(B.SANS_BOLD, 23)
    sub_lines = wrap_text(draw, DATA["subtitle"], sub_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 80)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=BTC_ORANGE)
        y += 30

    y += 24
    note_font = font(B.SANS_BOLD, 18)
    note_lines = wrap_text(draw, DATA["asof"], note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, y), line, font=note_font, fill=MUTED)
        y += 25

    draw_footer(draw, 1, 5)
    return img


def slide_row(row, idx, n_total):
    img, draw = base_slide()
    y = build_header(draw)

    color = ASSET_COLORS[row["label"]]
    kind = "chart" if row["label"].startswith("AKTIEN") else "bar"

    headline_font = font(B.SANS_BOLD, 32)
    draw.text((B.MARGIN_LEFT, y + 14), f"{row['label'].title()} gegen Bitcoin.", font=headline_font, fill=CREAM)
    y += 90

    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 40) / 2
    left_x = B.MARGIN_LEFT
    right_x = B.MARGIN_LEFT + col_w + 40
    icon_r = 44

    draw_asset_icon(img, int(left_x + col_w / 2), y + icon_r, icon_r, kind, color)
    draw = ImageDraw.Draw(img)
    draw_logo_circle(img, draw, int(right_x + col_w / 2), y + icon_r, icon_r, "btc_logo_icon.png", BTC_ORANGE)
    draw = ImageDraw.Draw(img)
    y += icon_r * 2 + 20

    label_font = font(B.SANS_BOLD, 16)
    lt = row["label"]
    ltw = draw.textlength(lt, font=label_font)
    draw.text((left_x + col_w / 2 - ltw / 2, y), lt, font=label_font, fill=color)
    rtw = draw.textlength("BITCOIN", font=label_font)
    draw.text((right_x + col_w / 2 - rtw / 2, y), "BITCOIN", font=label_font, fill=BTC_ORANGE)
    y += 30

    val_font = font(B.SANS_BOLD, 24)
    lines_l = wrap_text(draw, row["asset_value"], val_font, col_w)
    ly = y
    for line in lines_l:
        lw = draw.textlength(line, font=val_font)
        draw.text((left_x + col_w / 2 - lw / 2, ly), line, font=val_font, fill=CREAM)
        ly += 30
    lines_r = wrap_text(draw, row["btc_value"], val_font, col_w)
    ry = y
    for line in lines_r:
        rw = draw.textlength(line, font=val_font)
        draw.text((right_x + col_w / 2 - rw / 2, ry), line, font=val_font, fill=CREAM)
        ry += 30

    y = max(ly, ry) + 30
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    y += 20
    note_font = font(B.SANS_BOLD, 18)
    note_lines = wrap_text(draw, DATA["note"], note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=MUTED)
        y += 25

    draw_footer(draw, idx, n_total)
    return img


def slide_fazit():
    img, draw = base_slide()
    y = build_header(draw)

    y += 20
    title_font = font(B.SANS_BOLD, 36)
    lines = wrap_text(draw, "Starke Vergangenheits-Rendite,", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 46
    draw.text((B.MARGIN_LEFT, y), "aber auch starke Schwankungen.", font=title_font, fill=CREAM)
    y += 66

    body_font = font(B.SANS_BOLD, 24)
    lines2 = wrap_text(draw, DATA["cta"], body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=BTC_ORANGE)
        y += 32

    y += 30
    note_font = font(B.SANS_BOLD, 24)
    note_lines = wrap_text(draw, f"Schau bei {DATA['partner_handle']} vorbei fuer die Bitcoin-Perspektive "
                                  "auf dieselben Zahlen.", note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=CREAM)
        y += 32

    y += 30
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=BTC_ORANGE, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Keine Anlageberatung, keine Prognose --", font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur echte Zahlen aus der Vergangenheit.", font=font(B.SANS_BOLD, 22), fill=CREAM)

    draw_footer(draw, 5, 5)
    return img


def main():
    slides = [slide_intro]
    for i, row in enumerate(DATA["rows"], start=2):
        slides.append(lambda r=row, i=i: slide_row(r, i, 5))
    slides.append(slide_fazit)

    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    gap = 16
    sheet = Image.new("RGB", (W * n + gap * (n + 1), H + gap * 2), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        sheet.paste(im, (gap + (i - 1) * (W + gap), gap))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
