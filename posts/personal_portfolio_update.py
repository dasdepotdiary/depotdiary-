"""Eigenstaendiges "Daten-Karte"-Format fuer persoenliche Depot-Updates
(Kauf/Verkauf/Limit-Order) -- keine Collab, nur mein eigener Account.

Herkunft: extrahiert aus posts/collab_aktienanalyst.py (dort war das Format
noch an den Collab-Header/die Dual-Branding-Logik gebunden). Hier bewusst
vereinfacht auf ein-Account-Framing: EYEBROW zeigt die Aktion (VERKAUFT,
LIMIT-ORDER, TEILVERKAUF), keine "PICK VON"-Zeile mehr.

Rein faktisch (Kurs, KGV, Marktkap., 52W-Range, echter Kurs-Chart) + meine
eigene Begruendung in Ich-Form -- keine Kursziele, keine Kauf-/Verkaufs-
empfehlung (siehe CLAUDE.md-Regel).

Aufruf:
  python posts/personal_portfolio_update.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "personal_portfolio_update"
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
GREEN_MID = B.GREEN_MID
GOLD = "#C9A24B"
RED = "#C0392B"
CHART_LINE = "#C9A24B"
CHART_FILL = "#2A2416"

OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "DEPOT-UPDATE"

POSITIONS = [
    {
        "action": "VERKAUFT BEI ~160 EUR", "action_color": RED,
        "ticker": "PLTR", "wkn": "A2GS8V", "name": "Palantir",
        "logo_path": ROOT / "assets" / "pltr_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_PLTR_prices.json",
        "stats": [
            ("KURS", "182,53 USD"), ("KGV", "154,1"), ("KGV (FWD)", "97,9"),
            ("MARKTKAP.", "439,5 Mrd. USD"), ("52W-HOCH", "207,52 USD"), ("52W-TIEF", "106,37 USD"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 207,52 USD, 52W-Tief 106,37 USD",
        "reasoning": [
            "Ich hab Palantir bei 160 Euro verkauft -- die Bewertung war mir",
            "zu hoch geworden. Ich wollte auch wieder etwas Cash-Liquiditaet",
            "haben, falls die Kurse insgesamt nochmal tiefer gehen. War bei",
            "mir ohnehin keine grosse Position.",
        ],
    },
    {
        "action": "LIMIT-ORDER UNTER 300 EUR", "action_color": GOLD,
        "ticker": "AVGO", "wkn": "A4Z3V5", "name": "Broadcom",
        "logo_path": ROOT / "assets" / "avgo_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_AVGO_prices.json",
        "stats": [
            ("KURS", "357,16 USD"), ("KGV", "45,6"), ("MARKTKAP.", "1,77 Bio. USD"),
            ("52W-HOCH", "495,00 USD"), ("52W-TIEF", "289,96 USD"), ("STATUS", "offen"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 495,00 USD, 52W-Tief 289,96 USD",
        "reasoning": [
            "Ich hab eine Limit-Order fuer Broadcom unter 300 Euro gesetzt --",
            "zu dem Preis finde ich die Bewertung extrem attraktiv. Noch nicht",
            "ausgefuehrt, ich warte einfach ab.",
        ],
    },
    {
        "action": "TEILVERKAUF", "action_color": GOLD,
        "ticker": "ZETA", "wkn": "A2QG9G", "name": "Zeta Global",
        "logo_path": ROOT / "assets" / "zeta_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_ZETA_prices.json",
        "stats": [
            ("KURS", "32,68 USD"), ("KGV", "43,5"), ("KGV (FWD)", "25,8"),
            ("MARKTKAP.", "7,76 Mrd. USD"), ("UMSATZ-WACHSTUM", "+35,9%"), ("52W-HOCH", "32,75 USD"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 32,75 USD, 52W-Tief 14,37 USD",
        "reasoning": [
            "Bei Zeta Global verkauf ich einen Teil -- die Aktie ist zuletzt",
            "sehr gut gelaufen, und ich frag mich, ob sich das Tempo so",
            "fortsetzen laesst. Ein Teilverkauf nach starkem Lauf fuehlt sich",
            "fuer mich richtig an.",
        ],
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_logo_circle(img, draw, cx, cy, r, logo_path):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=GOLD, width=2)
    logo = Image.open(logo_path).convert("RGBA")
    target = int(r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def draw_stat_box(draw, x, y, w, h, label, value):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD, outline=CARD_BORDER, width=1)
    label_font = font(B.SANS_BOLD, 15)
    value_font = font(B.SANS_BOLD, 24)
    lw = draw.textlength(label, font=label_font)
    vw = draw.textlength(value, font=value_font)
    while lw > w - 16 and label_font.size > 10:
        label_font = font(B.SANS_BOLD, label_font.size - 1)
        lw = draw.textlength(label, font=label_font)
    while vw > w - 16 and value_font.size > 14:
        value_font = font(B.SANS_BOLD, value_font.size - 1)
        vw = draw.textlength(value, font=value_font)
    draw.text((x + w / 2 - lw / 2, y + 12), label, font=label_font, fill=MUTED)
    draw.text((x + w / 2 - vw / 2, y + 34), value, font=value_font, fill=GOLD)


def draw_price_chart(draw, x, y, w, h, prices_path, note):
    prices = json.loads(Path(prices_path).read_text(encoding="utf-8"))
    closes = [p["close"] for p in prices]
    lo, hi = min(closes), max(closes)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD, outline=CARD_BORDER, width=1)
    pad = 20
    chart_top, chart_bottom = y + pad + 30, y + h - pad - 56
    chart_left, chart_right = x + pad, x + w - pad
    span = max(hi - lo, 0.01)

    def px(i):
        return chart_left + (chart_right - chart_left) * i / (len(closes) - 1)

    def py(v):
        return chart_bottom - (chart_bottom - chart_top) * (v - lo) / span

    points = [(px(i), py(c)) for i, c in enumerate(closes)]
    fill_poly = points + [(points[-1][0], chart_bottom), (points[0][0], chart_bottom)]
    draw.polygon(fill_poly, fill=CHART_FILL)
    draw.line(points, fill=CHART_LINE, width=3, joint="curve")

    small_font = font(B.SANS_BOLD, 16)
    draw.text((chart_left, chart_top - 26), f"{hi:.2f} USD", font=small_font, fill=MUTED)
    draw.text((chart_left, chart_bottom + 6), f"{lo:.2f} USD", font=small_font, fill=MUTED)
    note_font = font(B.SANS_BOLD, 15)
    draw.text((x + pad, y + h - pad - 20), note, font=note_font, fill=MUTED)


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


def build_header(draw, subtitle=SERIES_TITLE):
    y = 40
    handle_font = font(B.SANS_BOLD, 19)
    title_font = font(B.SANS_BOLD, 21)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=GOLD)
    y += 30
    draw.text((B.MARGIN_LEFT, y), subtitle, font=title_font, fill=CREAM)
    y += 32
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 22


def build_intro():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    build_header(draw, subtitle="NEUE FOLGE")
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    y = 460
    draw.text((B.MARGIN_LEFT, y), "Depot-Update.", font=font(B.SANS_BOLD, 62), fill=CREAM)
    y += 82
    draw.text((B.MARGIN_LEFT, y), "Was sich diese Woche bei mir getan hat.", font=font(B.SANS_BOLD, 32), fill=GOLD)

    disclaimer_font = font(B.SANS_BOLD, 24)
    disclaimer_lines = wrap_text(draw, "Keine Anlageberatung -- nur, was ich selbst gemacht habe.",
                                  disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    dy = H - 40 - 32 * len(disclaimer_lines)
    for line in disclaimer_lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 32
    return img


def build_position_slide(pos, idx, n_total):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    y = build_header(draw)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    draw.text((B.MARGIN_LEFT, y), pos["action"], font=font(B.SANS_BOLD, 17), fill=pos["action_color"])
    y += 30

    logo_r = 44
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = y + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, pos["logo_path"])
    name_x = logo_cx + logo_r + 22
    name_font_size = 34 if len(pos["name"]) < 20 else 26
    draw.text((name_x, y + 4), pos["name"], font=font(B.SANS_BOLD, name_font_size), fill=CREAM)
    draw.text((name_x, y + 48), f"{pos['ticker']}  ·  WKN {pos['wkn']}",
               font=font(B.SANS_BOLD, 18), fill=MUTED)

    y = logo_cy + logo_r + 22
    cols = 3
    gap = 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 66
    for i, (label, value) in enumerate(pos["stats"]):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)
    rows = (len(pos["stats"]) + cols - 1) // cols
    y += rows * (box_h + gap)

    y += 14
    chart_h = 340
    draw_price_chart(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, chart_h,
                      pos["prices_path"], pos["chart_note"])
    y += chart_h + 32

    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=GOLD, width=3)
    y += 24
    body_font = font(B.SANS_BOLD, 22)
    for line in pos["reasoning"]:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33

    disclaimer_font = font(B.SANS_BOLD, 28)
    disclaimer_lines = wrap_text(draw, "Keine Anlageberatung -- nur, was ich selbst gemacht habe.",
                                  disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 140)
    divider_y = H - 44 - 34 * len(disclaimer_lines) - 14
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 14
    for line in disclaimer_lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 34
    page_font = font(B.SANS_BOLD, 28)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 14), page_text, font=page_font, fill=MUTED)

    return img


def main():
    n = len(POSITIONS) + 1
    build_intro().save(IG_DIR / "slide_1.png")
    for i, pos in enumerate(POSITIONS, start=2):
        build_position_slide(pos, i, n).save(IG_DIR / f"slide_{i}.png")

    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = min(4, n)
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
