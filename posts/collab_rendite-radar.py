"""Finaler Co-Post mit rendite.radar.official: 5 Aktienpaare (seine Wahl oben
im Partner-Stil, meine Wahl unten im depotdiary-Stil), echte Marktkap.-Daten.

Aufruf:
  python posts/collab_rendite-radar.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

NAME = "collab_rendite-radar"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE
MID = H // 2

RR_NAVY_DARK = (13, 22, 41)
RR_NAVY_MID = (20, 33, 58)
RR_RING = (35, 52, 84)
RR_CARD = (24, 38, 66)
RR_WHITE = (255, 255, 255)
RR_GREY = (168, 180, 201)


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_radar_rings(img, cx, cy, max_r, n=5):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(n, 0, -1):
        r = int(max_r * i / n)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RR_RING, width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def draw_partner_half(img, ticker, name, headline, body, stat_value):
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MID], fill=RR_NAVY_DARK)
    draw_radar_rings(img, W // 2, 90, 520, n=5)
    draw = ImageDraw.Draw(img)

    pad = 40
    card_top, card_bottom = 150, MID - 40
    draw.rounded_rectangle([pad, card_top, W - pad, card_bottom], radius=22, fill=RR_CARD)

    label_font = font(B.SANS_BOLD, 20)
    ticker_font = font(B.SANS_BOLD, 40)
    name_font = font(B.SANS_BOLD, 18)
    headline_font = font(B.SANS_BOLD, 28)
    body_font = font(B.SANS_BOLD, 20)
    stat_font = font(B.SANS_BOLD, 22)
    stat_val_font = font(B.SANS_BOLD, 26)

    x = pad + 32
    y = card_top + 30
    draw.text((x, y), "@RENDITE.RADAR.OFFICIAL", font=label_font, fill=RR_GREY)
    y += 34
    draw.text((x, y), ticker, font=ticker_font, fill=RR_WHITE)
    tw = draw.textlength(ticker, font=ticker_font)
    draw.text((x + tw + 14, y + 18), name, font=name_font, fill=RR_GREY)
    y += 52
    draw.text((x, y), headline, font=headline_font, fill=RR_WHITE)
    y += 40
    for line in body:
        draw.text((x, y), line, font=body_font, fill=RR_GREY)
        y += 27

    tile_y = card_bottom - 70
    draw.rounded_rectangle([x, tile_y, W - pad - 32, tile_y + 46], radius=10, fill=RR_NAVY_MID)
    draw.text((x + 16, tile_y + 12), "MARKTKAP.", font=stat_font, fill=RR_GREY)
    vw = draw.textlength(stat_value, font=stat_val_font)
    draw.text((W - pad - 32 - 16 - vw, tile_y + 10), stat_value, font=stat_val_font, fill=RR_WHITE)

    wm_font = font(B.SANS_BOLD, 18)
    draw.text((x, card_bottom + 14), "RENDITE RADAR", font=wm_font, fill=RR_WHITE)


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


def build_slide(n_total, idx, his, mine):
    img = Image.new("RGB", (W, H), B.BG)
    draw_partner_half(img, his["ticker"], his["name"], his["headline"], his["body"], his["stat_value"])
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
    img = Image.new("RGB", (W, H), RR_NAVY_DARK)
    draw_radar_rings(img, W // 2, MID, 700, n=7)
    draw = ImageDraw.Draw(img)
    draw.text((B.MARGIN_LEFT, 90), "CO-POST", font=font(B.SANS_BOLD, 22), fill=RR_GREY)
    draw.text((B.MARGIN_LEFT, 420), "10 Aktien.\n2 Accounts.\n1 Vergleich.",
               font=font(B.SANS_BOLD, 62), fill=RR_WHITE, spacing=18)
    draw.text((B.MARGIN_LEFT, H - 120), "@RENDITE.RADAR.OFFICIAL  x  @DASDEPOTDIARY",
               font=font(B.SANS_BOLD, 22), fill=RR_GREY)
    draw.text((B.MARGIN_LEFT, H - 80), "Keine Anlageberatung -- eigene Meinung, keine Empfehlung.",
               font=font(B.SANS_BOLD, 18), fill=RR_GREY)
    return img


PAIRS = [
    (
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "headline": "Erstmals ueber 3 Bio. USD Marktkap.",
         "body": ["Nach starken Quartalszahlen im", "August 2026 kurzzeitig durchbrochen."],
         "stat_value": "2,79 Bio. USD"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "headline": "In beiden Depots vertreten",
         "body": ["AWS waechst schneller als seit 2021,", "Cloud bleibt Wachstumstreiber."],
         "stat_value": "2,79 Bio. USD"},
    ),
    (
        {"ticker": "ALV", "name": "Allianz SE", "headline": "Einer der groessten Versicherer weltweit",
         "body": ["Dividendenrendite rund 2,9%,", "KGV im Branchenvergleich moderat."],
         "stat_value": "168,5 Mrd. EUR"},
        {"ticker": "NOW", "name": "ServiceNow Inc.", "headline": "Forward-KGV deutlich unter TTM-KGV",
         "body": ["Markt erwartet spuerbares", "Gewinnwachstum in den naechsten Jahren."],
         "stat_value": "132,9 Mrd. USD"},
    ),
    (
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "headline": "KGV 28% ueber 10-Jahres-Schnitt",
         "body": ["Groesste US-Bank nach Bilanzsumme,", "getragen von starkem Handelsgeschaeft."],
         "stat_value": "959,5 Mrd. USD"},
        {"ticker": "V", "name": "Visa Inc.", "headline": "Stabiles Wachstum trotz Bewertungsfragen",
         "body": ["Zahlungsnetzwerk mit globaler Reichweite,", "KGV rund 31."],
         "stat_value": "684 Mrd. USD"},
    ),
    (
        {"ticker": "HLAG", "name": "Hapag-Lloyd AG", "headline": "Prognose fuer 2026 angehoben",
         "body": ["Container-Reederei mit stark", "zyklischem Ergebnisverlauf."],
         "stat_value": "~21,7 Mrd. EUR"},
        {"ticker": "ASML", "name": "ASML Holding N.V.", "headline": "Forward-KGV unter TTM-KGV",
         "body": ["Monopolist bei EUV-Lithografie-", "Anlagen fuer Halbleiterproduktion."],
         "stat_value": "725 Mrd. USD"},
    ),
    (
        {"ticker": "HAG", "name": "Hensoldt AG", "headline": "Deutscher Ruestungs- und Sensorkonzern",
         "body": ["Profitiert von hoeheren", "Verteidigungsausgaben in Europa."],
         "stat_value": "~9,3 Mrd. EUR"},
        {"ticker": "ZETA", "name": "Zeta Global Holdings", "headline": "Q2-Umsatz ueber Erwartungen",
         "body": ["443 Mio. USD Umsatz, Jahresprognose", "wegen KI-Nachfrage angehoben."],
         "stat_value": "7,2 Mrd. USD"},
    ),
]


def main():
    n = len(PAIRS) + 1
    build_intro().save(IG_DIR / "slide_1.png")
    for i, (his, mine) in enumerate(PAIRS, start=1):
        img = build_slide(n, i + 1, his, mine)
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
