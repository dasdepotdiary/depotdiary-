"""Erzeugt das Open-Graph-Vorschaubild (1200x630) fuer Link-Previews."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw
import brand as B
from render import _font, _draw_tracked, _text_w, _line_height

ROOT = Path(__file__).parent.parent
SIZE = (1200, 630)


def main():
    img = Image.new("RGB", SIZE, B.BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 20, SIZE[1]], fill=B.INK)

    eyebrow_font = _font(B.SANS_BOLD, 30)
    _draw_tracked(draw, (80, 90), "PORTFOLIO · LIVE", eyebrow_font, B.SUBTEXT, 6)

    headline_font = _font(B.SERIF_BOLD, 92)
    accent_font = _font(B.SERIF_BOLD_ITALIC, 92)
    y = 210
    x = 80
    draw.text((x, y), "Mein Depot, ", font=headline_font, fill=B.INK)
    x += _text_w(draw, "Mein Depot, ", headline_font)
    draw.text((x, y), "offen", font=accent_font, fill=B.GREEN)
    x += _text_w(draw, "offen", accent_font)
    draw.text((x, y), "", font=headline_font, fill=B.INK)
    y += _line_height(headline_font) + 8
    draw.text((80, y), "dokumentiert.", font=headline_font, fill=B.INK)

    y += _line_height(headline_font) + 30
    draw.rectangle([80, y, 280, y + 6], fill=B.GREEN)
    y += 40

    body_font = _font(B.SERIF_REGULAR, 34)
    draw.text((80, y), "19, seit ich 14 bin dabei — in Prozent, nicht in Euro.", font=body_font, fill=B.BODY_TEXT)
    y += _line_height(body_font) + 50

    word_font = _font(B.SANS_BOLD, 26)
    _draw_tracked(draw, (80, y), "DEPOT DIARY", word_font, B.INK, 3)

    out_path = ROOT / "docs" / "assets" / "og-image.png"
    img.save(out_path)
    print("OG-Bild:", out_path)


if __name__ == "__main__":
    main()
