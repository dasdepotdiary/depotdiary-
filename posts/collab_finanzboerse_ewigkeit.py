"""Collab mit @finanzboerse: "5 Aktien fuer die Ewigkeit" -- auf
Nutzerwunsch vom 2026-09-08 ueberarbeitet: echtes Paar-Format
("Verschmelzung unserer Formate"), oben @finanzboerse's Pick, unten
@dasdepotdiary's Pick, pro Slide -- Struktur analog zu
draw_quote_half()/build_paired_slide() aus collab_finanzboerse_quotes.py,
aber mit Logo-Karten statt Zitaten.

Ticker vom Nutzer vorgegeben: @finanzboerse waehlt Amazon, Berkshire
Hathaway, Visa, Alphabet, Microsoft; @dasdepotdiary (eigene Auswahl,
teils bewusst im selben Sektor gepaart) Apple, Novo Nordisk, Mastercard,
Costco, Nvidia.

Bewusst OHNE Kurs/KGV/Marktkap-Zahlen -- eine "fuer die Ewigkeit"-Auswahl
mit tagesaktuellen Bewertungszahlen zu unterlegen waere sowohl inhaltlich
unpassend (die Zahlen veralten, der Titel nicht) als auch naeher an einer
Kaufempfehlung. Rein qualitative, zeitlose Geschaeftsmodell-Gruende,
explizit als persoenliche Auswahl markiert, keine Rangfolge.

Aufruf:
  python posts/collab_finanzboerse_ewigkeit.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "collab_finanzboerse_ewigkeit"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

FB_BG = (9, 13, 22)
FB_CARD = (17, 23, 37)
FB_CARD_BORDER = (40, 46, 62)
FB_GOLD = (201, 162, 57)
CREAM = (240, 238, 230)
MUTED = (140, 145, 158)
GREEN = B.GREEN_MID

PARTNER_HANDLE = "@FINANZBOERSE"
OWN_HANDLE = "@DASDEPOTDIARY"

PAIRS = json.loads((ROOT / "posts" / "inputs" / "collab_finanzboerse_ewigkeit.json").read_text(encoding="utf-8"))["pairs"]


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


def build_header(draw, y=36):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {PARTNER_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=FB_GOLD)
    y += 28
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=FB_CARD_BORDER, width=1)
    return y + 18


def base_slide():
    img = Image.new("RGB", (W, H), FB_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=FB_GOLD)
    return img, draw


def draw_pick_half(img, draw, top, bottom, pick, who_label, accent):
    half_h = bottom - top
    draw.text((B.MARGIN_LEFT, top), who_label, font=font(B.SANS_BOLD, 15), fill=accent)

    logo_r = 46
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = top + 34 + logo_r
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
                 fill=CREAM, outline=accent, width=2)
    logo = Image.open(ROOT / "assets" / pick["logo"]).convert("RGBA")
    target = int(logo_r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (logo_cx - logo.width // 2, logo_cy - logo.height // 2), logo)
    draw = ImageDraw.Draw(img)

    text_x = logo_cx + logo_r + 24
    name_font = font(B.SANS_BOLD, 26)
    draw.text((text_x, top + 30), pick["name"], font=name_font, fill=CREAM)
    ticker_font = font(B.SANS_BOLD, 17)
    draw.text((text_x, top + 62), pick["ticker"], font=ticker_font, fill=accent)

    why_font = font(B.SANS_BOLD, 18)
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    lines = wrap_text(draw, pick["why"], why_font, max_w)
    y = logo_cy + logo_r + 20
    for line in lines[:4]:
        draw.text((B.MARGIN_LEFT, y), line, font=why_font, fill=MUTED)
        y += 25
    return draw


def draw_vs_badge(img, draw, cx, cy, r=52):
    """Zweigeteiltes Rundbadge (Gold/Gruen diagonal) mit 'VS' und Schlagschatten --
    sitzt auf der Trennlinie zwischen den beiden Picks, damit sich jedes Paar
    wie ein echtes Showdown-Duell statt nur zwei uebereinander gestapelte
    Karten liest."""
    pad = 10
    size = (r + pad) * 2
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)

    shadow_off = 5
    ldraw.ellipse([pad - shadow_off + shadow_off, pad - shadow_off + shadow_off,
                   pad + 2 * r + shadow_off, pad + 2 * r + shadow_off], fill=(0, 0, 0, 110))

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([pad, pad, pad + 2 * r, pad + 2 * r], fill=255)

    badge = Image.new("RGB", (size, size), FB_GOLD)
    bdraw = ImageDraw.Draw(badge)
    bdraw.polygon([(pad, pad + 2 * r), (pad + 2 * r, pad), (pad + 2 * r, pad + 2 * r)], fill=GREEN)
    bdraw.line([(pad, pad + 2 * r), (pad + 2 * r, pad)], fill=CREAM, width=4)

    layer.paste(badge, (0, 0), mask)
    img.paste(layer, (cx - size // 2, cy - size // 2), layer)
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CREAM, width=4)

    vs_font = font(B.SANS_BOLD, 34)
    vs_text = "VS"
    tw = draw.textlength(vs_text, font=vs_font)
    draw.text((cx - tw / 2 + 2, cy - 21 + 2), vs_text, font=vs_font, fill=(0, 0, 0, 90))
    draw.text((cx - tw / 2, cy - 21), vs_text, font=vs_font, fill=CREAM,
              stroke_width=3, stroke_fill=(20, 18, 15))
    return draw


def draw_mini_logo(img, cx, cy, r, logo_path, ring_color):
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=ring_color, width=3)
    logo = Image.open(ROOT / "assets" / logo_path).convert("RGBA")
    target = int(r * 1.4)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def slide_intro():
    """Titelfolie im Stil von collab_aktienanalyst.py ("3 gegen 3"): zwei
    Spalten mit allen Logos untereinander, eine Spalte pro Account -- die
    "Verschmelzung" beider Formate, die es bei den alten Collabs schon gab,
    jetzt fuer 5 gegen 5 statt 3 gegen 3, plus VS-Badge auf der Trennlinie."""
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 90), "COLLAB · SHOWDOWN", font=eyebrow_font, fill=FB_GOLD)

    y = 128
    draw.text((B.MARGIN_LEFT, y), "5 gegen 5.", font=font(B.SANS_BOLD, 56), fill=CREAM)
    y += 66
    draw.text((B.MARGIN_LEFT, y), "Aktien fuer die Ewigkeit.", font=font(B.SANS_BOLD, 34), fill=FB_GOLD)
    y += 46
    draw.text((B.MARGIN_LEFT, y), "Je fuenf Picks pro Seite -- ein Duell pro Slide.",
               font=font(B.SANS_BOLD, 20), fill=MUTED)
    y += 46

    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 60) / 2
    left_x = B.MARGIN_LEFT
    right_x = B.MARGIN_LEFT + col_w + 60
    draw.text((left_x, y), PARTNER_HANDLE, font=font(B.SANS_BOLD, 19), fill=FB_GOLD)
    draw.text((right_x, y), OWN_HANDLE, font=font(B.SANS_BOLD, 19), fill=GREEN)
    y += 36

    mid_x = left_x + col_w + 30
    rows_top = y
    row_gap = 128
    logo_r = 40
    name_font = font(B.SANS_BOLD, 18)

    for i, pair in enumerate(PAIRS):
        cy = rows_top + logo_r + i * row_gap
        draw_mini_logo(img, int(left_x + col_w / 2), cy, logo_r, pair["partner"]["logo"], FB_GOLD)
        tw = draw.textlength(pair["partner"]["ticker"], font=name_font)
        draw.text((left_x + col_w / 2 - tw / 2, cy + logo_r + 10), pair["partner"]["ticker"], font=name_font, fill=CREAM)

        draw_mini_logo(img, int(right_x + col_w / 2), cy, logo_r, pair["own"]["logo"], GREEN)
        tw = draw.textlength(pair["own"]["ticker"], font=name_font)
        draw.text((right_x + col_w / 2 - tw / 2, cy + logo_r + 10), pair["own"]["ticker"], font=name_font, fill=CREAM)

    rows_bottom = rows_top + logo_r + (len(PAIRS) - 1) * row_gap + logo_r + 30
    draw.line([(mid_x, rows_top - 6), (mid_x, rows_bottom)], fill=FB_CARD_BORDER, width=1)
    draw = draw_vs_badge(img, draw, int(mid_x), int((rows_top + rows_bottom) / 2), r=40)

    draw_footer(draw, 1, 7)
    return img


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- persoenliche Auswahl, kein Ratschlag."):
    disclaimer_font = font(B.SANS_BOLD, 17)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 36 - 24 * len(lines) - 10
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=FB_CARD_BORDER, width=1)
    dy = divider_y + 10
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 24
    page_font = font(B.SANS_BOLD, 17)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 10), page_text, font=page_font, fill=MUTED)


def slide_pair(pair, idx, n_total):
    img, draw = base_slide()
    top = build_header(draw)

    footer_h = 70
    footer_top = H - footer_h
    usable_bottom = footer_top - 10
    half_h = (usable_bottom - top - 16) // 2
    mid_y = top + half_h + 8

    draw = draw_pick_half(img, draw, top, mid_y - 8, pair["partner"], f"PICK VON {PARTNER_HANDLE}", FB_GOLD)
    draw.line([(B.MARGIN_LEFT, mid_y), (W - B.MARGIN_RIGHT, mid_y)], fill=FB_CARD_BORDER, width=1)
    draw = draw_pick_half(img, draw, mid_y + 14, usable_bottom, pair["own"], f"MEIN PICK ({OWN_HANDLE})", GREEN)

    draw_vs_badge(img, draw, W - B.MARGIN_RIGHT - 60, mid_y, r=34)
    draw = ImageDraw.Draw(img)

    draw_footer(draw, idx, n_total)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)

    y += 20
    title_font = font(B.SANS_BOLD, 38)
    lines = wrap_text(draw, "Welche der 10 wuerdest du", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 48
    draw.text((B.MARGIN_LEFT, y), "selbst halten?", font=title_font, fill=CREAM)
    y += 70

    body_font = font(B.SANS_BOLD, 23)
    lines2 = wrap_text(draw, "Schreib's uns in die Kommentare -- bei beiden Accounts.",
                        body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=FB_GOLD)
        y += 30

    y += 40
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=FB_GOLD, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Keine Rangfolge, keine Bewertung --", font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur unsere persoenliche, langfristige Auswahl.", font=font(B.SANS_BOLD, 22), fill=CREAM)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_intro]
    for i, pair in enumerate(PAIRS, start=2):
        slides.append(lambda p=pair, i=i: slide_pair(p, i, 7))
    slides.append(slide_outro)

    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, FB_BG)
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
