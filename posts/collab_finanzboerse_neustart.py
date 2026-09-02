"""Co-Post mit finanzboerse: 10 Aktienpaare -- "Wenn wir von null anfangen
wuerden", seine Wahl oben im Partner-Stil, meine Wahl unten im
depotdiary-Stil, echte Marktkap.-Daten.

Aufruf:
  python posts/collab_finanzboerse_neustart.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

NAME = "collab_finanzboerse_neustart"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE
MID = H // 2

FB_BG = (9, 13, 22)
FB_CARD = (17, 23, 37)
FB_GOLD = (201, 162, 57)
FB_GOLD_SOFT = (150, 128, 78)
FB_WHITE = (245, 245, 240)
FB_GREY = (150, 158, 175)


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_rank_badge(draw, cx, cy, r, rank):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=FB_GOLD, width=3)
    f = font(B.SANS_BOLD, int(r * 1.1))
    text = str(rank)
    tw = draw.textlength(text, font=f)
    draw.text((cx - tw / 2, cy - r * 0.72), text, font=f, fill=FB_GOLD)


def draw_partner_half(img, rank, ticker, name, headline, body, stat_value):
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MID], fill=FB_BG)

    pad = 40
    card_top, card_bottom = 150, MID - 40
    draw.rounded_rectangle([pad, card_top, W - pad, card_bottom], radius=18, fill=FB_CARD,
                            outline=FB_GOLD_SOFT, width=1)

    label_font = font(B.SANS_BOLD, 20)
    ticker_font = font(B.SANS_BOLD, 40)
    name_font = font(B.SANS_BOLD, 18)
    headline_font = font(B.SANS_BOLD, 27)
    body_font = font(B.SANS_BOLD, 20)
    stat_font = font(B.SANS_BOLD, 20)
    stat_val_font = font(B.SANS_BOLD, 26)

    draw_rank_badge(draw, W - pad - 44, card_top + 44, 26, rank)

    x = pad + 32
    y = card_top + 30
    draw.text((x, y), "@FINANZBOERSE", font=label_font, fill=FB_GOLD)
    y += 34
    draw.text((x, y), ticker, font=ticker_font, fill=FB_WHITE)
    tw = draw.textlength(ticker, font=ticker_font)
    draw.text((x + tw + 14, y + 18), name, font=name_font, fill=FB_GREY)
    y += 52
    draw.line([(x, y), (x + 90, y)], fill=FB_GOLD, width=2)
    y += 14
    draw.text((x, y), headline, font=headline_font, fill=FB_WHITE)
    y += 38
    for line in body:
        draw.text((x, y), line, font=body_font, fill=FB_GREY)
        y += 27

    tile_y = card_bottom - 70
    draw.rounded_rectangle([x, tile_y, W - pad - 32, tile_y + 46], radius=10, fill=FB_BG,
                            outline=FB_GOLD_SOFT, width=1)
    draw.text((x + 16, tile_y + 13), "MARKTKAP.", font=stat_font, fill=FB_GREY)
    vw = draw.textlength(stat_value, font=stat_val_font)
    draw.text((W - pad - 32 - 16 - vw, tile_y + 10), stat_value, font=stat_val_font, fill=FB_GOLD)

    wm_font = font(B.SANS_BOLD, 18)
    draw.text((x, card_bottom + 14), "FINANZBÖRSE", font=wm_font, fill=FB_GOLD)


def draw_depotdiary_half(draw, ticker, name, headline, body, stat_value):
    pad_x = B.MARGIN_LEFT
    max_w_right = W - B.MARGIN_RIGHT

    owner_font = font(B.SANS_BOLD, 20)
    ticker_font = font(B.SERIF_BOLD, 44)
    name_font = font(B.SERIF_REGULAR, 19)
    headline_font = font(B.SERIF_BOLD, 26)
    body_font = font(B.SERIF_REGULAR, 20)

    y = MID + 40
    draw.text((pad_x, y), "@DASDEPOTDIARY", font=owner_font, fill=B.GREEN)
    y += 34
    draw.text((pad_x, y), ticker, font=ticker_font, fill=B.INK)
    tw = draw.textlength(ticker, font=ticker_font)
    draw.text((pad_x + tw + 14, y + 16), name, font=name_font, fill=B.SUBTEXT)
    y += 58
    draw.text((pad_x, y), headline, font=headline_font, fill=B.INK)
    y += 38
    for line in body:
        draw.text((pad_x, y), line, font=body_font, fill=B.SUBTEXT)
        y += 29

    tile_h = 56
    y += 10
    draw.rectangle([pad_x, y, max_w_right, y + tile_h], fill=B.CARD)
    label_font = font(B.SERIF_BOLD, 19)
    val_font = font(B.SERIF_BOLD, 27)
    draw.text((pad_x + 20, y + 15), "MARKTKAP.", font=label_font, fill=B.INK)
    vw = draw.textlength(stat_value, font=val_font)
    draw.text((max_w_right - 20 - vw, y + 13), stat_value, font=val_font, fill=B.GREEN)


def build_slide(n_total, idx, rank, his, mine):
    img = Image.new("RGB", (W, H), B.BG)
    draw_partner_half(img, rank, his["ticker"], his["name"], his["headline"], his["body"], his["stat_value"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)
    draw.line([(0, MID), (W, MID)], fill=B.DIVIDER, width=3)

    draw_depotdiary_half(draw, mine["ticker"], mine["name"], mine["headline"], mine["body"], mine["stat_value"])

    disclaimer_font = font(B.SERIF_REGULAR, 17)
    draw.text((B.MARGIN_LEFT, H - 44), "Keine Anlageberatung. Beide Seiten: eigene Meinung, keine Empfehlung.",
               font=disclaimer_font, fill=B.SUBTEXT)

    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 70), page_text, font=page_font, fill=B.SUBTEXT)

    return img


def build_intro():
    img = Image.new("RGB", (W, H), FB_BG)
    draw = ImageDraw.Draw(img)
    for i, y in enumerate(range(140, H - 140, 46)):
        draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=(15, 20, 32), width=1)
    draw.text((B.MARGIN_LEFT, 90), "CO-POST", font=font(B.SANS_BOLD, 22), fill=FB_GOLD)
    draw.text((B.MARGIN_LEFT, 360), "Wenn wir von\nnull anfangen\nwuerden.",
               font=font(B.SANS_BOLD, 58), fill=FB_WHITE, spacing=18)
    draw.text((B.MARGIN_LEFT, 590), "Je 10 Aktien fuer ein neues Portfolio.",
               font=font(B.SANS_BOLD, 24), fill=FB_GOLD)
    draw.text((B.MARGIN_LEFT, H - 120), "@FINANZBOERSE  x  @DASDEPOTDIARY",
               font=font(B.SANS_BOLD, 22), fill=FB_GOLD)
    draw.text((B.MARGIN_LEFT, H - 80), "Keine Anlageberatung -- eigene Meinung, keine Empfehlung.",
               font=font(B.SANS_BOLD, 18), fill=FB_GREY)
    return img


PAIRS = [
    (
        {"ticker": "CRCL", "name": "Circle Internet Group", "headline": "Stablecoin-Emittent, seit IPO volatil",
         "body": ["Boersengang im Juni 2025,", "Kurs seither sehr schwankend."],
         "stat_value": "25,1 Mrd. USD"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "headline": "Cloud- und E-Commerce-Riese",
         "body": ["AWS bleibt der wichtigste", "Gewinntreiber im Konzern."],
         "stat_value": "2,79 Bio. USD"},
    ),
    (
        {"ticker": "PLUG", "name": "Plug Power Inc.", "headline": "Wasserstoff-Spezialist, weit unter altem Hoch",
         "body": ["Kurs bei rund 2,17 USD,", "deutlich unter fruehren Bewertungen."],
         "stat_value": "~3,0 Mrd. USD"},
        {"ticker": "ASML", "name": "ASML Holding N.V.", "headline": "Monopolist bei EUV-Lithografie",
         "body": ["Zentraler Zulieferer fuer die", "gesamte Halbleiterindustrie."],
         "stat_value": "675 Mrd. USD"},
    ),
    (
        {"ticker": "NVDA", "name": "Nvidia Corp.", "headline": "Aktie nach Q2-Zahlen fast 9% gesprungen",
         "body": ["96,22 Mrd. USD Umsatz, zweitgroesster", "Tagesgewinn der Börsengeschichte."],
         "stat_value": "5,49 Bio. USD"},
        {"ticker": "NOW", "name": "ServiceNow Inc.", "headline": "Cloud-Software fuer Unternehmensprozesse",
         "body": ["Rund +19% in den letzten 30 Tagen,", "deutliche Erholung."],
         "stat_value": "131,3 Mrd. USD"},
    ),
    (
        {"ticker": "AAPL", "name": "Apple Inc.", "headline": "Zweitwertvollstes Unternehmen der Welt",
         "body": ["iPhone bleibt Haupteinnahmequelle,", "Dienstleistungssparte waechst."],
         "stat_value": "4,60 Bio. USD"},
        {"ticker": "BRK.B", "name": "Berkshire Hathaway", "headline": "Beteiligungsholding von Warren Buffett",
         "body": ["Haelt u.a. grosse Positionen in", "Apple, Coca-Cola und Banken."],
         "stat_value": "1,08 Bio. USD"},
    ),
    (
        {"ticker": "O", "name": "Realty Income Corp.", "headline": "Monatliche Dividende seit ueber 30 Jahren",
         "body": ["670 Ausschuettungen in Folge,", "Dividendenrendite rund 5,25%."],
         "stat_value": "~59 Mrd. USD"},
        {"ticker": "CCJ", "name": "Cameco Corp.", "headline": "Groesster Uranproduzent Nordamerikas",
         "body": ["Profitiert von steigender Nachfrage", "nach Kernenergie fuer KI-Rechenzentren."],
         "stat_value": "46,3 Mrd. USD"},
    ),
    (
        {"ticker": "NKE", "name": "Nike Inc.", "headline": "Aktie nahe 12-Jahres-Tief",
         "body": ["Rund -50% Marktkap. im Jahresvergleich,", "schwierigstes Jahr seit 1993."],
         "stat_value": "57,1 Mrd. USD"},
        {"ticker": "RMS", "name": "Hermès International", "headline": "Luxuskonzern, u.a. bekannt fuer die Birkin Bag",
         "body": ["Wachstum in Asien schwaecht sich", "zuletzt etwas ab."],
         "stat_value": "193 Mrd. EUR"},
    ),
    (
        {"ticker": "VNA", "name": "Vonovia SE", "headline": "Groesster Wohnimmobilienkonzern Deutschlands",
         "body": ["Aktie nahe 52-Wochen-Tief,", "Analysten uneinig ueber Ausblick."],
         "stat_value": "~17,0 Mrd. EUR"},
        {"ticker": "VRT", "name": "Vertiv Holdings", "headline": "Kuehlung/Infrastruktur fuer KI-Rechenzentren",
         "body": ["Profitiert direkt vom Ausbau", "der globalen Rechenzentrums-Kapazitaet."],
         "stat_value": "~100 Mrd. USD"},
    ),
    (
        {"ticker": "BMW", "name": "BMW AG", "headline": "Einer der drei deutschen Premium-Autohersteller",
         "body": ["Aktie unter dem 52-Wochen-Hoch,", "schwaches Jahr bislang."],
         "stat_value": "34,7 Mrd. EUR"},
        {"ticker": "RTX", "name": "RTX Corp.", "headline": "Luft- und Ruestungskonzern",
         "body": ["Zu RTX gehoeren u.a. Raytheon,", "Pratt & Whitney und Collins Aerospace."],
         "stat_value": "~270 Mrd. USD"},
    ),
    (
        {"ticker": "MSFT", "name": "Microsoft Corp.", "headline": "In beiden Portfolios vertreten",
         "body": ["Cloud-Geschaeft (Azure) waechst", "weiter zweistellig."],
         "stat_value": "3,69 Bio. USD"},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "headline": "In beiden Portfolios vertreten",
         "body": ["Cloud-Geschaeft (Azure) waechst", "weiter zweistellig."],
         "stat_value": "3,69 Bio. USD"},
    ),
    (
        {"ticker": "V", "name": "Visa Inc.", "headline": "In beiden Portfolios vertreten",
         "body": ["Zahlungsnetzwerk mit globaler", "Reichweite, Allzeithoch im August."],
         "stat_value": "735,6 Mrd. USD"},
        {"ticker": "V", "name": "Visa Inc.", "headline": "In beiden Portfolios vertreten",
         "body": ["Zahlungsnetzwerk mit globaler", "Reichweite, Allzeithoch im August."],
         "stat_value": "735,6 Mrd. USD"},
    ),
]


def main():
    n = len(PAIRS) + 1
    build_intro().save(IG_DIR / "slide_1.png")
    for i, (his, mine) in enumerate(PAIRS, start=1):
        img = build_slide(n, i + 1, i, his, mine)
        img.save(IG_DIR / f"slide_{i + 1}.png")

    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, B.BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 3
    rows = (n + cols - 1) // cols
    gap = 20
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (245, 245, 245))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
