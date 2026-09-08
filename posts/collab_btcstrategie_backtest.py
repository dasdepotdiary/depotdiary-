"""Collab mit @btcstrategie: "1.000EUR vor 1/3/5 Jahren -- Aktien oder
Bitcoin?" -- auf Nutzerwunsch vom 2026-09-08 (Partner-Account per
WhatsApp-Screenrecording identifiziert: @btcstrategie, Stuttgart,
Bitcoin-Erklaer-Content).

Reiner historischer Backtest, echte Schlusskurse (S&P 500, Bitcoin,
EUR/USD zur Waehrungsumrechnung, Yahoo Finance) -- explizit als
Rueckblick markiert, KEINE Prognose, keine Kaufempfehlung fuer eine der
beiden Anlageklassen. Ergebnis ist bewusst nicht einseitig (1 Jahr:
Aktien vorn, 3 Jahre: Bitcoin vorn, 5 Jahre: fast gleichauf).

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

OWN_HANDLE = "@DASDEPOTDIARY"

DATA = json.loads((ROOT / "posts" / "inputs" / "collab_btcstrategie_backtest.json").read_text(encoding="utf-8"))["meta"]


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


def draw_vs_box(draw, x, y, w, h, label, value, color):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD, outline=color, width=2)
    label_font = font(B.SANS_BOLD, 18)
    draw.text((x + 24, y + 22), label, font=label_font, fill=color)
    value_font = font(B.SANS_BOLD, 34)
    lines = wrap_text(draw, value, value_font, w - 48)
    vy = y + 62
    for line in lines:
        draw.text((x + 24, vy), line, font=value_font, fill=CREAM)
        vy += 42


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 110), "COLLAB · BACKTEST", font=eyebrow_font, fill=BTC_ORANGE)

    title_font = font(B.SANS_BOLD, 46)
    lines = wrap_text(draw, DATA["title"], title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    y = 160
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 56

    y += 20
    sub_font = font(B.SANS_BOLD, 24)
    sub_lines = wrap_text(draw, DATA["subtitle"], sub_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in sub_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=sub_font, fill=BTC_ORANGE)
        y += 32

    y += 40
    legend_font = font(B.SANS_BOLD, 20)
    draw.rounded_rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + 26, y + 26], radius=6, fill=GREEN)
    draw.text((B.MARGIN_LEFT + 38, y + 2), "S&P 500 (Aktienmarkt)", font=legend_font, fill=CREAM)
    y += 42
    draw.rounded_rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + 26, y + 26], radius=6, fill=BTC_ORANGE)
    draw.text((B.MARGIN_LEFT + 38, y + 2), "Bitcoin", font=legend_font, fill=CREAM)

    draw_footer(draw, 1, 5)
    return img


def slide_row(row, idx, n_total):
    img, draw = base_slide()
    y = build_header(draw)

    headline_font = font(B.SANS_BOLD, 38)
    draw.text((B.MARGIN_LEFT, y + 20), f"1.000 € {row['label'].replace('VOR ', 'vor ').lower()}.", font=headline_font, fill=CREAM)
    y += 100

    box_h = 130
    draw_vs_box(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, box_h, "AKTIEN (S&P 500)", row["stocks"], GREEN)
    y += box_h + 16
    draw_vs_box(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, box_h, "BITCOIN", row["btc"], BTC_ORANGE)
    y += box_h + 40

    note_font = font(B.SANS_BOLD, 19)
    note_lines = wrap_text(draw, DATA["note"], note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=MUTED)
        y += 26

    draw_footer(draw, idx, n_total)
    return img


def slide_fazit():
    img, draw = base_slide()
    y = build_header(draw)

    y += 20
    title_font = font(B.SANS_BOLD, 38)
    lines = wrap_text(draw, "Der Zeitraum entscheidet mehr", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 48
    draw.text((B.MARGIN_LEFT, y), "als die Anlageklasse.", font=title_font, fill=CREAM)
    y += 70

    body_font = font(B.SANS_BOLD, 24)
    body_lines = wrap_text(draw, DATA["cta"], body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in body_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=BTC_ORANGE)
        y += 32

    y += 40
    note_font = font(B.SANS_BOLD, 24)
    note_lines = wrap_text(draw, f"Schau bei {DATA['partner_handle']} vorbei fuer die Bitcoin-Perspektive "
                                  "auf dieselben Zahlen.", note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=CREAM)
        y += 32

    y += 40
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

    cols = 5
    gap = 16
    sheet = Image.new("RGB", (W * n + gap * (n + 1), H + gap * 2), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        sheet.paste(im, (gap + (i - 1) * (W + gap), gap))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
