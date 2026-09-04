"""Neues Format: "ETF-Steckbrief" -- wie der Deep Dive (posts/personal_deep_dive*.py),
aber fuer einen Fonds/ETF statt eine Einzelaktie: Basisdaten, Top-Holdings,
Laender-/Sektor-Verteilung, echter Kursverlauf. Kein "Insider"-Slide (ETFs
haben keine Insider), stattdessen die Zusammensetzung im Fokus.

Rein faktisch -- TER/Fondsvolumen/Holdings/Verteilung sind oeffentliche
Fondsdaten, keine eigene Bewertung, keine Empfehlung (siehe CLAUDE.md-Regel).

Erstes Beispiel: iShares Core MSCI World UCITS ETF (Nutzerwunsch 2026-09-04,
"ETF-Steckbrief" als neues Format vorgeschlagen und gleich umgesetzt).

Aufruf:
  python posts/personal_etf_steckbrief.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "personal_etf_steckbrief_msciworld"
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

OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "ETF-STECKBRIEF"

NAME_FULL = "iShares Core MSCI World"
ISIN = "IE00B4L5Y983"
TICKER = "EUNL"
LOGO_PATH = ROOT / "assets" / "ishares_logo_icon.png"
PRICES_PATH = ROOT / "data" / "demo_EUNL_prices.json"

ACCENT = "#2E86D6"
CHART_LINE = ACCENT
CHART_FILL = "#141F2A"

TOP_HOLDINGS = [
    ("NVIDIA", "5,12%"), ("Apple", "4,85%"), ("Microsoft", "3,04%"),
    ("Amazon.com", "2,63%"), ("Alphabet", "2,36%"),
]
COUNTRIES = [("USA", 69.07), ("Japan", 5.67), ("Grossbritannien", 3.76), ("Kanada", 3.42), ("Sonstige", 18.08)]
SECTORS = [("Technologie", 29.52), ("Finanzen", 16.51), ("Industrie", 11.17),
           ("Gesundheit", 9.22), ("Konsum (zyklisch)", 8.83), ("Kommunikation", 7.95)]


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


def draw_logo_circle(img, draw, cx, cy, r, logo_path):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=ACCENT, width=2)
    logo = Image.open(logo_path).convert("RGBA")
    target = int(r * 1.4)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def draw_stat_box(draw, x, y, w, h, label, value):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD, outline=CARD_BORDER, width=1)
    label_font = font(B.SANS_BOLD, 15)
    value_font = font(B.SANS_BOLD, 22)
    lw = draw.textlength(label, font=label_font)
    vw = draw.textlength(value, font=value_font)
    while lw > w - 16 and label_font.size > 10:
        label_font = font(B.SANS_BOLD, label_font.size - 1)
        lw = draw.textlength(label, font=label_font)
    while vw > w - 16 and value_font.size > 12:
        value_font = font(B.SANS_BOLD, value_font.size - 1)
        vw = draw.textlength(value, font=value_font)
    draw.text((x + w / 2 - lw / 2, y + 12), label, font=label_font, fill=MUTED)
    draw.text((x + w / 2 - vw / 2, y + 34), value, font=value_font, fill=ACCENT)


def draw_bar_row(draw, x, y, w, label, pct, max_pct):
    label_font = font(B.SANS_BOLD, 20)
    pct_font = font(B.SANS_BOLD, 20)
    draw.text((x, y), label, font=label_font, fill=CREAM)
    pct_text = f"{pct:.1f}%".replace(".", ",")
    pw = draw.textlength(pct_text, font=pct_font)
    draw.text((x + w - pw, y), pct_text, font=pct_font, fill=ACCENT)
    bar_y = y + 30
    bar_h = 14
    draw.rounded_rectangle([x, bar_y, x + w, bar_y + bar_h], radius=7, fill=CARD)
    fill_w = max(6, w * (pct / max_pct))
    draw.rounded_rectangle([x, bar_y, x + fill_w, bar_y + bar_h], radius=7, fill=ACCENT)
    return bar_y + bar_h + 22


def draw_price_chart(draw, x, y, w, h, note):
    prices = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
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
    draw.text((chart_left, chart_top - 26), f"{hi:.2f} EUR", font=small_font, fill=MUTED)
    draw.text((chart_left, chart_bottom + 6), f"{lo:.2f} EUR", font=small_font, fill=MUTED)
    note_font = font(B.SANS_BOLD, 15)
    draw.text((x + pad, y + h - pad - 20), note, font=note_font, fill=MUTED)


def draw_footer(draw, idx, n_total):
    disclaimer_font = font(B.SANS_BOLD, 20)
    disclaimer_lines = wrap_text(draw, "Keine Anlageberatung -- nur Zahlen, die ich mir angeschaut habe.",
                                  disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 40 - 28 * len(disclaimer_lines) - 12
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 12
    for line in disclaimer_lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 28
    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 12), page_text, font=page_font, fill=MUTED)


def build_header(draw, subtitle=SERIES_TITLE):
    y = 40
    handle_font = font(B.SANS_BOLD, 19)
    title_font = font(B.SANS_BOLD, 21)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=ACCENT)
    y += 30
    draw.text((B.MARGIN_LEFT, y), subtitle, font=title_font, fill=CREAM)
    y += 32
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 22


def base_slide():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=ACCENT)
    return img, draw


def slide_1_intro():
    img, draw = base_slide()
    build_header(draw, subtitle="NEUE REIHE")

    logo_r = 90
    draw_logo_circle(img, draw, W // 2, 470, logo_r, LOGO_PATH)
    draw = ImageDraw.Draw(img)

    title_font = font(B.SANS_BOLD, 46)
    lines = wrap_text(draw, f"{NAME_FULL}.", title_font, W - 120)
    ty = 620
    for line in lines:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, ty), line, font=title_font, fill=CREAM)
        ty += 56

    sub_font = font(B.SANS_BOLD, 26)
    sub = "Ein ETF-Steckbrief."
    sw = draw.textlength(sub, font=sub_font)
    draw.text((W / 2 - sw / 2, ty + 14), sub, font=sub_font, fill=ACCENT)

    tag_font = font(B.SANS_BOLD, 20)
    tag = "BASISDATEN  ·  HOLDINGS  ·  VERTEILUNG"
    tgw = draw.textlength(tag, font=tag_font)
    draw.text((W / 2 - tgw / 2, ty + 70), tag, font=tag_font, fill=MUTED)

    disclaimer_font = font(B.SANS_BOLD, 20)
    dtext = "Keine Anlageberatung -- nur Zahlen, die ich mir angeschaut habe."
    dw = draw.textlength(dtext, font=disclaimer_font)
    draw.text((W / 2 - dw / 2, H - 70), dtext, font=disclaimer_font, fill=MUTED)
    return img


def slide_2_basisdaten():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "BASISDATEN", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 30

    logo_r = 40
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = y + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, LOGO_PATH)
    draw = ImageDraw.Draw(img)
    name_x = logo_cx + logo_r + 22
    draw.text((name_x, y + 8), NAME_FULL, font=font(B.SANS_BOLD, 26), fill=CREAM)
    draw.text((name_x, y + 44), f"{TICKER}  ·  {ISIN}", font=font(B.SANS_BOLD, 16), fill=MUTED)

    y = logo_cy + logo_r + 24
    body_font = font(B.SANS_BOLD, 23)
    lines = wrap_text(draw, "Bildet den MSCI-World-Index nach -- rund 1.323 Unternehmen aus "
                             "23 Industrielaendern, physisch replizierend (der ETF haelt die "
                             "Aktien tatsaechlich, kein Swap).",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33

    y += 20
    cols, gap = 3, 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 66
    stats = [
        ("TER", "0,20% p.a."), ("FONDSVOLUMEN", "127,6 Mrd. EUR"), ("AUFLAGEDATUM", "25.09.2009"),
        ("REPLIKATION", "physisch"), ("AUSSCHUETTUNG", "thesaurierend"), ("ANZAHL HOLDINGS", "1.323"),
        ("FONDSWAEHRUNG", "USD"), ("DOMIZIL", "Irland"), ("BOERSE (BSP.)", "Xetra"),
    ]
    for i, (label, value) in enumerate(stats):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)

    draw_footer(draw, 2, 7)
    return img


def slide_3_holdings():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "TOP-HOLDINGS", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 32)
    draw.text((B.MARGIN_LEFT, y), "Die fuenf groessten Positionen.", font=headline_font, fill=CREAM)
    y += 70

    max_pct = max(float(p.replace(",", ".").replace("%", "")) for _, p in TOP_HOLDINGS)
    for name, pct_text in TOP_HOLDINGS:
        pct = float(pct_text.replace(",", ".").replace("%", ""))
        y = draw_bar_row(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, name, pct, max_pct)

    y += 20
    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Die Top 5 machen zusammen rund 18% des gesamten Fonds aus -- "
                             "der Rest verteilt sich auf ueber 1.300 weitere Unternehmen.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 3, 7)
    return img


def slide_4_laender():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "LAENDER-VERTEILUNG", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 32)
    draw.text((B.MARGIN_LEFT, y), "Fast 70% USA.", font=headline_font, fill=CREAM)
    y += 70

    max_pct = max(p for _, p in COUNTRIES)
    for name, pct in COUNTRIES:
        y = draw_bar_row(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, name, pct, max_pct)

    y += 20
    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "'World' heisst hier vor allem 'USA' -- wer bewusst breiter "
                             "streuen will (z.B. mehr Schwellenlaender), braucht dafuer "
                             "einen zusaetzlichen ETF.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 4, 7)
    return img


def slide_5_sektoren():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "SEKTOR-VERTEILUNG", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 32)
    draw.text((B.MARGIN_LEFT, y), "Technologie klar vorne.", font=headline_font, fill=CREAM)
    y += 70

    max_pct = max(p for _, p in SECTORS)
    for name, pct in SECTORS:
        y = draw_bar_row(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, name, pct, max_pct)

    draw_footer(draw, 5, 7)
    return img


def slide_6_kursverlauf():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "KURSVERLAUF", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 30)
    draw.text((B.MARGIN_LEFT, y), "Deutlich ruhiger als eine Einzelaktie.", font=headline_font, fill=CREAM)
    y += 56

    chart_h = 400
    draw_price_chart(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, chart_h,
                      "Kursverlauf 1 Jahr (woechentlich) -- 52W-Hoch 129,85 EUR, 52W-Tief 104,16 EUR")
    y += chart_h + 28

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Die Schwankungsbreite ist deutlich kleiner als bei den "
                             "Einzelaktien in meinen Deep Dives -- genau das ist der Punkt "
                             "eines breit gestreuten ETFs: einzelne Ausreisser fallen weniger "
                             "ins Gewicht.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 6, 7)
    return img


def slide_7_fazit():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "FAZIT", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 40)
    draw.text((B.MARGIN_LEFT, y), "Was ich mitnehme.", font=headline_font, fill=CREAM)
    y += 66

    body_font = font(B.SANS_BOLD, 24)
    lines = wrap_text(draw, "Sehr breite Streuung (1.323 Positionen) bei niedrigen Kosten "
                             "(0,20% TER), aber mit klarer USA- und Tech-Uebergewichtung. Wer "
                             "das bewusst ausgleichen will, kombiniert das mit anderen ETFs "
                             "oder Regionen -- eine individuelle Entscheidung, keine "
                             "Pauschalantwort.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 34
    y += 30

    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=ACCENT, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Keine Kaufempfehlung, keine Bewertung meinerseits --",
               font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur Zahlen, die ich mir angeschaut habe.",
               font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 50
    draw.text((B.MARGIN_LEFT, y), "Folgen fuer mehr ETF-Steckbriefe.", font=font(B.SANS_BOLD, 24), fill=ACCENT)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_1_intro, slide_2_basisdaten, slide_3_holdings, slide_4_laender,
              slide_5_sektoren, slide_6_kursverlauf, slide_7_fazit]
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
