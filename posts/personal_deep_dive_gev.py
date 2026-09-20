"""Deep Dive zu GE Vernova (GEV) -- Sieger der Deep-Dive-Abstimmung vom
19.-20.09.2026 (Aktien-Check/Watchlist dieser Woche: SAP, Alphabet, Costco,
GE Vernova -- Follower haben per DM/Kommentar abgestimmt).

7-Folien-Format wie personal_deep_dive.py/personal_deep_dive_vst.py.
Rein faktisch -- keine Kursziele, keine Kauf-/Verkaufsempfehlung. Kein
Logo-Asset vorhanden -> grosser Ticker-Schriftzug statt Logo-Kreis.
Keine oeffentlichen Insider-Transaktionen in der Datenbank gefunden --
das wird auf der Insider-Folie auch so ehrlich benannt statt erfunden.

Aufruf:
  python posts/personal_deep_dive_gev.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "personal_deep_dive_gev"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

BG = "#0D1512"
CARD = "#17211D"
CARD_BORDER = "#2E3B36"
CREAM = "#F2F0EA"
MUTED = "#93A39B"
GREEN_MID = B.GREEN_MID

OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "DEEP DIVE"

TICKER = "GEV"
NAME_FULL = "GE Vernova"
PRICES_PATH = ROOT / "data" / "demo_GEV_prices.json"

ACCENT = "#22B893"
CHART_LINE = ACCENT
CHART_FILL = "#123028"


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


def draw_ticker_badge(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CARD, outline=ACCENT, width=3)
    tf = font(B.SANS_BOLD, int(r * 0.7))
    tw = draw.textlength(TICKER, font=tf)
    draw.text((cx - tw / 2, cy - r * 0.42), TICKER, font=tf, fill=ACCENT)


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
    draw.text((x + w / 2 - vw / 2, y + 34), value, font=value_font, fill=ACCENT)


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
    draw.text((chart_left, chart_top - 26), f"{hi:.2f} USD", font=small_font, fill=MUTED)
    draw.text((chart_left, chart_bottom + 6), f"{lo:.2f} USD", font=small_font, fill=MUTED)
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
    build_header(draw, subtitle="EURE ABSTIMMUNG")

    draw_ticker_badge(draw, W // 2, 470, 90)

    title_font = font(B.SANS_BOLD, 52)
    title = f"{NAME_FULL}."
    tw = draw.textlength(title, font=title_font)
    draw.text((W / 2 - tw / 2, 620), title, font=title_font, fill=CREAM)

    sub_font = font(B.SANS_BOLD, 24)
    sub = f"Euer Sieger dieser Woche -- ein genauerer Blick auf {TICKER}."
    lines = wrap_text(draw, sub, sub_font, W - 160)
    sy = 700
    for line in lines:
        sw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - sw / 2, sy), line, font=sub_font, fill=ACCENT)
        sy += 32

    tag_font = font(B.SANS_BOLD, 20)
    tag = "BEWERTUNG  ·  KURSANALYSE  ·  INSIDER-AKTIVITAET"
    tgw = draw.textlength(tag, font=tag_font)
    draw.text((W / 2 - tgw / 2, sy + 30), tag, font=tag_font, fill=MUTED)

    disclaimer_font = font(B.SANS_BOLD, 20)
    dtext = "Keine Anlageberatung -- nur Zahlen, die ich mir angeschaut habe."
    dw = draw.textlength(dtext, font=disclaimer_font)
    draw.text((W / 2 - dw / 2, H - 70), dtext, font=disclaimer_font, fill=MUTED)
    return img


def slide_2_overview():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "UNTERNEHMEN", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 30

    draw_ticker_badge(draw, B.MARGIN_LEFT + 44, y + 44, 44)
    name_x = B.MARGIN_LEFT + 44 + 44 + 22
    draw.text((name_x, y + 4), NAME_FULL, font=font(B.SANS_BOLD, 34), fill=CREAM)
    draw.text((name_x, y + 48), f"{TICKER}  ·  NYSE", font=font(B.SANS_BOLD, 18), fill=MUTED)

    y += 44 + 44 + 24
    body_font = font(B.SANS_BOLD, 23)
    lines = wrap_text(draw, "GE Vernova erzeugt und ueberträgt elektrische Energie -- 2024 "
                             "als eigenstaendiges Unternehmen von General Electric abgespalten. "
                             "Drei Segmente: Power (Gas-/Dampfturbinen, Kernkraft), Wind "
                             "(Onshore/Offshore) und Electrification (Netztechnik, Software).",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33
    y += 10

    lines2 = wrap_text(draw, "Aktuell im Fokus: steigender Strombedarf durch KI-Rechenzentren "
                              "-- Gasturbinen und Netztechnik gehoeren zu den Bereichen mit "
                              "der staerksten Nachfrage.", body_font,
                        W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33

    y += 20
    cols, gap = 3, 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 66
    stats = [
        ("KURS", "940,33 USD"), ("MARKTKAP.", "250,4 Mrd. USD"), ("52W-HOCH", "1.195,94 USD"),
        ("52W-TIEF", "529,18 USD"), ("BOERSENGANG", "2024 (Spin-off)"), ("HAUPTSITZ", "Cambridge, USA"),
        ("SEGMENTE", "3 (Power/Wind/Elec.)"), ("DIVIDENDE/JAHR", "1,75 USD"), ("BETA", "0,97"),
    ]
    for i, (label, value) in enumerate(stats):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)

    draw_footer(draw, 2, 7)
    return img


def slide_3_bewertung():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "BEWERTUNG", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 30)
    for line in wrap_text(draw, "Starkes Gewinnwachstum, erwartetes KGV hoeher als aktuelles.",
                           headline_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT):
        draw.text((B.MARGIN_LEFT, y), line, font=headline_font, fill=CREAM)
        y += 38
    y += 20

    cols, gap = 2, 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 78
    stats = [
        ("KGV (AKTUELL)", "26,5x"), ("KGV (ERWARTET)", "37,6x"),
        ("PEG-RATIO", "1,80"), ("GEWINNWACHSTUM Q2", "+32,8% YoY"),
        ("UMSATZWACHSTUM Q2", "+21,9% YoY"), ("NETTOMARGE", "23,0%"),
    ]
    for i, (label, value) in enumerate(stats):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)
    y += 3 * (box_h + gap) + 16

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Das erwartete KGV (37,6x) liegt hoeher als das aktuelle (26,5x) -- "
                             "der Markt rechnet also mit einem niedrigeren Gewinn im kommenden "
                             "Jahr als im laufenden. Gleichzeitig wuchs der Gewinn im letzten "
                             "Quartal um 32,8% gegenueber dem Vorjahr, der Umsatz um 21,9%.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 3, 7)
    return img


def draw_heart_icon(draw, cx, cy, size, color):
    r = size * 0.28
    draw.ellipse([cx - size * 0.5, cy - size * 0.28, cx - size * 0.5 + 2 * r, cy - size * 0.28 + 2 * r], fill=color)
    draw.ellipse([cx, cy - size * 0.28, cx + 2 * r, cy - size * 0.28 + 2 * r], fill=color)
    draw.polygon([(cx - size * 0.5, cy), (cx + size * 0.5, cy), (cx, cy + size * 0.55)], fill=color)


def draw_comment_icon(draw, cx, cy, size, color):
    draw.rounded_rectangle([cx - size * 0.55, cy - size * 0.4, cx + size * 0.55, cy + size * 0.35],
                            radius=size * 0.18, outline=color, width=max(3, int(size * 0.09)))
    draw.polygon([(cx - size * 0.15, cy + size * 0.3), (cx + size * 0.1, cy + size * 0.3),
                  (cx - size * 0.2, cy + size * 0.62)], fill=color)


def draw_share_icon(draw, cx, cy, size, color):
    w = max(3, int(size * 0.1))
    draw.line([(cx - size * 0.5, cy + size * 0.35), (cx - size * 0.5, cy - size * 0.15),
               (cx + size * 0.5, cy - size * 0.15)], fill=color, width=w, joint="curve")
    draw.polygon([(cx + size * 0.5, cy - size * 0.42), (cx + size * 0.5, cy + size * 0.12),
                  (cx + size * 0.82, cy - size * 0.15)], fill=color)


def slide_4_cta():
    img, draw = base_slide()
    build_header(draw, subtitle="KURZE PAUSE")

    y = 380
    f1 = font(B.SANS_BOLD, 46)
    draw.text((B.MARGIN_LEFT, y), "Bevor's weitergeht:", font=f1, fill=CREAM)
    y += 76

    f2 = font(B.SANS_BOLD, 34)
    for line in ["Danke fuers Mitstimmen!", "Wenn dir das Format gefaellt:", "liken, kommentieren, teilen --",
                 "und folgen fuer die naechste", "Abstimmung."]:
        draw.text((B.MARGIN_LEFT, y), line, font=f2, fill=ACCENT)
        y += 46

    y += 40
    icon_size = 84
    gap = 130
    total_w = 3 * icon_size + 2 * (gap - icon_size)
    start_x = W / 2 - total_w / 2 + icon_size / 2
    icon_y = y + icon_size / 2
    draw_heart_icon(draw, start_x, icon_y, icon_size, ACCENT)
    draw_comment_icon(draw, start_x + gap, icon_y, icon_size, ACCENT)
    draw_share_icon(draw, start_x + 2 * gap, icon_y, icon_size, ACCENT)
    y += icon_size + 30
    label_font = font(B.SANS_BOLD, 18)
    labels = ["LIKE", "KOMMENTAR", "TEILEN"]
    for i, label in enumerate(labels):
        lw = draw.textlength(label, font=label_font)
        draw.text((start_x + i * gap - lw / 2, y), label, font=label_font, fill=MUTED)

    draw_footer(draw, 4, 7)
    return img


def slide_5_kursanalyse():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "KURSANALYSE", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 30)
    for line in wrap_text(draw, "Mehr als verdoppelt im Jahresverlauf, zuletzt korrigiert.",
                           headline_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT):
        draw.text((B.MARGIN_LEFT, y), line, font=headline_font, fill=CREAM)
        y += 40
    y += 20

    chart_h = 400
    draw_price_chart(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, chart_h,
                      "Kursverlauf 1 Jahr (woechentlich) -- 52W-Hoch 1.195,94 USD, 52W-Tief 529,18 USD")
    y += chart_h + 28

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Aktuell rund 21% unter dem 52-Wochen-Hoch, aber rund 78% ueber "
                             "dem 52-Wochen-Tief. Der Kurs zog vor allem zwischen Jahresbeginn "
                             "und April deutlich an -- getragen vom Thema steigender "
                             "Strombedarf durch KI-Rechenzentren -- und korrigierte seither "
                             "wieder etwas.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 5, 7)
    return img


def slide_6_insider():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "INSIDER-AKTIVITAET", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    headline_font = font(B.SANS_BOLD, 30)
    for line in wrap_text(draw, "Keine aktuellen Meldungen in meiner Datenquelle gefunden.",
                           headline_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT):
        draw.text((B.MARGIN_LEFT, y), line, font=headline_font, fill=CREAM)
        y += 38
    y += 20

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Ueber die oeffentliche SEC-Form-4-Datenbank, die ich fuer diese "
                             "Reihe nutze, waren fuer GE Vernova aktuell keine Insider-"
                             "Transaktionen abrufbar -- das kann heissen, dass zuletzt keine "
                             "gemeldet wurden, oder dass die Daten hier gerade nicht vorliegen. "
                             "Ich zeig hier lieber ehrlich eine Luecke, statt mir etwas "
                             "auszudenken.",
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
    lines = wrap_text(draw, "GE Vernova waechst zweistellig (Umsatz +21,9%, Gewinn +32,8% im "
                             "letzten Quartal) und profitiert vom steigenden Strombedarf durch "
                             "KI-Rechenzentren. Das erwartete KGV liegt aber ueber dem "
                             "aktuellen -- der Markt rechnet mit etwas weniger Gewinn im "
                             "kommenden Jahr. Der Kurs hat sich seit dem Spin-off 2024 vervielfacht, "
                             "ist zuletzt aber rund 21% von seinem 52-Wochen-Hoch entfernt.",
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
    draw.text((B.MARGIN_LEFT, y), "nur die Zahlen, die ich mir angeschaut habe.",
               font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 50
    draw.text((B.MARGIN_LEFT, y), "Danke fuers Abstimmen -- folgen fuer mehr Deep Dives.",
               font=font(B.SANS_BOLD, 24), fill=ACCENT)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_1_intro, slide_2_overview, slide_3_bewertung, slide_4_cta,
              slide_5_kursanalyse, slide_6_insider, slide_7_fazit]
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
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (10, 14, 12))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
