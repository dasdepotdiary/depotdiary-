"""Ad-hoc Story-Format "DAMALS INVESTIERT" -- kein fixer Rhythmus, sondern
wenn ein interessanter Fall auffaellt (Nutzerwunsch 2026-09-17: "einmal in
der Woche, zweimal in der Woche, einfach wenn du dran denkst"): "Haettest
du vor X Jahren in Y investiert, haettest du heute so viel."

v2 (2026-09-18, Nutzer: "gefaellt mir nicht, nimm die Skyline-Optik, macht
den Graphen kleiner, drei Werte untereinander pro Seite"): Skyline-Hintergrund
(gedimmt, wie im Vermoegensingenieur-Collab) statt flachem Petrol/Gold-Verlauf,
3 kompakte Karten (Chart+Zahlen) auf EINER Slide statt eine volle Slide je Wert.

WICHTIG: nutzt IMMER split-adjustierte Kurse (TIME_SERIES_*_ADJUSTED /
'adjusted close' bzw. bei Krypto Yahoo-Finance-Chart-API) -- sonst verzerren
Aktiensplits (z.B. Nvidia 10:1 2024, Monster Energy 2:1 2023 + 2:1 2026) das
Ergebnis massiv. Vor dem Bauen IMMER die SPLITS-Daten fuer den Ticker pruefen.
Ehrlich bleiben: nicht nur Gewinner zeigen (Ethereum lag in diesem Beispiel
sogar leicht im Minus) -- das ist glaubwuerdiger als reine Erfolgsgeschichten.

Input: Liste von Dicts mit ticker, name, years_ago, start_date, start_price,
end_price, invested, note, csv_path (Spalten timestamp,close -- adjustierte
Kurse), accent.

Aufruf (Prototyp/Test):
  python posts/story_damals_investiert.py
"""
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font

ROOT = Path(__file__).parent.parent
NAME = "story_damals_investiert"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
DATA_DIR = OUTPUT / "data"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
INK = "#F5F2EA"
SUBTEXT = "#C9C4B6"
GOLD = "#E0B15C"
TEAL = "#4FBFB5"
RED = "#C25C51"
SKYBLUE = "#7EC8E3"
CARD = (10, 10, 10, 168)
CARD_BORDER = "#4A4638"
DIVIDER = "#4A4638"

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def fmt_de(value, decimals=0):
    sign = "-" if value < 0 else ""
    return sign + f"{abs(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


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


def skyline_background(brightness=0.34):
    img = Image.open(ROOT / "assets" / "skyline_still_1.png").convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    # Vignette oben/unten fuer Lesbarkeit
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, W, 260], fill=140)
    vdraw.rectangle([0, H - 260, W, H], fill=160)
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(black, img, vignette)
    return img


def render_chart(csv_path, accent_hex, out_path):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        next(f)
        for line in f:
            ts, close = line.strip().split(",")
            rows.append((ts, float(close)))
    rows.sort(key=lambda r: r[0])
    closes = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(9.6, 2.6), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    x = list(range(len(closes)))
    ax.plot(x, closes, color=accent_hex, linewidth=3, solid_capstyle="round")
    ax.fill_between(x, closes, min(closes) * 0.92, color=accent_hex, alpha=0.16)
    ax.set_xlim(0, len(closes) - 1)
    ax.set_ylim(min(closes) * 0.92, max(closes) * 1.06)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout(pad=0.1)
    fig.savefig(out_path, transparent=True)
    plt.close(fig)


def center_text(draw, text, fnt, y, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((W / 2 - tw / 2, y), text, font=fnt, fill=fill)
    return tw


def draw_card(img, draw, x, y, w, entry):
    factor = entry["end_price"] / entry["start_price"]
    end_value = entry["invested"] * factor
    gain_pct = (factor - 1) * 100
    accent = entry.get("accent", GOLD)
    pos = factor >= 1

    pad = 24
    header_h = 34
    chart_h = 138
    stats_h = 70
    card_h = header_h + chart_h + stats_h + pad * 2

    overlay = Image.new("RGBA", (w, card_h), CARD)
    img.paste(overlay, (x, y), overlay)
    draw.rounded_rectangle([x, y, x + w, y + card_h], radius=16, outline=CARD_BORDER, width=1)

    name_font = font(B.SANS_BOLD, 24)
    ticker_font = font(B.SANS_BOLD, 17)
    draw.text((x + pad, y + pad), entry["name"], font=name_font, fill=INK)
    nw = draw.textlength(entry["name"], font=name_font)
    draw.text((x + pad + nw + 12, y + pad + 5), entry["ticker"], font=ticker_font, fill=accent)

    factor_font = font(B.SANS_BOLD, 24)
    factor_text = f"{'+' if pos else ''}{fmt_de(gain_pct, 0)}%"
    fw = draw.textlength(factor_text, font=factor_font)
    draw.text((x + w - pad - fw, y + pad), factor_text, font=factor_font, fill=(TEAL if pos else RED))

    chart_y = y + pad + header_h
    chart_path = OUTPUT / f"_chart_{entry['ticker']}.png"
    render_chart(entry["csv_path"], accent, chart_path)
    chart_img = Image.open(chart_path).convert("RGBA")
    chart_w = w - 2 * pad
    ch = int(chart_img.height * chart_w / chart_img.width)
    chart_img = chart_img.resize((chart_w, min(ch, chart_h)))
    img.paste(chart_img, (x + pad, chart_y), chart_img)
    draw = ImageDraw.Draw(img)

    stats_y = chart_y + chart_h + 10
    label_font = font(B.SANS_BOLD, 15)
    val_font = font(B.SANS_BOLD, 26)
    draw.text((x + pad, stats_y), f"{fmt_de(entry['invested'])} € ({entry['start_date']})", font=label_font, fill=SUBTEXT)
    end_text = f"{fmt_de(end_value)} € heute"
    draw.text((x + pad, stats_y + 22), end_text, font=val_font, fill=INK)
    mult_text = f"das {fmt_de(factor, 1)}-fache"
    mw = draw.textlength(mult_text, font=label_font)
    draw.text((x + w - pad - mw, stats_y + 30), mult_text, font=label_font, fill=accent)

    return card_h


def slide_damals(entries, years_ago, brightness=0.34):
    img = skyline_background(brightness)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=SKYBLUE)

    y = 44
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + DATE_LABEL, font=eyebrow_font, fill=SUBTEXT)

    invested_amount = entries[0]["invested"] if entries else 1000
    invested_font = font(B.SANS_BOLD, 26)
    invested_text = f"bei {fmt_de(invested_amount)} € investiert"
    iw = draw.textlength(invested_text, font=invested_font)
    draw.text((W - B.MARGIN_RIGHT - iw, y - 4), invested_text, font=invested_font, fill=INK)

    y += 34
    title_font = font(B.SANS_BOLD, 34)
    draw.text((B.MARGIN_LEFT, y), "DAMALS INVESTIERT", font=title_font, fill=INK)
    y += 42
    sub_font = font(B.SANS_BOLD, 19)
    hook = f"Hättest du vor {years_ago} Jahren investiert..."
    draw.text((B.MARGIN_LEFT, y), hook, font=sub_font, fill=SKYBLUE)
    y += 38

    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    for entry in entries:
        card_h = draw_card(img, draw, B.MARGIN_LEFT, y, content_w, entry)
        y += card_h + 14

    text = "Keine Anlageempfehlung -- reine Vergangenheitsbetrachtung, keine Garantie fuer die Zukunft."
    disclaimer_font = font(B.SANS_BOLD, 16)
    draw.line([(B.MARGIN_LEFT, H - 80), (W - B.MARGIN_RIGHT, H - 80)], fill=DIVIDER, width=1)
    dy = H - 62
    for line in wrap_text(draw, text, disclaimer_font, content_w):
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=SUBTEXT)
        dy += 20

    for entry in entries:
        (OUTPUT / f"_chart_{entry['ticker']}.png").unlink(missing_ok=True)
    return img


def main():
    entries = [
        {"name": "Netflix", "ticker": "NFLX", "start_date": "09/2023", "start_price": 37.76, "end_price": 71.79,
         "invested": 1000, "csv_path": DATA_DIR / "NFLX_3y.csv", "accent": RED},
        {"name": "Eli Lilly", "ticker": "LLY", "start_date": "09/2023", "start_price": 526.2055, "end_price": 1152.93,
         "invested": 1000, "csv_path": DATA_DIR / "LLY_3y.csv", "accent": TEAL},
        {"name": "Uber", "ticker": "UBER", "start_date": "09/2023", "start_price": 45.99, "end_price": 70.50,
         "invested": 1000, "csv_path": DATA_DIR / "UBER_3y.csv", "accent": SKYBLUE},
        {"name": "Robinhood", "ticker": "HOOD", "start_date": "09/2023", "start_price": 9.81, "end_price": 119.82,
         "invested": 1000, "csv_path": DATA_DIR / "HOOD_3y.csv", "accent": GOLD},
        {"name": "Solana", "ticker": "SOL", "start_date": "09/2023", "start_price": 21.4624, "end_price": 113.23,
         "invested": 1000, "csv_path": DATA_DIR / "SOL_3y.csv", "accent": "#C77D3B"},
    ]
    img = slide_damals(entries, years_ago=3, brightness=0.85)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
