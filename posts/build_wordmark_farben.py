"""Farbvarianten der zweifarbigen Wortmarke (Option W2, Nutzer-Favorit 2026-10-06:
"zwei schoene Farben, die zu Himmel und Skyline passen, Pink nicht unbedingt").
Nur Vorschlaege nach output/logo_optionen/ -- keine Live-Assets.

Aufruf:
  python posts/build_wordmark_farben.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, str(Path(__file__).parent))
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent
OUT = ROOT / "output" / "logo_optionen"
OUT.mkdir(parents=True, exist_ok=True)

CREAM = (245, 243, 238)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def text_mask(text, font, spacing, size):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    x = 0
    for ch in text:
        d.text((x, 0), ch, font=font, fill=255)
        x += d.textlength(ch, font=font) + spacing
    return m, x - spacing


def gradient(size, c1, c2):
    g = Image.new("RGB", size)
    px = g.load()
    for x in range(size[0]):
        t = x / max(1, size[0] - 1)
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        for y in range(size[1]):
            px[x, y] = col
    return g


def wordmark(col_a, col_b):
    """col_x: (c1, c2) -> Verlauf links nach rechts innerhalb des Wortes."""
    f = S.font(170)
    H = 230
    ma, wa = text_mask("DEPOT", f, 14, (900, H))
    mb, wb = text_mask("DIARY", f, 14, (900, H))
    gap = 56
    W = int(wa + gap + wb)
    out = Image.new("RGBA", (W + 10, H), (0, 0, 0, 0))
    ga = gradient((int(wa) + 2, H), col_a[0], col_a[1])
    gb = gradient((int(wb) + 2, H), col_b[0], col_b[1])
    out.paste(ga, (0, 0), ma.crop((0, 0, int(wa) + 2, H)))
    out.paste(gb, (int(wa + gap), 0), mb.crop((0, 0, int(wb) + 2, H)))
    box = out.getchannel("A").getbbox()
    return out.crop(box)


VARIANTEN = [
    ("V1 Weiss + Sonnenuntergang-Gold", ((CREAM, CREAM), (hex_rgb("#FFD166"), hex_rgb("#FF8A3D")))),
    ("V2 Gold + Orange (warm)", ((hex_rgb("#FFE29A"), hex_rgb("#FFC24D")), (hex_rgb("#FF9A4A"), hex_rgb("#FF6A3D")))),
    ("V3 Himmelblau + Orange (Komplementaer)", ((hex_rgb("#8FD3FF"), hex_rgb("#4DA8F5")), (hex_rgb("#FFB347"), hex_rgb("#FF7A3D")))),
    ("V4 Weiss + Blaue Stunde", ((CREAM, CREAM), (hex_rgb("#7FDBFF"), hex_rgb("#3A86FF")))),
]

HINTERGRUENDE = [
    ROOT / "assets" / "sk_nyc_wtc_sunset_still.jpg",
    ROOT / "assets" / "sk_dubai_burj_sunset_still.jpg",
    ROOT / "assets" / "sk_chicago_pink_still.jpg",
]


def cover(path, w, h, focus=0.3, dim=0.62):
    im = Image.open(path).convert("RGB")
    r = w / h
    if im.width / im.height > r:
        nw = int(im.height * r)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / r)
        y0 = int((im.height - nh) * focus)
        im = im.crop((0, y0, im.width, y0 + nh))
    return ImageEnhance.Brightness(im.resize((w, h), Image.LANCZOS)).enhance(dim)


def main():
    cw, ch = 560, 330
    sheet = Image.new("RGB", (cw * 4, ch * 3 + 60), (14, 14, 14))
    d = ImageDraw.Draw(sheet)
    marks = [wordmark(*v[1]) for v in VARIANTEN]
    for row, bg in enumerate(HINTERGRUENDE):
        for col, mk in enumerate(marks):
            cell = cover(bg, cw, ch, focus=0.25 + 0.1 * row)
            tw = cw - 80
            m = mk.resize((tw, int(mk.height * tw / mk.width)), Image.LANCZOS)
            cell = cell.convert("RGBA")
            cell.alpha_composite(m, (40, (ch - m.height) // 2))
            sheet.paste(cell.convert("RGB"), (col * cw, row * ch))
    for col, (name, _) in enumerate(VARIANTEN):
        d.text((col * cw + 14, ch * 3 + 18), name, font=S.font(22), fill=CREAM)
    sheet.save(OUT / "wordmark_farben.png")
    for (name, _), mk in zip(VARIANTEN, marks):
        mk.save(OUT / f"wordmark_{name[:2]}.png")
    print("fertig")


if __name__ == "__main__":
    main()
