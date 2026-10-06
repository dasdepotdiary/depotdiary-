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
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S
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
    """v3 (2026-10-06): depotdiary-Foto-Schema (Skyline-Foto, Glas-Karten fuer Chart,
    Kennzahlen und Begruendung, vivide Akzentfarbe). Schnittstelle unveraendert."""
    key = f"watchlist-{entry['date_label']}-{entry['ticker']}"
    accent = S.accent_for(key)
    img = S.story_background(S.photo_for(key), scrim_from=0.62, scrim_len=0.20)

    chart_path = OUTPUT / f"_chart_{entry['ticker']}.png"
    render_chart(entry["csv_path"], accent, chart_path)
    chart_img = Image.open(chart_path).convert("RGBA")
    chart_w = 840
    chart_h = int(chart_img.height * chart_w / chart_img.width)
    chart_card = (50, 530, S.SW - 50, 530 + chart_h + 40)

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
            ("7-Tage-Veraenderung", f"{entry['change_7d']:+.2f} %".replace(".", ",")),
            ("Tief (dargestellt)", f"{fmt_de(entry['range_low'])} USD"),
            ("Hoch (dargestellt)", f"{fmt_de(entry['range_high'])} USD"),
        ]
    rows = (len(stats) + 1) // 2
    row_h = 64
    kpi_top = chart_card[3] + 20
    kpi_card = (50, kpi_top, S.SW - 50, kpi_top + rows * row_h + 40)

    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    qf = S.font(24)
    qlines = S.wrap_text(tmp, entry["quote"], qf, S.SW - 200)[:5]
    q_top = kpi_card[3] + 20
    quote_card = (50, q_top, S.SW - 50, q_top + 52 + len(qlines) * 32 + 16)

    img = S.glass(img, [chart_card, kpi_card, quote_card], radius=24, alpha=182)
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, f"MEINE WATCHLIST   {weekday_label.upper()}", entry["date_label"][:6])

    draw.text((82, 386), entry["name"].upper(), font=S.font(60), fill=(0, 0, 0))
    draw.text((80, 383), entry["name"].upper(), font=S.font(60), fill=S.CREAM)
    draw.text((82, 464), entry["ticker"], font=S.font(28), fill=(0, 0, 0))
    draw.text((80, 462), entry["ticker"], font=S.font(28), fill=accent)
    price_text = f"{fmt_de(entry['price'])} {entry.get('currency', 'USD')}"
    pf = S.font(44)
    pw = draw.textlength(price_text, font=pf)
    draw.text((S.SW - 80 - pw, 392), price_text, font=pf, fill=S.CREAM)
    change = entry["change_pct"]
    ctext = f"{change:+.2f}%".replace(".", ",") + f"  (Stand {entry['as_of']})"
    cf = S.font(24)
    cw = draw.textlength(ctext, font=cf)
    col = "#4ADE80" if change >= 0 else "#FF6B6B"
    draw.text((S.SW - 80 - cw + 2, 454), ctext, font=cf, fill=(0, 0, 0))
    draw.text((S.SW - 80 - cw, 452), ctext, font=cf, fill=col)

    img.paste(chart_img.resize((chart_w, chart_h)), (120, chart_card[1] + 20), chart_img.resize((chart_w, chart_h)))
    draw = ImageDraw.Draw(img)

    pad = 40
    col_w = (kpi_card[2] - kpi_card[0] - 2 * pad) / 2
    for i, (label, value) in enumerate(stats):
        c, r = i % 2, i // 2
        cx = kpi_card[0] + pad + c * col_w
        cy = kpi_top + 22 + r * row_h
        draw.text((cx, cy), label.upper(), font=S.font(17), fill=S.SOFT)
        draw.text((cx, cy + 24), value, font=S.font(26), fill=S.CREAM)

    draw.text((quote_card[0] + pad, q_top + 16), "MEINE BEGRUENDUNG", font=S.font(17), fill=accent)
    qy = q_top + 46
    for line in qlines:
        draw.text((quote_card[0] + pad, qy), line, font=qf, fill=S.CREAM)
        qy += 32

    draw.text((80, S.SAFE_BOTTOM - 62), "Meine Watchlist -- keine Kaufempfehlung, nur meine eigene Beobachtung.",
              font=S.font(20), fill=S.SOFT)
    S.draw_wordmark(img)
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
