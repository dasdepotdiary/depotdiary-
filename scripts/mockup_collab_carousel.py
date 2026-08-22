"""Vorlaeufiger Design-Mockup fuer den geplanten Collab-Post mit 10 Aktien
(5 von depotdiary, 5 vom Partner-Account) -- pro Folie eine Aktie oben
(depotdiary), eine unten (Partner), getrennt durch eine mittige Trennlinie
und Label. Platzhalter-Daten, nur zur Layout-Abstimmung.

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


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_half(draw, y_top, y_bottom, owner_label, ticker, headline, stat_label, stat_value, accent):
    pad_x = B.MARGIN_LEFT
    max_w = W - B.MARGIN_RIGHT - pad_x

    owner_font = font(B.SANS_BOLD, 24)
    ticker_font = font(B.SERIF_BOLD, 56)
    headline_font = font(B.SERIF_REGULAR, 26)
    stat_label_font = font(B.SERIF_BOLD, 22)
    stat_value_font = font(B.SERIF_BOLD, 34)

    y = y_top + 36
    draw.text((pad_x, y), owner_label.upper(), font=owner_font, fill=accent)
    y += 40
    draw.text((pad_x, y), ticker, font=ticker_font, fill=B.INK)
    y += 72
    draw.text((pad_x, y), headline, font=headline_font, fill=B.SUBTEXT)
    y += 44

    tile_h = 74
    draw.rectangle([pad_x, y, W - B.MARGIN_RIGHT, y + tile_h], fill=B.CARD)
    draw.text((pad_x + 20, y + 14), stat_label, font=stat_label_font, fill=B.INK)
    vw = draw.textlength(stat_value, font=stat_value_font)
    draw.text((W - B.MARGIN_RIGHT - 20 - vw, y + 18), stat_value, font=stat_value_font, fill=accent)


def build_slide(n_total, idx, mine, his):
    img = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)

    mid = H // 2
    draw_half(draw, 0, mid, "@dasdepotdiary", mine["ticker"], mine["headline"],
               mine["stat_label"], mine["stat_value"], B.GREEN)

    divider_y = mid
    draw.line([(0, divider_y), (W, divider_y)], fill=B.DIVIDER, width=3)
    draw.ellipse([W // 2 - 22, divider_y - 22, W // 2 + 22, divider_y + 22], fill=B.BG, outline=B.DIVIDER, width=2)
    vs_font = font(B.SANS_BOLD, 22)
    vs_w = draw.textlength("VS", font=vs_font)
    draw.text((W // 2 - vs_w / 2, divider_y - 13), "VS", font=vs_font, fill=B.INK)

    draw_half(draw, mid, H, "@partner_account", his["ticker"], his["headline"],
               his["stat_label"], his["stat_value"], B.OCHRE)

    footer_font = font(B.SANS_BOLD, 20)
    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((B.MARGIN_LEFT, H - 44), "DEPOT DIARY x PARTNER", font=footer_font, fill=B.INK)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 44), page_text, font=page_font, fill=B.SUBTEXT)

    return img


def main():
    pairs = [
        ({"ticker": "AMZN", "headline": "Q2 Umsatz +20% ggue. Vorjahr", "stat_label": "KGV", "stat_value": "34,2"},
         {"ticker": "TSLA", "headline": "Lieferzahlen leicht ruecklaeufig", "stat_label": "KGV", "stat_value": "68,7"}),
        ({"ticker": "MSFT", "headline": "Azure-Wachstum bleibt stark", "stat_label": "Marktkap.", "stat_value": "3,1 Bio. USD"},
         {"ticker": "NVDA", "headline": "KI-Nachfrage weiter ungebrochen", "stat_label": "Marktkap.", "stat_value": "4,4 Bio. USD"}),
    ]
    for i, (mine, his) in enumerate(pairs, start=1):
        img = build_slide(len(pairs) + 1, i + 1, mine, his)
        img.save(OUT / f"slide_{i + 1}.png")

    # Intro-Folie (Platzhalter)
    intro = Image.new("RGB", (W, H), B.BG)
    d = ImageDraw.Draw(intro)
    d.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)
    d.text((B.MARGIN_LEFT, 56), "CO-POST", font=font(B.SANS_BOLD, B.EYEBROW_SIZE), fill=B.SUBTEXT)
    d.text((B.MARGIN_LEFT, 220), "5 Aktien.\n2 Depots.\n1 Vergleich.",
            font=font(B.SERIF_BOLD, 64), fill=B.INK, spacing=16)
    intro.save(OUT / "slide_1.png")

    # Kontaktabzug
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
