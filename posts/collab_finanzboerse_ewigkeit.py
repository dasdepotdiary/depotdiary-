"""Collab mit @finanzboerse: "5 Aktien fuer die Ewigkeit" -- auf Nutzerwunsch
vom 2026-09-08, neuer Stil ggue. den bisherigen finanzboerse-Collabs
(collab_finanzboerse_quotes.py, dunkles Gold/Navy-Palette bleibt, aber
Profilkarten-Layout statt Zitat-Paaren).

Bewusst OHNE Kurs/KGV/Marktkap-Zahlen -- eine "fuer die Ewigkeit"-Auswahl mit
tagesaktuellen Bewertungszahlen zu unterlegen waere sowohl inhaltlich
unpassend (die Zahlen veralten, der Titel nicht) als auch naeher an einer
Kaufempfehlung. Stattdessen rein qualitative, zeitlose Geschaeftsmodell-
Gruende (Moat/Diversifikation) -- explizit als persoenliche Auswahl markiert,
keine Bewertung, keine Empfehlung.

Ticker vom Nutzer vorgegeben: Amazon, Berkshire Hathaway, Visa, Alphabet,
Microsoft.

Aufruf:
  python posts/collab_finanzboerse_ewigkeit.py
"""
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
FB_GOLD_HEX = "#C9A239"
CREAM = (240, 238, 230)
MUTED = (140, 145, 158)

PARTNER_HANDLE = "@FINANZBOERSE"
OWN_HANDLE = "@DASDEPOTDIARY"

STOCKS = [
    {
        "ticker": "AMZN", "name": "Amazon", "logo": "amzn_logo_icon.png",
        "why": "E-Commerce-Marktfuehrer und mit AWS gleichzeitig das Cloud-Rueckgrat, "
               "auf dem ein grosser Teil des Internets laeuft -- zwei fuehrende "
               "Geschaeftsmodelle in einem Unternehmen.",
    },
    {
        "ticker": "BRK.B", "name": "Berkshire Hathaway", "logo": "brk_logo_icon.png",
        "why": "Kein einzelnes Unternehmen, sondern ein breit gestreutes Konglomerat -- "
               "Versicherung, Eisenbahn, Energie und ein eigenes Aktienportfolio in "
               "einer einzigen Position.",
    },
    {
        "ticker": "V", "name": "Visa", "logo": "v_logo_icon.png",
        "why": "Betreibt das Zahlungsnetzwerk, nicht das Kreditrisiko -- verdient an "
               "jeder Kartentransaktion weltweit, unabhaengig davon, ob Kunden ihre "
               "Rechnung bezahlen koennen.",
    },
    {
        "ticker": "GOOGL", "name": "Alphabet", "logo": "googl_logo_icon.png",
        "why": "Google-Suche, YouTube, Cloud und Waymo unter einem Dach -- eine "
               "der breitesten Datengrundlagen im gesamten Tech-Sektor.",
    },
    {
        "ticker": "MSFT", "name": "Microsoft", "logo": "msft_logo_icon.png",
        "why": "Windows und Office als Unternehmens-Standard weltweit, dazu Azure als "
               "eine der groessten Cloud-Plattformen -- tief in den Alltag von "
               "Firmen jeder Groesse eingebaut.",
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


def build_header(draw, y=40):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {PARTNER_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=FB_GOLD)
    y += 30
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=FB_CARD_BORDER, width=1)
    return y + 22


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- meine persoenliche Auswahl, kein Ratschlag."):
    disclaimer_font = font(B.SANS_BOLD, 18)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 40 - 26 * len(lines) - 12
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=FB_CARD_BORDER, width=1)
    dy = divider_y + 12
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 26
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 12), page_text, font=page_font, fill=MUTED)


def draw_logo_circle(img, draw, cx, cy, r, logo_path):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=FB_GOLD, width=2)
    logo = Image.open(logo_path).convert("RGBA")
    target = int(r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def base_slide():
    img = Image.new("RGB", (W, H), FB_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=FB_GOLD)
    return img, draw


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 110), "COLLAB", font=eyebrow_font, fill=FB_GOLD)

    title_font = font(B.SANS_BOLD, 52)
    lines = wrap_text(draw, "5 Aktien fuer die Ewigkeit.", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    y = 160
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 62

    y += 20
    sub_font = font(B.SANS_BOLD, 24)
    sub_lines = wrap_text(draw, "Zwei Accounts, zwei eigene Auswahlen -- das hier sind meine "
                                 "fuenf Positionen, die ich mir zutraue, sehr lange zu halten.",
                           sub_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in sub_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=sub_font, fill=FB_GOLD)
        y += 32

    y += 30
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=FB_CARD_BORDER, width=1)
    y += 24
    note_font = font(B.SANS_BOLD, 19)
    note_lines = wrap_text(draw, "Keine Rangfolge, keine Kaufempfehlung -- nur Unternehmen, "
                                  "deren Geschaeftsmodell ich langfristig fuer robust halte.",
                            note_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in note_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=note_font, fill=MUTED)
        y += 26

    draw_footer(draw, 1, 7)
    return img


def slide_stock(stock, idx, n_total):
    img, draw = base_slide()
    y = build_header(draw)

    draw.text((B.MARGIN_LEFT, y), f"{idx-1:02d} / 05", font=font(B.SANS_BOLD, 17), fill=FB_GOLD)
    y += 40

    logo_r = 70
    logo_cx = W // 2
    logo_cy = y + logo_r + 20
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, ROOT / "assets" / stock["logo"])
    draw = ImageDraw.Draw(img)

    y = logo_cy + logo_r + 40
    name_font = font(B.SANS_BOLD, 44)
    name_text = stock["name"]
    nw = draw.textlength(name_text, font=name_font)
    draw.text((W / 2 - nw / 2, y), name_text, font=name_font, fill=CREAM)
    y += 56

    ticker_font = font(B.SANS_BOLD, 22)
    ticker_text = stock["ticker"]
    tw = draw.textlength(ticker_text, font=ticker_font)
    draw.text((W / 2 - tw / 2, y), ticker_text, font=ticker_font, fill=FB_GOLD)
    y += 60

    draw.rounded_rectangle([B.MARGIN_LEFT, y, W - B.MARGIN_RIGHT, y + 260], radius=14,
                            fill=FB_CARD, outline=FB_CARD_BORDER, width=1)
    body_font = font(B.SANS_BOLD, 24)
    lines = wrap_text(draw, stock["why"], body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 56)
    by = y + 28
    for line in lines:
        draw.text((B.MARGIN_LEFT + 28, by), line, font=body_font, fill=CREAM)
        by += 34

    draw_footer(draw, idx, n_total)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)

    y += 20
    title_font = font(B.SANS_BOLD, 40)
    lines = wrap_text(draw, "Und die 5 von @finanzboerse?", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 50

    y += 20
    body_font = font(B.SANS_BOLD, 24)
    lines2 = wrap_text(draw, "Schau auf seinem Account vorbei fuer seine eigene Auswahl -- "
                              "spannend zu sehen, wo sich unsere Listen ueberschneiden und wo nicht.",
                        body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=FB_GOLD)
        y += 32

    y += 40
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=FB_GOLD, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Keine Rangfolge, keine Bewertung --", font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur meine persoenliche, langfristige Auswahl.", font=font(B.SANS_BOLD, 22), fill=CREAM)

    draw_footer(draw, 7, 7)
    return img


def main():
    slides = [slide_intro]
    for i, stock in enumerate(STOCKS, start=2):
        slides.append(lambda s=stock, i=i: slide_stock(s, i, 7))
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
