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
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

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
    """v3 (2026-10-05): depotdiary-Foto-Schema (Skyline-Foto, Glas-Karten fuer
    Chart und Kennzahlen, vivide Akzentfarbe) statt fast-schwarzer Flaeche mit
    ochre/gruen. Schnittstelle (stock-Dict) unveraendert."""
    key = f"aktiencheck-{DATE_LABEL}-{stock['ticker']}"
    accent = S.accent_for(key)
    img = S.story_background(S.photo_for(key), scrim_from=0.62, scrim_len=0.20)

    # Layout vorab (Glas-Karten muessen VOR dem Text gezeichnet werden)
    chart_w = 840
    chart_h = int(chart_w * 4.7 / 9.6)
    chart_card = (50, 530, S.SW - 50, 530 + chart_h + 40)
    kpi_top = chart_card[3] + 20
    row_h = 64
    card_h = 4 * row_h + 100
    kpi_card = (50, kpi_top, S.SW - 50, kpi_top + card_h)
    img = S.glass(img, [chart_card, kpi_card], radius=24, alpha=182)
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, f"AKTIEN-CHECK   {idx}/{total}", DATE_LABEL[:6])

    # Name, Ticker, Kurs
    draw.text((82, 386), stock["name"].upper(), font=S.font(60), fill=(0, 0, 0))
    draw.text((80, 383), stock["name"].upper(), font=S.font(60), fill=S.CREAM)
    draw.text((82, 464), stock["ticker"], font=S.font(28), fill=(0, 0, 0))
    draw.text((80, 462), stock["ticker"], font=S.font(28), fill=accent)
    price_text = f"{fmt_de(stock['price'])} USD"
    pf = S.font(44)
    pw = draw.textlength(price_text, font=pf)
    draw.text((S.SW - 80 - pw, 392), price_text, font=pf, fill=S.CREAM)
    change = stock["change_pct"]
    ctext = f"{change:+.2f}%".replace(".", ",") + f"  (Stand {stock.get('as_of', DATE_LABEL)})"
    cf = S.font(24)
    cw = draw.textlength(ctext, font=cf)
    draw.text((S.SW - 80 - cw + 2, 454), ctext, font=cf, fill=(0, 0, 0))
    draw.text((S.SW - 80 - cw, 452), ctext, font=cf, fill="#4ADE80" if change >= 0 else "#FF6B6B")

    # Chart
    chart_path = OUTPUT / f"_chart_{stock['ticker']}.png"
    render_chart(stock["csv_path"], accent, chart_path)
    chart_img = Image.open(chart_path).convert("RGBA")
    chart_img = chart_img.resize((chart_w, chart_h))
    img.paste(chart_img, (120, chart_card[1] + 20), chart_img)
    draw = ImageDraw.Draw(img)

    # Kennzahlen-Grid + Range-Bar
    pad = 40
    stats = [
        ("KGV (aktuell)", fmt_de(stock["pe"], 1) if stock.get("pe") else "---"),
        ("KGV (erwartet)", fmt_de(stock["forward_pe"], 1) if stock.get("forward_pe") else "---"),
        ("PEG-Ratio", fmt_de(stock["peg"], 2) if stock.get("peg") else "---"),
        ("Dividendenrendite", f"{fmt_de(stock['div_yield'], 2)} %" if stock.get("div_yield") else "keine"),
        ("Marktkap.", stock["market_cap"]),
        ("Tagesvolumen", stock["volume"]),
        ("Gewinnwachstum (YoY)", f"{stock['earnings_growth']:+.1f} %".replace(".", ",") if stock.get("earnings_growth") is not None else "---"),
        ("Beta (Volatilitaet)", fmt_de(stock["beta"], 2) if stock.get("beta") is not None else "---"),
    ]
    col_w = (kpi_card[2] - kpi_card[0] - 2 * pad) / 2
    for i, (label, value) in enumerate(stats):
        col, row = i % 2, i // 2
        cx = kpi_card[0] + pad + col * col_w
        cy = kpi_top + 22 + row * row_h
        draw.text((cx, cy), label.upper(), font=S.font(17), fill=S.SOFT)
        draw.text((cx, cy + 24), value, font=S.font(26), fill=S.CREAM)

    draw_range_bar(draw, kpi_card[0] + pad, kpi_top + 4 * row_h + 42, kpi_card[2] - kpi_card[0] - 2 * pad,
                    stock["week52_low"], stock["week52_high"], stock["price"], accent)

    # Notiz
    note_f = S.font(22)
    ny = kpi_card[3] + 26
    for line in S.wrap_text(draw, stock["note"], note_f, S.SW - 160)[:3]:
        draw.text((82, ny + 2), line, font=note_f, fill=(0, 0, 0))
        draw.text((80, ny), line, font=note_f, fill=S.CREAM)
        ny += 30

    draw.text((80, S.SAFE_BOTTOM - 62), "Keine Anlageberatung -- nur Zahlen, die ich mir angeschaut habe.",
              font=S.font(20), fill=S.SOFT)
    S.draw_wordmark(img)
    chart_path.unlink(missing_ok=True)
    return img


def main():
    stocks = [
        {"name": "Nike", "ticker": "NKE", "price": 35.84, "change_pct": -1.51, "as_of": "29.09.", "pe": 17.07,
         "forward_pe": 21.01, "peg": 1.40, "div_yield": 4.48, "earnings_growth": 428.0, "beta": 1.11,
         "market_cap": "53,2 Mrd. USD", "volume": "29,0 Mio.", "week52_low": 35.22, "week52_high": 74.51,
         "note": "Notiert nur knapp ueber dem 52-Wochen-Tief (35,22 USD) und rund 52% unter dem Hoch -- dadurch liegt die Dividendenrendite aktuell bei 4,5%.",
         "csv_path": DATA_DIR / "NKE.csv", "accent": OCHRE},
        {"name": "Micron", "ticker": "MU", "price": 1065.08, "change_pct": 1.05, "as_of": "29.09.", "pe": 23.81,
         "forward_pe": 7.02, "peg": 0.16, "div_yield": 0.05, "earnings_growth": 1369.0, "beta": 2.22,
         "market_cap": "1,20 Bio. USD", "volume": "19,7 Mio.", "week52_low": 179.43, "week52_high": 1254.81,
         "note": "Kurs hat sich seit dem 52-Wochen-Tief (179,43 USD) fast versechsfacht. Beta von 2,2: schwankt gut doppelt so stark wie der Gesamtmarkt.",
         "csv_path": DATA_DIR / "MU.csv", "accent": GREEN},
        {"name": "Disney", "ticker": "DIS", "price": 105.41, "change_pct": -0.17, "as_of": "29.09.", "pe": 21.78,
         "forward_pe": 13.81, "peg": 3.37, "div_yield": 1.42, "earnings_growth": -48.3, "beta": 1.41,
         "market_cap": "182,0 Mrd. USD", "volume": "7,3 Mio.", "week52_low": 91.49, "week52_high": 115.42,
         "note": "Bewegt sich seit einem Jahr in einer vergleichsweise engen Spanne (91,49-115,42 USD) -- Quartalsgewinn im Jahresvergleich um 48% gesunken (letztes verfuegbares Quartal).",
         "csv_path": DATA_DIR / "DIS.csv", "accent": CAT_TEAL},
    ]
    for i, stock in enumerate(stocks, start=1):
        img = slide_stock(stock, i, len(stocks))
        img.save(TT_DIR / f"slide_{i}.png")
        if i == 1:
            img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {len(stocks)} Slides in {TT_DIR}")


if __name__ == "__main__":
    main()
