"""Taegliches Story-Format "MEINE WATCHLIST" -- eine Aktie/Kryptowaehrung,
die der Nutzer selbst beobachtet, inkl. seiner eigenen (verbatim-nahen)
Begruendung. Klar als persoenliche Beobachtung gekennzeichnet, keine
Kaufempfehlung. Teilt sich Chart-/Card-Bausteine mit story_aktiencheck.py.

Input pro Eintrag: name, ticker, kind ("stock"|"crypto"), price, change_pct,
csv_path, quote (Nutzer-eigene Begruendung), plus je nach kind
Fundamentaldaten (stock: pe, forward_pe, peg, div_yield, market_cap, volume;
crypto: market_cap, range_note).

Aufruf (Prototyp/Test):
  python posts/story_watchlist.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import (
    font, fmt_de, gradient_background, add_glow, render_chart,
    draw_range_bar, build_header, CARD, CARD_BORDER, CREAM, MUTED, GREEN, RED,
    OCHRE, CAT_TEAL, W, H, OUTPUT as _AKTIENCHECK_OUTPUT,
)

NAME = "story_watchlist"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
DATA_DIR = Path(__file__).parent.parent / "output" / "story_aktiencheck" / "data"
TT_DIR.mkdir(parents=True, exist_ok=True)

DATE_LABEL = date.today().strftime("%d.%m.%Y")


def draw_watchlist_header(draw, y, weekday_label, date_label):
    handle_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY", font=handle_font, fill=CREAM)
    y += 32
    title_font = font(B.SANS_BOLD, 44)
    draw.text((B.MARGIN_LEFT, y), "MEINE WATCHLIST", font=title_font, fill=CREAM)
    y += 56
    date_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), f"{weekday_label}, {date_label}", font=date_font, fill=MUTED)
    y += 38
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 40


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def slide_watchlist(entry, weekday_label):
    img = gradient_background()
    add_glow(img, W * 0.5, -100, 620, (40, 40, 40), strength=22)
    draw = ImageDraw.Draw(img)
    accent = entry.get("accent", OCHRE)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=accent)

    y = draw_watchlist_header(draw, 64, weekday_label, entry["date_label"])
    y += 44

    name_font = font(B.SANS_BOLD, 48)
    ticker_font = font(B.SANS_BOLD, 24)
    draw.text((B.MARGIN_LEFT, y), entry["name"], font=name_font, fill=CREAM)
    y += 60
    draw.text((B.MARGIN_LEFT, y), entry["ticker"], font=ticker_font, fill=accent)

    price_font = font(B.SANS_BOLD, 40)
    price_text = f"{fmt_de(entry['price'])} {entry.get('currency', 'USD')}"
    pw = draw.textlength(price_text, font=price_font)
    draw.text((W - B.MARGIN_RIGHT - pw, y - 36), price_text, font=price_font, fill=CREAM)
    change = entry["change_pct"]
    change_font = font(B.SANS_BOLD, 22)
    change_text = f"{change:+.2f}% (Stand {entry['as_of']})"
    cw = draw.textlength(change_text, font=change_font)
    change_color = GREEN if change >= 0 else RED
    draw.text((W - B.MARGIN_RIGHT - cw, y + 14), change_text, font=change_font, fill=change_color)
    y += 70

    chart_path = OUTPUT / f"_chart_{entry['ticker']}.png"
    render_chart(entry["csv_path"], accent, chart_path)
    chart_img = Image.open(chart_path).convert("RGBA")
    chart_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    chart_h = int(chart_img.height * chart_w / chart_img.width)
    chart_img = chart_img.resize((chart_w, chart_h))
    img.paste(chart_img, (B.MARGIN_LEFT, y), chart_img)
    y += chart_h + 24

    pad = 28
    if entry["kind"] == "stock":
        stats = [
            ("KGV (aktuell)", fmt_de(entry["pe"], 1)),
            ("KGV (erwartet)", fmt_de(entry["forward_pe"], 1) if entry.get("forward_pe") else "---"),
            ("PEG-Ratio", fmt_de(entry["peg"], 2) if entry.get("peg") else "---"),
            ("Dividendenrendite", f"{fmt_de(entry['div_yield'], 2)} %" if entry.get("div_yield") else "keine"),
            ("Marktkap.", entry["market_cap"]),
            ("Tagesvolumen", entry["volume"]),
        ]
    else:
        stats = [
            ("Marktkap. (ca.)", entry["market_cap"]),
            ("7-Tage-Veraenderung", f"{entry['change_7d']:+.2f} %"),
            ("Tief (dargestellt)", f"{fmt_de(entry['range_low'])} USD"),
            ("Hoch (dargestellt)", f"{fmt_de(entry['range_high'])} USD"),
        ]

    rows = (len(stats) + 1) // 2
    row_h = 64
    grid_h = rows * row_h
    card_h = grid_h + 40
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
    y += card_h + 30

    # Begruendungs-Zitat-Karte
    quote_font = font(B.SANS_BOLD_ITALIC if hasattr(B, "SANS_BOLD_ITALIC") else B.SANS_BOLD, 22)
    quote_lines = wrap_text(draw, f"„{entry['quote']}“", quote_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 2 * pad)
    quote_h = 40 + len(quote_lines) * 30 + 20
    draw.rounded_rectangle([B.MARGIN_LEFT, y, W - B.MARGIN_RIGHT, y + quote_h], radius=16, fill="#181818", outline=accent, width=1)
    draw.rounded_rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + 6, y + quote_h], radius=3, fill=accent)
    label_font2 = font(B.SANS_BOLD, 16)
    draw.text((B.MARGIN_LEFT + pad, y + 16), "MEINE BEGRUENDUNG", font=label_font2, fill=accent)
    qy = y + 42
    for line in quote_lines:
        draw.text((B.MARGIN_LEFT + pad, qy), line, font=quote_font, fill=CREAM)
        qy += 30

    text = "Meine Watchlist -- keine Kaufempfehlung, nur meine eigene Beobachtung."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=CARD_BORDER, width=1)
    dis_lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    dy = H - 68
    for line in dis_lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 22

    chart_path.unlink(missing_ok=True)
    return img


WATCHLIST_WEEK = [
    {"weekday": "Dienstag", "date_label": "22.09.2026", "name": "Hermès", "ticker": "RMS", "kind": "stock",
     "price": 1346.50, "change_pct": 0.19, "as_of": "22.09.", "pe": 31.17, "forward_pe": None,
     "peg": None, "div_yield": 1.35, "market_cap": "140,4 Mrd. EUR", "volume": "18,6 Tsd.",
     "currency": "EUR",
     "csv_path": DATA_DIR / "RMS.csv", "accent": OCHRE,
     "quote": "Ich beobachte Hermès, weil die Aktie rund 41% unter ihrem 52-Wochen-Hoch liegt -- der gesamte Luxussektor kaempft gerade mit schwaecherer Nachfrage, vor allem aus China."},
]


def main():
    for entry in WATCHLIST_WEEK:
        img = slide_watchlist(entry, entry["weekday"])
        out_name = f"{entry['weekday'].lower()}_{entry['ticker'].lower()}"
        (TT_DIR / out_name).mkdir(exist_ok=True)
        img.save(TT_DIR / out_name / "slide_1.png")
        img.save(OUTPUT / f"uebersicht_{out_name}.png")
    print(f"Fertig: {len(WATCHLIST_WEEK)} Watchlist-Slides in {TT_DIR}")


if __name__ == "__main__":
    main()
