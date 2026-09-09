"""Neues Reel-Format, Nutzerwunsch (2026-09-09): "so nah wie moeglich" an den
visuellen Stil von @trade_rian ran (bold Hook-Headline, annotierter Chart mit
Trendlinie/HH-HL-Markern, dramatische Neugier-Framing wie "wette du kennst
nicht alle 3") -- OHNE dessen expliziter Kauf-Empfehlungssprache ("du
solltest jetzt kaufen", "meine finale Meinung", "diese Aktien kaufe ich
jetzt"). Das ist der bewusste Kompromiss, siehe [[feedback_depotdiary_compliance_regeln]]:
Format/Optik uebernehmen, Bewertung/Empfehlung nicht -- nur beobachtende
Sprache ("ist um X% gesprungen", "hat sich bewegt"), keine Aussage ob
gut/schlecht/kaufenswert.

Erste Ausgabe: "3 Aktien, die diese Woche stark in Bewegung waren" --
Oracle, Adobe, GameStop (alle 3 gerade nach Quartalszahlen in Bewegung,
echte Live-Kurse via Yahoo-Finance-Chart-API, kein synthetischer Wert).

Aufruf:
  python posts/format_wochenbewegung.py
"""
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "format_wochenbewegung"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BLACK = (10, 10, 10)
CREAM = "#F2F0EA"
MUTED = "#8A8A8A"
RED_ACCENT = "#E8384F"
GREEN = "#3DDC84"
RED = "#E8384F"

OWN_HANDLE = "@DASDEPOTDIARY"

# (Ticker, Anzeigename, Logo-Datei oder None, Kurzfakt zum Kontext -- rein
# faktisch/oeffentlich, keine Bewertung)
STOCKS = [
    {"ticker": "ORCL", "name": "Oracle", "logo": "orcl_logo_icon.png",
     "fact": "Quartalszahlen diese Woche veroeffentlicht -- Cloud-Umsatz im Fokus der Reaktion."},
    {"ticker": "ADBE", "name": "Adobe", "logo": "adbe_logo_icon.png",
     "fact": "Quartalszahlen diese Woche veroeffentlicht -- Markt reagiert auf den Wachstumsausblick."},
    {"ticker": "GME", "name": "GameStop", "logo": None,
     "fact": "Weiter im Umbau vom stationaeren Haendler zum breiteren Geschaeftsmodell."},
]


def fetch_change(symbol):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                      params={"range": "5d", "interval": "1d"},
                      headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r.raise_for_status()
    meta = r.json()["chart"]["result"][0]["meta"]
    price = meta["regularMarketPrice"]
    prev = meta.get("previousClose") or meta.get("chartPreviousClose")
    change = (price / prev - 1) * 100 if prev else 0.0
    return price, change


def fetch_history(symbol, rng="1mo"):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                      params={"range": rng, "interval": "1d"},
                      headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r.raise_for_status()
    closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    return [c for c in closes if c is not None]


def fmt_de(value, decimals=2):
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


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


def base_slide():
    img = Image.new("RGB", (W, H), BLACK)
    # sehr dezente rote Vignette oben -- Anlehnung an trade_rians dunklen,
    # kontrastreichen Look, aber eigenstaendig statt kopiert
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([W / 2 - 500, -300, W / 2 + 500, 500], fill=55)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    red_layer = Image.new("RGB", (W, H), (60, 10, 16))
    img.paste(red_layer, (0, 0), glow)
    return img, ImageDraw.Draw(img)


def build_header(draw, y=60):
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, y), OWN_HANDLE, font=handle_font, fill=MUTED)
    return y + 50


def footer_disclaimer(draw):
    note_font = font(B.SANS_BOLD, 22)
    note = "Reine Marktbeobachtung -- keine Anlageberatung, keine Kauf-/Verkaufsempfehlung."
    lines = wrap_text(draw, note, note_font, W - 140)
    ny = H - 40 - len(lines) * 28
    for line in lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, ny), line, font=note_font, fill=MUTED)
        ny += 28


def slide_hook():
    img, draw = base_slide()
    build_header(draw)

    y = H * 0.28
    label_font = font(B.SANS_BOLD, 28)
    label = "DIESE WOCHE"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=RED_ACCENT)
    y += 60

    title_font = font(B.SANS_BOLD, 66)
    for line in ["3 AKTIEN, DIE SICH", "STARK BEWEGT HABEN"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 76

    y += 40
    sub_font = font(B.SANS_BOLD, 32)
    sub_lines = wrap_text(draw, "Wette, du kennst nicht alle 3 -- und wie stark.", sub_font, W - 160)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 42

    footer_disclaimer(draw)
    return img


def mini_chart(draw, closes, x0, y0, x1, y1, color):
    n = len(closes)
    if n < 2:
        return
    lo, hi = min(closes), max(closes)
    span = (hi - lo) or 1
    pts = []
    for i, c in enumerate(closes):
        x = x0 + (x1 - x0) * i / (n - 1)
        y = y1 - (y1 - y0) * (c - lo) / span
        pts.append((x, y))
    draw.line(pts, fill=color, width=5, joint="curve")

    # HH/HL-Marker an lokalen Extrempunkten -- Anlehnung an trade_rians
    # Trendlinien-Chart-Optik, hier rein deskriptiv (kein Kaufsignal)
    marker_font = font(B.SANS_BOLD, 20)
    for i in range(1, n - 1):
        is_peak = closes[i] > closes[i - 1] and closes[i] > closes[i + 1]
        is_trough = closes[i] < closes[i - 1] and closes[i] < closes[i + 1]
        if is_peak or is_trough:
            px, py = pts[i]
            r = 5
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)


def slide_stock(idx, stock):
    img, draw = base_slide()
    y = build_header(draw)
    y += 60  # mehr Luft oben -- Inhalt insgesamt vertikal ausgewogener ueber die volle 9:16-Flaeche

    badge_font = font(B.SANS_BOLD, 26)
    badge = f"AKTIE {idx + 1} / 3"
    tw = draw.textlength(badge, font=badge_font)
    draw.text((W / 2 - tw / 2, y), badge, font=badge_font, fill=RED_ACCENT)
    y += 70

    if stock["logo"]:
        logo = Image.open(ROOT / "assets" / stock["logo"]).convert("RGBA")
        target_w = 280
        ratio = target_w / logo.width
        logo = logo.resize((target_w, max(1, int(logo.height * ratio))))
        lx = W / 2 - logo.width / 2
        img.paste(logo, (int(lx), int(y)), logo)
        y += logo.height + 30
        draw = ImageDraw.Draw(img)
    else:
        ticker_font = font(B.SANS_BOLD, 68)
        tw = draw.textlength(stock["ticker"], font=ticker_font)
        draw.text((W / 2 - tw / 2, y), stock["ticker"], font=ticker_font, fill=CREAM)
        y += 90

    name_font = font(B.SANS_BOLD, 34)
    tw = draw.textlength(stock["name"], font=name_font)
    draw.text((W / 2 - tw / 2, y), stock["name"], font=name_font, fill=MUTED)
    y += 70

    price, change = stock["price"], stock["change"]
    color = GREEN if change >= 0 else RED
    change_font = font(B.SANS_BOLD, 96)
    change_str = f"{'+' if change >= 0 else ''}{fmt_de(change)}%"
    tw = draw.textlength(change_str, font=change_font)
    draw.text((W / 2 - tw / 2, y), change_str, font=change_font, fill=color)
    y += 118

    price_font = font(B.SANS_BOLD, 30)
    price_str = f"{fmt_de(price)} USD"
    tw = draw.textlength(price_str, font=price_font)
    draw.text((W / 2 - tw / 2, y), price_str, font=price_font, fill=MUTED)
    y += 80

    range_font = font(B.SANS_BOLD, 24)
    range_label = "LETZTE 4 WOCHEN"
    tw = draw.textlength(range_label, font=range_font)
    draw.text((W / 2 - tw / 2, y), range_label, font=range_font, fill=MUTED)
    y += 50

    chart_top = y
    chart_bottom = y + 620
    mini_chart(draw, stock["history"], 120, chart_bottom, W - 120, chart_top, color)
    y = chart_bottom + 40

    lo, hi = min(stock["history"]), max(stock["history"])
    span_font = font(B.SANS_BOLD, 26)
    span_str = f"Spanne: {fmt_de(lo)} -- {fmt_de(hi)} USD"
    tw = draw.textlength(span_str, font=span_font)
    draw.text((W / 2 - tw / 2, y), span_str, font=span_font, fill=MUTED)
    y += 70

    fact_font = font(B.SANS_BOLD, 32)
    fact_lines = wrap_text(draw, stock["fact"], fact_font, W - 180)
    for line in fact_lines:
        tw = draw.textlength(line, font=fact_font)
        draw.text((W / 2 - tw / 2, y), line, font=fact_font, fill=CREAM)
        y += 42

    footer_disclaimer(draw)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)
    y += 100

    title_font = font(B.SANS_BOLD, 54)
    for line in ["WELCHE BEWEGUNG", "UEBERRASCHT DICH?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 66

    y += 40
    sub_font = font(B.SANS_BOLD, 32)
    sub = "Schreib's in die Kommentare."
    tw = draw.textlength(sub, font=sub_font)
    draw.text((W / 2 - tw / 2, y), sub, font=sub_font, fill=RED_ACCENT)

    footer_disclaimer(draw)
    return img


def main():
    for s in STOCKS:
        price, change = fetch_change(s["ticker"])
        s["price"], s["change"] = price, change
        s["history"] = fetch_history(s["ticker"])

    slides = [slide_hook]
    for i, s in enumerate(STOCKS):
        slides.append(lambda i=i, s=s: slide_stock(i, s))
    slides.append(slide_outro)

    for i, fn in enumerate(slides, start=1):
        img = fn()
        img.save(TT_DIR / f"slide_{i}.png")
        feed_w, feed_h = B.FEED_SIZE
        crop_h = int(feed_w * H / W)
        top = max(0, (H - crop_h) // 3)
        cropped = img.crop((0, top, W, min(H, top + crop_h))).resize((feed_w, feed_h))
        cropped.save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = 3
    rows = (n + cols - 1) // cols
    gap = 16
    tw, th = W // 3, H // 3
    sheet = Image.new("RGB", (tw * cols + gap * (cols + 1), th * rows + gap * (rows + 1)), (16, 14, 14))
    for i in range(1, n + 1):
        im = Image.open(TT_DIR / f"slide_{i}.png").resize((tw, th))
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = [
        "Drei Aktien, die sich diese Woche stark bewegt haben. Wette, du kennst nicht alle drei -- und wie stark.",
        f"Aktie eins: {STOCKS[0]['name']}, {'plus' if STOCKS[0]['change']>=0 else 'minus'} {abs(round(STOCKS[0]['change'],1))} Prozent. {STOCKS[0]['fact']}",
        f"Aktie zwei: {STOCKS[1]['name']}, {'plus' if STOCKS[1]['change']>=0 else 'minus'} {abs(round(STOCKS[1]['change'],1))} Prozent. {STOCKS[1]['fact']}",
        f"Aktie drei: {STOCKS[2]['name']}, {'plus' if STOCKS[2]['change']>=0 else 'minus'} {abs(round(STOCKS[2]['change'],1))} Prozent. {STOCKS[2]['fact']}",
        "Welche Bewegung ueberrascht dich am meisten? Schreib's in die Kommentare -- und folge fuer mehr.",
    ]
    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md + timing.json")


if __name__ == "__main__":
    main()
