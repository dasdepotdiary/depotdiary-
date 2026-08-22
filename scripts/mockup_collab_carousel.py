"""Vorlaeufiger Design-Mockup fuer den geplanten Collab-Post mit 10 Aktien
(5 vom Partner rendite.radar.official, 5 von depotdiary) -- pro Folie eine
Aktie oben (Partner, in dessen eigenem Navy/Radar-Stil), eine unten
(depotdiary, in unserem Creme/Serif-Stil), klar getrennt. Reihenfolge und
Partner-Stil nach Analyse von dessen echten Posts (WhatsApp-Referenzvideo).
Platzhalter-Daten, nur zur Layout-Abstimmung.

Partner-Stil (rendite.radar.official): dunkles Navy (#0F1B33-artig),
konzentrische "Radar"-Ringe im Hintergrund, abgerundete dunkle Karte,
weisser fetter Sans-Serif-Text, "RENDITE RADAR" Wordmark unten links.

Aufruf:
  python scripts/mockup_collab_carousel.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

OUT = Path(__file__).parent.parent / "output" / "_mockup_collab"
OUT.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE
MID = H // 2

# Partner-Farben (aus Referenzvideo abgeleitet, kein offizieller Brand-Kit)
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


def draw_partner_half(draw, img, ticker, headline, body, stat_label, stat_value):
    """Obere Haelfte im rendite.radar.official-Stil: Navy, Radar-Ringe,
    dunkle abgerundete Karte, weisser Sans-Serif-Text."""
    draw.rectangle([0, 0, W, MID], fill=RR_NAVY_DARK)
    draw_radar_rings(img, W // 2, 90, 520, n=5)
    draw = ImageDraw.Draw(img)  # neu holen nach paste

    pad = 40
    card_top, card_bottom = 150, MID - 40
    draw.rounded_rectangle([pad, card_top, W - pad, card_bottom], radius=22, fill=RR_CARD)

    label_font = font(B.SANS_BOLD, 20)
    ticker_font = font(B.SANS_BOLD, 40)
    headline_font = font(B.SANS_BOLD, 30)
    body_font = font(B.SANS_BOLD, 21)
    stat_font = font(B.SANS_BOLD, 22)
    stat_val_font = font(B.SANS_BOLD, 26)

    x = pad + 32
    y = card_top + 30
    draw.text((x, y), "@RENDITE.RADAR.OFFICIAL", font=label_font, fill=RR_GREY)
    y += 34
    draw.text((x, y), ticker, font=ticker_font, fill=RR_WHITE)
    y += 52
    draw.text((x, y), headline, font=headline_font, fill=RR_WHITE)
    y += 42
    for line in body:
        draw.text((x, y), line, font=body_font, fill=RR_GREY)
        y += 28

    tile_y = card_bottom - 70
    draw.rounded_rectangle([x, tile_y, W - pad - 32, tile_y + 46], radius=10, fill=RR_NAVY_MID)
    draw.text((x + 16, tile_y + 12), stat_label, font=stat_font, fill=RR_GREY)
    vw = draw.textlength(stat_value, font=stat_val_font)
    draw.text((W - pad - 32 - 16 - vw, tile_y + 10), stat_value, font=stat_val_font, fill=RR_WHITE)

    wm_font = font(B.SANS_BOLD, 18)
    draw.text((x, card_bottom + 14), "RENDITE RADAR", font=wm_font, fill=RR_WHITE)


def draw_depotdiary_half(draw, ticker, headline, body, stat_label, stat_value):
    """Untere Haelfte im depotdiary-Stil: Creme, schwarzer Balken, Serife,
    gruener Akzent -- wie gewohnt."""
    pad_x = B.MARGIN_LEFT
    max_w_right = W - B.MARGIN_RIGHT

    owner_font = font(B.SANS_BOLD, 20)
    ticker_font = font(B.SERIF_BOLD, 44)
    headline_font = font(B.SERIF_BOLD, 27)
    body_font = font(B.SERIF_REGULAR, 21)

    y = MID + 40
    draw.text((pad_x, y), "@DASDEPOTDIARY", font=owner_font, fill=B.GREEN)
    y += 34
    draw.text((pad_x, y), ticker, font=ticker_font, fill=B.INK)
    y += 58
    draw.text((pad_x, y), headline, font=headline_font, fill=B.INK)
    y += 40
    for line in body:
        draw.text((pad_x, y), line, font=body_font, fill=B.SUBTEXT)
        y += 30

    tile_h = 60
    y += 12
    draw.rectangle([pad_x, y, max_w_right, y + tile_h], fill=B.CARD)
    label_font = font(B.SERIF_BOLD, 20)
    val_font = font(B.SERIF_BOLD, 28)
    draw.text((pad_x + 20, y + 16), stat_label, font=label_font, fill=B.INK)
    vw = draw.textlength(stat_value, font=val_font)
    draw.text((max_w_right - 20 - vw, y + 14), stat_value, font=val_font, fill=B.GREEN)


def build_slide(n_total, idx, his, mine):
    img = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(img)

    draw_partner_half(draw, img, his["ticker"], his["headline"], his["body"],
                       his["stat_label"], his["stat_value"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)
    draw.line([(0, MID), (W, MID)], fill=B.DIVIDER, width=3)

    draw_depotdiary_half(draw, mine["ticker"], mine["headline"], mine["body"],
                         mine["stat_label"], mine["stat_value"])

    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 44), page_text, font=page_font, fill=B.SUBTEXT)

    return img


def build_intro():
    img = Image.new("RGB", (W, H), RR_NAVY_DARK)
    draw = ImageDraw.Draw(img)
    draw_radar_rings(img, W // 2, MID, 700, n=7)
    draw = ImageDraw.Draw(img)
    draw.text((B.MARGIN_LEFT, 90), "CO-POST", font=font(B.SANS_BOLD, 22), fill=RR_GREY)
    draw.text((B.MARGIN_LEFT, 420), "10 Aktien.\n2 Accounts.\n1 Vergleich.",
               font=font(B.SANS_BOLD, 62), fill=RR_WHITE, spacing=18)
    draw.text((B.MARGIN_LEFT, H - 90), "@RENDITE.RADAR.OFFICIAL  x  @DASDEPOTDIARY",
               font=font(B.SANS_BOLD, 22), fill=RR_GREY)
    return img


def main():
    pairs = [
        ({"ticker": "TSLA", "headline": "Lieferzahlen leicht ruecklaeufig",
          "body": ["Q2-Auslieferungen unter Erwartung,", "Fokus verschiebt sich auf Robotaxi."],
          "stat_label": "KGV", "stat_value": "68,7"},
         {"ticker": "AMZN", "headline": "Q2 Umsatz +20%",
          "body": ["AWS waechst schneller als seit 2021,", "Cloud bleibt Wachstumstreiber."],
          "stat_label": "KGV", "stat_value": "34,2"}),
        ({"ticker": "NVDA", "headline": "KI-Nachfrage ungebrochen",
          "body": ["Rechenzentrums-Umsatz treibt Wachstum,", "Bewertung bleibt Streitpunkt."],
          "stat_label": "Marktkap.", "stat_value": "4,4 Bio. USD"},
         {"ticker": "MSFT", "headline": "Azure waechst stabil",
          "body": ["Cloud-Segment weiter zweistellig,", "KI-Integration in Kernprodukten."],
          "stat_label": "Marktkap.", "stat_value": "3,1 Bio. USD"}),
    ]
    build_intro().save(OUT / "slide_1.png")
    for i, (his, mine) in enumerate(pairs, start=1):
        img = build_slide(len(pairs) + 1, i + 1, his, mine)
        img.save(OUT / f"slide_{i + 1}.png")

    n = len(pairs) + 1
    cols = 3
    rows = (n + cols - 1) // cols
    gap = 20
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (245, 245, 245))
    for i in range(1, n + 1):
        im = Image.open(OUT / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUT / "uebersicht.png")
    print(f"Mockup: {OUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
