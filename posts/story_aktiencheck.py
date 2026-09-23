"""Taegliches Story-Format "AKTIEN-CHECK" -- eine volle Story-Slide pro Aktie
(story_sequence), mit echtem Kurschart (matplotlib, aus lokal abgelegten
Tagesschlusskursen) plus Fundamentaldaten. Reine Fakten (Kurs, KGV, Marktkap,
52W-Range) -- keine Kaufempfehlung, keine Kursziele.

v2 (2026-09-15, Nutzer-Feedback "Farben nicht optimal" + "brauche Charts"):
warmes Dunkel-Palette passend zur Marke (Ochre/Gruen statt Blau) statt der
ersten Blau-Version; echter Kurschart statt nur 52W-Positionsbalken; eine
ganze Slide pro Aktie statt drei Karten auf einer Slide.

Input: Liste von Dicts mit name, ticker, price, change_pct, pe, market_cap,
week52_low, week52_high, note, csv_path (lokale Datei mit timestamp,close).

Aufruf (Prototyp/Test):
  python posts/story_aktiencheck.py
"""
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "story_aktiencheck"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
DATA_DIR = OUTPUT / "data"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (6, 6, 6)
BG_BOTTOM = (0, 0, 0)
CARD = "#141414"
CARD_BORDER = "#2E2E2E"
CREAM = "#F5F5F3"
MUTED = "#8F8F8C"
GREEN = "#5CA87F"
RED = "#C25C51"
OCHRE = "#D4AF4A"
CAT_TEAL = "#4FBFB5"

OWN_HANDLE = "@DASDEPOTDIARY"
DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def font(path, size):
    return ImageFont.truetype(path, size)


def fmt_de(value, decimals=2):
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def gradient_background(tint_hex=None, tint_strength=0.05):
    """Fast schwarz, aber pro Aktie leicht in Richtung ihrer Akzentfarbe
    eingefaerbt -- Nutzer-Feedback 2026-09-15: 'ein bisschen eine
    Veraenderung, andere Hintergrundfarbe' bei gleichzeitig schwarzer Basis."""
    top, bottom = BG_TOP, BG_BOTTOM
    if tint_hex:
        tr, tg, tb = _hex_to_rgb(tint_hex)
        top = tuple(int(top[i] + (tr, tg, tb)[i] * tint_strength) for i in range(3))
        bottom = tuple(int(bottom[i] + (tr, tg, tb)[i] * (tint_strength * 0.4)) for i in range(3))
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_glow(img, cx, cy, radius, color, strength=45):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.6))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def render_chart(csv_path, accent_hex, out_path, days=90):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        next(f)
        for line in f:
            ts, close = line.strip().split(",")
            rows.append((ts, float(close)))
    rows.sort(key=lambda r: r[0])
    rows = rows[-days:]
    closes = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(9.6, 4.7), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    x = list(range(len(closes)))
    line_color = accent_hex
    ax.plot(x, closes, color=line_color, linewidth=3.5, solid_capstyle="round")
    ax.fill_between(x, closes, min(closes) * 0.97, color=line_color, alpha=0.12)

    ax.set_xlim(0, len(closes) - 1)
    ax.set_ylim(min(closes) * 0.97, max(closes) * 1.03)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.tick_params(axis="y", colors=MUTED, labelsize=15)
    ax.yaxis.set_major_formatter(lambda v, pos: fmt_de(v, 0))
    ax.grid(axis="y", color="#3A352C", linewidth=0.6, alpha=0.5)

    plt.tight_layout(pad=0.3)
    fig.savefig(out_path, transparent=True)
    plt.close(fig)


def build_header(draw, y, idx, total):
    handle_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=CREAM)
    y += 32
    title_font = font(B.SANS_BOLD, 44)
    draw.text((B.MARGIN_LEFT, y), "AKTIEN-CHECK", font=title_font, fill=CREAM)
    y += 56
    date_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), f"{DATE_LABEL} -- {idx}/{total}", font=date_font, fill=MUTED)
    y += 38
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 44


def draw_range_bar(draw, x, y, w, low, high, current, accent):
    bar_h = 8
    draw.rounded_rectangle([x, y, x + w, y + bar_h], radius=4, fill="#2A2620")
    pos = max(0.0, min(1.0, (current - low) / (high - low))) if high > low else 0.5
    marker_x = x + w * pos
    draw.ellipse([marker_x - 9, y + bar_h / 2 - 9, marker_x + 9, y + bar_h / 2 + 9], fill=accent, outline=CREAM, width=2)
    label_font = font(B.SANS_BOLD, 16)
    draw.text((x, y + bar_h + 10), f"52W-Tief {fmt_de(low)}", font=label_font, fill=MUTED)
    hi_text = f"52W-Hoch {fmt_de(high)}"
    hw = draw.textlength(hi_text, font=label_font)
    draw.text((x + w - hw, y + bar_h + 10), hi_text, font=label_font, fill=MUTED)


def slide_stock(stock, idx, total):
    accent = stock.get("accent", OCHRE)
    img = gradient_background(tint_hex=accent, tint_strength=0.06)
    add_glow(img, W * 0.5, -100, 620, (40, 40, 40), strength=22)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=accent)

    y = build_header(draw, 64, idx, total)
    y += 60

    name_font = font(B.SANS_BOLD, 48)
    ticker_font = font(B.SANS_BOLD, 24)
    draw.text((B.MARGIN_LEFT, y), stock["name"], font=name_font, fill=CREAM)
    y += 60
    draw.text((B.MARGIN_LEFT, y), stock["ticker"], font=ticker_font, fill=accent)

    price_font = font(B.SANS_BOLD, 40)
    price_text = f"{fmt_de(stock['price'])} USD"
    pw = draw.textlength(price_text, font=price_font)
    draw.text((W - B.MARGIN_RIGHT - pw, y - 36), price_text, font=price_font, fill=CREAM)
    change = stock["change_pct"]
    change_font = font(B.SANS_BOLD, 22)
    change_text = f"{change:+.2f}% (Stand {stock.get('as_of', DATE_LABEL)})"
    cw = draw.textlength(change_text, font=change_font)
    change_color = GREEN if change >= 0 else RED
    draw.text((W - B.MARGIN_RIGHT - cw, y + 14), change_text, font=change_font, fill=change_color)
    y += 70

    # Chart
    chart_path = OUTPUT / f"_chart_{stock['ticker']}.png"
    render_chart(stock["csv_path"], accent, chart_path)
    chart_img = Image.open(chart_path).convert("RGBA")
    chart_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    chart_h = int(chart_img.height * chart_w / chart_img.width)
    chart_img = chart_img.resize((chart_w, chart_h))
    img.paste(chart_img, (B.MARGIN_LEFT, y), chart_img)
    y += chart_h + 24

    # Fundamentaldaten-Karte: 2x3-Kennzahlen-Grid + Range-Bar
    pad = 28
    stats = [
        ("KGV (aktuell)", fmt_de(stock["pe"], 1) if stock.get("pe") else "---"),
        ("KGV (erwartet)", fmt_de(stock["forward_pe"], 1) if stock.get("forward_pe") else "---"),
        ("PEG-Ratio", fmt_de(stock["peg"], 2) if stock.get("peg") else "---"),
        ("Dividendenrendite", f"{fmt_de(stock['div_yield'], 2)} %" if stock.get("div_yield") else "keine"),
        ("Marktkap.", stock["market_cap"]),
        ("Tagesvolumen", stock["volume"]),
        ("Gewinnwachstum (YoY)", f"{stock['earnings_growth']:+.1f} %" if stock.get("earnings_growth") is not None else "---"),
        ("Beta (Volatilitaet)", fmt_de(stock["beta"], 2) if stock.get("beta") is not None else "---"),
    ]
    row_h = 64
    grid_h = 4 * row_h
    card_h = grid_h + 100
    draw.rounded_rectangle([B.MARGIN_LEFT, y, W - B.MARGIN_RIGHT, y + card_h], radius=16, fill=CARD, outline=CARD_BORDER, width=1)

    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 2 * pad) / 2
    label_font = font(B.SANS_BOLD, 17)
    value_font = font(B.SANS_BOLD, 25)
    for i, (label, value) in enumerate(stats):
        col = i % 2
        row = i // 2
        cx = B.MARGIN_LEFT + pad + col * col_w
        cy = y + 24 + row * row_h
        draw.text((cx, cy), label.upper(), font=label_font, fill=MUTED)
        draw.text((cx, cy + 24), value, font=value_font, fill=CREAM)

    draw_range_bar(draw, B.MARGIN_LEFT + pad, y + grid_h + 44, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 2 * pad,
                    stock["week52_low"], stock["week52_high"], stock["price"], accent)

    note_font = font(B.SANS_BOLD, 19)
    words = stock["note"].split()
    lines, cur = [], ""
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 2 * pad
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=note_font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    ny = y + card_h + 30
    for line in lines[:3]:
        draw.text((B.MARGIN_LEFT, ny), line, font=note_font, fill=MUTED)
        ny += 26

    text = "Keine Anlageberatung -- nur Zahlen, die ich mir angeschaut habe."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=CARD_BORDER, width=1)
    draw.text((B.MARGIN_LEFT, H - 68), text, font=disclaimer_font, fill=MUTED)

    chart_path.unlink(missing_ok=True)
    return img


def main():
    stocks = [
        {"name": "Oracle", "ticker": "ORCL", "price": 144.56, "change_pct": -3.11, "as_of": "23.09.", "pe": 23.42,
         "forward_pe": 18.25, "peg": 0.83, "div_yield": 1.35, "earnings_growth": 54.5, "beta": 1.73,
         "market_cap": "451,1 Mrd. USD", "volume": "22,1 Mio.", "week52_low": 114.50, "week52_high": 319.46,
         "note": "Groesster Tagesverlust der drei (-3,1%) an einem insgesamt schwachen Tag fuer Tech-Werte. Gewinn im letzten Quartal YoY deutlich gestiegen (+54,5%).",
         "csv_path": DATA_DIR / "ORCL.csv", "accent": OCHRE},
        {"name": "McDonald's", "ticker": "MCD", "price": 238.34, "change_pct": -4.80, "as_of": "23.09.", "pe": 20.32,
         "forward_pe": 17.76, "peg": 2.14, "div_yield": 2.97, "earnings_growth": 5.7, "beta": 0.41,
         "market_cap": "177,2 Mrd. USD", "volume": "16,5 Mio.", "week52_low": 234.04, "week52_high": 335.18,
         "note": "Zweitgroesster Tagesverlust der drei (-4,8%), heute neues 52-Wochen-Tief markiert -- am Tag der Ankuendigung von 8,5 Mrd. USD fuer die Modernisierung von Franchise-Restaurants.",
         "csv_path": DATA_DIR / "MCD.csv", "accent": GREEN},
        {"name": "JPMorgan Chase", "ticker": "JPM", "price": 337.68, "change_pct": -0.68, "as_of": "23.09.", "pe": 14.57,
         "forward_pe": 14.08, "peg": 1.64, "div_yield": 1.70, "earnings_growth": 46.9, "beta": 0.98,
         "market_cap": "903,8 Mrd. USD", "volume": "7,0 Mio.", "week52_low": 276.44, "week52_high": 366.50,
         "note": "Geringste Tagesbewegung der drei (-0,7%) an einem Tag, an dem Anleger aus einzelnen Tech-Werten in Bankaktien rotierten. Mit Abstand niedrigstes KGV im Vergleich (14,6).",
         "csv_path": DATA_DIR / "JPM.csv", "accent": CAT_TEAL},
    ]
    for i, stock in enumerate(stocks, start=1):
        img = slide_stock(stock, i, len(stocks))
        img.save(TT_DIR / f"slide_{i}.png")
        if i == 1:
            img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {len(stocks)} Slides in {TT_DIR}")


if __name__ == "__main__":
    main()
