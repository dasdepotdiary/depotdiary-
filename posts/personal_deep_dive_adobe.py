"""Deep Dive #7: Adobe Inc. (ADBE), auf Nutzerwunsch vom 2026-09-06
(urspruenglicher Kandidat, dann erst als Schnell-Check mit Oracle kombiniert
-- jetzt zusaetzlich der volle Deep Dive). Gleiche Struktur wie
posts/personal_deep_dive_vst.py -- Akzentfarbe Adobe Red (#FA0C00).

Statt eines klassischen Insider-Form-4 hier die naeher liegende, echte
Story der Woche: der ueberraschende CEO-Wechsel plus zusaetzlicher Abgang
des Creative-Cloud-Chefs, beides oeffentlich und rein faktisch berichtet.

Aufruf:
  python posts/personal_deep_dive_adobe.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "personal_deep_dive_adobe"
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
SERIES_TITLE = "DEEP DIVE"

TICKER = "ADBE"
NAME_FULL = "Adobe"
WKN = "871981"
LOGO_PATH = ROOT / "assets" / "adbe_logo_icon.png"
PRICES_PATH = ROOT / "data" / "demo_ADBE_prices.json"

ACCENT = "#FA0C00"
CHART_LINE = ACCENT
CHART_FILL = "#330705"


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
    target = int(r * 1.6)
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
    build_header(draw, subtitle="DEEP DIVE #7")

    logo_r = 90
    draw_logo_circle(img, draw, W // 2, 470, logo_r, LOGO_PATH)
    draw = ImageDraw.Draw(img)

    title_font = font(B.SANS_BOLD, 56)
    title = f"{NAME_FULL}."
    tw = draw.textlength(title, font=title_font)
    draw.text((W / 2 - tw / 2, 620), title, font=title_font, fill=CREAM)

    sub_font = font(B.SANS_BOLD, 26)
    sub = f"Ein genauerer Blick auf {TICKER}."
    sw = draw.textlength(sub, font=sub_font)
    draw.text((W / 2 - sw / 2, 700), sub, font=sub_font, fill=ACCENT)

    tag_font = font(B.SANS_BOLD, 20)
    tag = "BEWERTUNG  ·  KURSANALYSE  ·  FUEHRUNGSWECHSEL"
    tgw = draw.textlength(tag, font=tag_font)
    draw.text((W / 2 - tgw / 2, 760), tag, font=tag_font, fill=MUTED)

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

    logo_r = 40
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = y + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, LOGO_PATH)
    draw = ImageDraw.Draw(img)
    name_x = logo_cx + logo_r + 22
    draw.text((name_x, y + 8), NAME_FULL, font=font(B.SANS_BOLD, 30), fill=CREAM)
    draw.text((name_x, y + 44), f"{TICKER}  ·  WKN {WKN}  ·  NASDAQ", font=font(B.SANS_BOLD, 18), fill=MUTED)

    y = logo_cy + logo_r + 24
    body_font = font(B.SANS_BOLD, 23)
    lines = wrap_text(draw, "Adobe steht hinter Photoshop, Premiere, Illustrator und Acrobat "
                             "-- Software, die kreative und dokumentbasierte Arbeit fast "
                             "ueberall im Berufsleben begleitet.", body_font,
                       W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33
    y += 10

    lines2 = wrap_text(draw, "Berichtet Donnerstag dieser Woche Quartalszahlen -- mitten in "
                              "einem gerade erst angekuendigten Fuehrungswechsel an der "
                              "Unternehmensspitze.", body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33

    y += 20
    cols, gap = 3, 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 66
    stats = [
        ("KURS", "266,51 USD"), ("MARKTKAP.", "105,9 Mrd. USD"), ("52W-HOCH", "370,86 USD"),
        ("52W-TIEF", "190,12 USD"), ("HAUPTSITZ", "San Jose, CA"), ("BOERSE", "NASDAQ"),
        ("SEGMENT", "Kreativ-/Dokument-Software"), ("NAECHSTE ZAHLEN", "10. Sept. 2026"), ("UMSATZ (TTM)", "25,2 Mrd. USD"),
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

    draw.text((B.MARGIN_LEFT, y), "Deutlich guenstiger als der eigene", font=font(B.SANS_BOLD, 27), fill=CREAM)
    y += 38
    draw.text((B.MARGIN_LEFT, y), "Softwaresektor.", font=font(B.SANS_BOLD, 27), fill=CREAM)
    y += 62

    cols, gap = 2, 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 78
    stats = [
        ("KGV (TRAILING)", "15,2x"), ("KGV (FORWARD)", "10,3x"),
        ("MARKTKAP.", "105,9 Mrd. USD"), ("UMSATZ-WACHSTUM", "+11,5%"),
    ]
    for i, (label, value) in enumerate(stats):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)
    y += 2 * (box_h + gap) + 16

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Mit einem KGV von 15,2x (forward 10,3x) ist Adobe deutlich "
                             "guenstiger bewertet als viele andere grosse Software-Aktien -- "
                             "der Markt preist Sorgen ein, ob generative KI Adobes teure "
                             "Kreativ-Tools langfristig ueberfluessig macht.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 3, 7)
    return img


def draw_heart_icon(draw, cx, cy, size, color):
    r = size * 0.28
    draw.ellipse([cx - size * 0.5, cy - size * 0.28, cx - size * 0.5 + 2 * r, cy - size * 0.28 + 2 * r],
                 fill=color)
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
    for line in ["Folge @dasdepotdiary,", "wenn du mehr Deep Dives willst.", "Und wenn dir das Format",
                 "gefaellt: liken, kommentieren,", "teilen -- hilft dem Account", "wirklich weiter."]:
        draw.text((B.MARGIN_LEFT, y), line, font=f2, fill=ACCENT)
        y += 46

    y += 50
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

    draw.text((B.MARGIN_LEFT, y), "Ein laengerer, zaeher Ruecksetzer.", font=font(B.SANS_BOLD, 30), fill=CREAM)
    y += 56

    chart_h = 400
    draw_price_chart(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, chart_h,
                      "Kursverlauf 1 Jahr -- 52W-Hoch 370,86 USD, 52W-Tief 190,12 USD")
    y += chart_h + 28

    body_font = font(B.SANS_BOLD, 22)
    lines = wrap_text(draw, "Die Aktie steht rund 28% unter ihrem 52-Wochen-Hoch -- ein "
                             "deutlich ruhigerer, laenger anhaltender Ruecksetzer als bei "
                             "vielen anderen Tech-Aktien, ohne die grossen Ausschlaege nach "
                             "oben oder unten.",
                       body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 32

    draw_footer(draw, 5, 7)
    return img


def slide_6_fuehrung():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "FUEHRUNGSWECHSEL", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    draw.text((B.MARGIN_LEFT, y), "Neue Spitze mitten in der Earnings-Woche.", font=font(B.SANS_BOLD, 26), fill=CREAM)
    y += 52

    items = [
        ("3. SEPTEMBER 2026", "Adobe kuendigte an: Anil Chakravarthy wird zum 1. Dezember neuer CEO, der bisherige CEO Shantanu Narayen (18 Jahre im Amt) wird Executive Chair."),
        ("GLEICHZEITIG", "David Wadhwani, bisher Chef des Creative-Cloud-Geschaefts (Photoshop, Premiere etc.), verlaesst das Unternehmen komplett -- ein groesserer Umbau der Fuehrungsebene als nur der CEO-Wechsel."),
    ]
    body_font = font(B.SANS_BOLD, 20)
    label_font = font(B.SANS_BOLD, 18)
    for label, text in items:
        draw.text((B.MARGIN_LEFT, y), label, font=label_font, fill=ACCENT)
        y += 26
        lines = wrap_text(draw, text, body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
        for line in lines:
            draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
            y += 28
        y += 18

    note_font = font(B.SANS_BOLD, 18)
    lines = wrap_text(draw, "Die Aktie gab am Tag nach der Ankuendigung rund 7% nach -- "
                             "Analysten zeigten sich laut Berichten ueberrascht von der Wahl. "
                             "Quelle: Unternehmensmitteilung, oeffentliche Berichterstattung.",
                       note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=MUTED)
        y += 26

    draw_footer(draw, 6, 7)
    return img


def slide_7_fazit():
    img, draw = base_slide()
    y = build_header(draw)
    draw.text((B.MARGIN_LEFT, y), "FAZIT", font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 40

    draw.text((B.MARGIN_LEFT, y), "Was ich mitnehme.", font=font(B.SANS_BOLD, 40), fill=CREAM)
    y += 66

    body_font = font(B.SANS_BOLD, 24)
    lines = wrap_text(draw, "Adobe ist im Vergleich zu anderen Software-Werten guenstig "
                             "bewertet -- aber mit gutem Grund: die KI-Frage (kann generative "
                             "KI Adobes Tools ersetzen?) und jetzt zusaetzlich ein "
                             "ueberraschender Fuehrungswechsel mitten in der wichtigsten "
                             "Berichtswoche. Die Zahlen am Donnerstag treffen also auf ein "
                             "Unternehmen im Umbruch.",
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
    draw.text((B.MARGIN_LEFT, y), "Folgen fuer mehr Deep Dives.", font=font(B.SANS_BOLD, 24), fill=ACCENT)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_1_intro, slide_2_overview, slide_3_bewertung, slide_4_cta,
              slide_5_kursanalyse, slide_6_fuehrung, slide_7_fazit]
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
