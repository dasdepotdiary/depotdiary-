"""Co-Post mit @aktien.analyst: "3 gegen 3" -- je 3 Dividendenaktien pro
Seite, eine Aktie pro Folie (kein Split-Screen-Vergleich auf derselben Aktie).

FINALE PICKS (bestaetigt 2026-09-02):
  @aktien.analyst: Coca-Cola (KO), Procter & Gamble (PG), AT&T (T)
  @dasdepotdiary:  Novo Nordisk (NVO), Main Street Capital (MAIN), PepsiCo (PEP)
Ziel-Postzeitpunkt: 2026-09-02, 18:00 Uhr (Vorgabe von @aktien.analyst).

Aenderungen ggue. der Demo-Version (Nutzer-Feedback 2026-09-02):
- Kein "Ich halte X seit ..." mehr -- das genaue Datum ist nicht bekannt/
  nicht einheitlich zu belegen. Fuer die eigenen Picks (NVO/MAIN/PEP) daher
  Ich-Form OHNE Datumsangabe. Fuer die Partner-Picks (KO/PG/T) KEINE erfundene
  Ich-Perspektive fuer eine fremde Person -- stattdessen neutraler Fakten-Text
  (Dividendenhistorie/Kennzahlen), da ich seine tatsaechliche Begruendung
  nicht kenne.
- Titelfolie zeigt jetzt alle 6 Logos (3 gegen 3, zwei Spalten).
- Logo: echte Firmenlogos (Wikipedia, freigestellt) unter assets/*_logo_icon.png.
  Main Street Capital hat keine brauchbare Wikipedia-Logo-Quelle -- Monogramm-
  Platzhalter "MSC".

WICHTIG -- bewusst NICHT uebernommen aus der urspruenglichen Referenz: das
"Hannes' Meinung"/"Svens Meinung" + "HOT"-Rating-Format. Eine explizite
Hot/Cold-Einstufung oder Wachstumspotenzial-Aussage ist im Kern eine
Kaufempfehlung und faellt unter BaFin/MAR Art. 20 (siehe CLAUDE.md-Regel,
mehrfach verifiziert). Kein Rating, keine Bewertung, kein Kursziel.
Kurs-Chart ist eine reine Ist-Verlaufslinie (echte Tagesschlusskurse),
keine Trendlinie, keine eingezeichnete Prognose.

Aufruf:
  python posts/collab_aktienanalyst.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "collab_aktienanalyst"
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
CHART_LINE = "#C9A24B"
CHART_FILL = "#2A2416"

PARTNER_HANDLE = "@AKTIEN.ANALYST"
OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "3 GEGEN 3 -- DIVIDENDENAKTIEN IM VERGLEICH"

PICKS = [
    {
        "side": "partner", "ticker": "KO", "wkn": "850663", "name": "Coca-Cola",
        "logo_path": ROOT / "assets" / "ko_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_KO_prices.json",
        "stats": [
            ("DIV.-RENDITE", "2,4 %"), ("KURS", "88,00 USD"), ("KGV", "26,6"),
            ("MARKTKAP.", "381,5 Mrd. USD"), ("Q2-UMSATZ", "13,4 Mrd. USD"), ("UMSATZ-WACHSTUM", "+7 %"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 92,49 USD, 52W-Tief 65,35 USD",
        "note_lines": [
            "63 Jahre in Folge Dividende erhoeht (\"Dividend King\").",
            "Q2 2026: Umsatz +7% auf 13,4 Mrd. USD, organisches",
            "Wachstum +6%. Pick von @aktien.analyst.",
        ],
    },
    {
        "side": "partner", "ticker": "PG", "wkn": "852062", "name": "Procter & Gamble",
        "logo_path": ROOT / "assets" / "pg_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_PG_prices.json",
        "stats": [
            ("DIV.-RENDITE", "3,0 %"), ("KURS", "146,21 USD"), ("KGV", "22,0"),
            ("MARKTKAP.", "337,0 Mrd. USD"), ("UMSATZ FY26", "87,0 Mrd. USD"), ("UMSATZ-WACHSTUM", "+3,3 %"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 167,25 USD, 52W-Tief 137,62 USD",
        "note_lines": [
            "70 Jahre in Folge Dividende erhoeht -- eine der laengsten",
            "Erhoehungsserien im S&P 500. Umsatz FY2026: 87,0 Mrd. USD",
            "(+3,3%). Pick von @aktien.analyst.",
        ],
    },
    {
        "side": "partner", "ticker": "T", "wkn": "A0HL9Z", "name": "AT&T",
        "logo_path": ROOT / "assets" / "t_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_ATT_prices.json",
        "stats": [
            ("DIV.-RENDITE", "4,3 %"), ("KURS", "26,00 USD"), ("KGV", "8,5"),
            ("MARKTKAP.", "177,3 Mrd. USD"), ("52W-HOCH", "29,79 USD"), ("52W-TIEF", "19,89 USD"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 29,79 USD, 52W-Tief 19,89 USD",
        "note_lines": [
            "US-Telekomkonzern, deutlich niedrigeres KGV als die",
            "anderen Picks in dieser Runde. Dividende seit dem",
            "Spin-off von WarnerMedia 2022 neu kalibriert. Pick von @aktien.analyst.",
        ],
    },
    {
        "side": "depotdiary", "ticker": "NVO", "wkn": "A3EU6E", "name": "Novo Nordisk",
        "logo_path": ROOT / "assets" / "nvo_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_nvo_prices.json",
        "stats": [
            ("DIV.-RENDITE", "4,0 %"), ("KURS", "45,33 USD"), ("KGV", "11,3"),
            ("MARKTKAP.", "205,1 Mrd. USD"), ("Q2-UMSATZ", "78,5 Mrd. DKK"), ("UMSATZ-WACHSTUM", "+7 %"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 64,16 USD, 52W-Tief 35,12 USD",
        "reasoning": [
            "Ich halte Novo Nordisk wegen der Dividendenhistorie --",
            "seit 2000 ununterbrochen gezahlt, zuletzt von 0,80 auf",
            "1,80 USD je Aktie gestiegen (2022-2026). Wie sich der Kurs",
            "weiterentwickelt, weiss ich nicht -- das ist keine Prognose.",
        ],
    },
    {
        "side": "depotdiary", "ticker": "MAIN", "wkn": "A0X8Y3", "name": "Main Street Capital",
        "logo_path": None, "logo_letters": "MSC", "logo_bg": "#0B3D2E",
        "prices_path": ROOT / "data" / "demo_MAIN_prices.json",
        "stats": [
            ("DIV.-RENDITE", "5,5 %"), ("KURS", "57,97 USD"), ("KGV", "10,6"),
            ("MARKTKAP.", "5,2 Mrd. USD"), ("52W-HOCH", "67,34 USD"), ("52W-TIEF", "48,95 USD"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 67,34 USD, 52W-Tief 48,95 USD",
        "reasoning": [
            "Ich halte Main Street Capital wegen der monatlichen",
            "Dividende und der ueber 20-jaehrigen Historie als Business",
            "Development Company. Hoehere Rendite bedeutet hier auch",
            "hoeheres Risiko -- keine Empfehlung, nur meine Position.",
        ],
    },
    {
        "side": "depotdiary", "ticker": "PEP", "wkn": "851995", "name": "PepsiCo",
        "logo_path": ROOT / "assets" / "pep_logo_icon.png",
        "prices_path": ROOT / "data" / "demo_PEP_prices.json",
        "stats": [
            ("DIV.-RENDITE", "4,2 %"), ("KURS", "139,79 USD"), ("KGV", "18,4"),
            ("MARKTKAP.", "191,7 Mrd. USD"), ("Q2-UMSATZ-WACHSTUM", "+6,4 %"), ("52W-TIEF", "133,73 USD"),
        ],
        "chart_note": "Kursverlauf 1 Jahr -- 52W-Hoch 171,48 USD, 52W-Tief 133,73 USD",
        "reasoning": [
            "Ich halte PepsiCo wegen der 54 Jahre in Folge erhoehten",
            "Dividende und dem breiten Portfolio (Snacks + Getraenke).",
            "Q2 2026 lief mit +6,4% Umsatzwachstum solide. Wie sich der",
            "Kurs weiterentwickelt, weiss ich nicht -- das ist keine Prognose.",
        ],
    },
]


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


def draw_logo_circle(img, draw, cx, cy, r, pick):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=GOLD, width=2)
    if pick.get("logo_path"):
        logo = Image.open(pick["logo_path"]).convert("RGBA")
        target = int(r * 1.5)
        ratio = min(target / logo.width, target / logo.height)
        logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
        img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)
    else:
        letters = pick.get("logo_letters", "?")
        f = font(B.SANS_BOLD, int(r * 0.7))
        w = draw.textlength(letters, font=f)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pick.get("logo_bg", "#333"))
        draw.text((cx - w / 2, cy - r * 0.5), letters, font=f, fill=CREAM)


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


def build_header(draw, subtitle=SERIES_TITLE):
    y = 40
    handle_font = font(B.SANS_BOLD, 19)
    title_font = font(B.SANS_BOLD, 21)
    text = f"{PARTNER_HANDLE}  x  {OWN_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=GOLD)
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

    y = 210
    draw.text((B.MARGIN_LEFT, y), "3 gegen 3.", font=font(B.SANS_BOLD, 68), fill=CREAM)
    y += 82
    draw.text((B.MARGIN_LEFT, y), "Dividendenaktien im Vergleich.", font=font(B.SANS_BOLD, 40), fill=GOLD)
    y += 66
    draw.text((B.MARGIN_LEFT, y), "Je drei Picks pro Seite -- eine Aktie pro Folie.",
               font=font(B.SANS_BOLD, 24), fill=MUTED)

    y += 70
    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 60) / 2
    left_x = B.MARGIN_LEFT
    right_x = B.MARGIN_LEFT + col_w + 60
    draw.text((left_x, y), PARTNER_HANDLE, font=font(B.SANS_BOLD, 22), fill=GOLD)
    draw.text((right_x, y), OWN_HANDLE, font=font(B.SANS_BOLD, 22), fill=GREEN_MID)
    y += 44
    mid_x = left_x + col_w + 30
    draw.line([(mid_x, y - 10), (mid_x, y + 630)], fill=CARD_BORDER, width=1)

    logo_r = 60
    row_gap = 210
    partner_picks = [p for p in PICKS if p["side"] == "partner"]
    own_picks = [p for p in PICKS if p["side"] == "depotdiary"]
    name_font = font(B.SANS_BOLD, 22)
    for i, pick in enumerate(partner_picks):
        cy = y + logo_r + i * row_gap
        draw_logo_circle(img, draw, int(left_x + col_w / 2), cy, logo_r, pick)
        tw = draw.textlength(pick["ticker"], font=name_font)
        draw.text((left_x + col_w / 2 - tw / 2, cy + logo_r + 14), pick["ticker"], font=name_font, fill=CREAM)
    for i, pick in enumerate(own_picks):
        cy = y + logo_r + i * row_gap
        draw_logo_circle(img, draw, int(right_x + col_w / 2), cy, logo_r, pick)
        tw = draw.textlength(pick["ticker"], font=name_font)
        draw.text((right_x + col_w / 2 - tw / 2, cy + logo_r + 14), pick["ticker"], font=name_font, fill=CREAM)

    disclaimer_font = font(B.SANS_BOLD, 30)
    disclaimer_lines = wrap_text(draw, "Keine Anlageberatung -- nur, welche Aktien wir persoenlich halten.",
                                  disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    dy = H - 40 - 36 * len(disclaimer_lines)
    for line in disclaimer_lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 36
    return img


def build_stock_slide(pick, idx, n_total):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    y = build_header(draw)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)

    who = f"PICK VON {PARTNER_HANDLE}" if pick["side"] == "partner" else f"MEIN PICK ({OWN_HANDLE})"
    draw.text((B.MARGIN_LEFT, y), who, font=font(B.SANS_BOLD, 17), fill=GREEN_MID)
    y += 30

    logo_r = 44
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = y + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, pick)
    name_x = logo_cx + logo_r + 22
    name_font_size = 34 if len(pick["name"]) < 20 else 26
    draw.text((name_x, y + 4), pick["name"], font=font(B.SANS_BOLD, name_font_size), fill=CREAM)
    draw.text((name_x, y + 48), f"{pick['ticker']}  ·  WKN {pick['wkn']}",
               font=font(B.SANS_BOLD, 18), fill=MUTED)

    y = logo_cy + logo_r + 22
    cols = 3
    gap = 12
    box_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - (cols - 1) * gap) / cols
    box_h = 66
    for i, (label, value) in enumerate(pick["stats"]):
        row, col = divmod(i, cols)
        bx = B.MARGIN_LEFT + col * (box_w + gap)
        by = y + row * (box_h + gap)
        draw_stat_box(draw, bx, by, box_w, box_h, label, value)
    rows = (len(pick["stats"]) + cols - 1) // cols
    y += rows * (box_h + gap)

    y += 14
    chart_h = 340
    draw_price_chart(draw, B.MARGIN_LEFT, y, W - B.MARGIN_LEFT - B.MARGIN_RIGHT, chart_h,
                      pick["prices_path"], pick["chart_note"])
    y += chart_h + 32

    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=GOLD, width=3)
    y += 24
    body_font = font(B.SANS_BOLD, 22)
    lines = pick.get("reasoning") or pick.get("note_lines") or []
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 33

    disclaimer_font = font(B.SANS_BOLD, 28)
    disclaimer_lines = wrap_text(draw, "Keine Anlageberatung. Beide Seiten: eigene Meinung, keine Empfehlung.",
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
    n = len(PICKS) + 1
    build_intro().save(IG_DIR / "slide_1.png")
    for i, pick in enumerate(PICKS, start=2):
        build_stock_slide(pick, i, n).save(IG_DIR / f"slide_{i}.png")

    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 3
    rows = (n + cols - 1) // cols
    gap = 20
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (30, 30, 30))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
