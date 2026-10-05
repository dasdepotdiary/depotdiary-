"""Logo-/Profilbild-Optionen im neuen depotdiary-Foto-Schema (2026-10-05,
Nutzer: "die Depot-Diary-Logos muessten wir noch ueberarbeiten"). Baut nur
VORSCHLAEGE nach output/logo_optionen/ -- aendert keine Live-Assets.

Aufruf:
  python posts/build_logo_optionen.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent
OUT = ROOT / "output" / "logo_optionen"
OUT.mkdir(parents=True, exist_ok=True)

CREAM = (245, 243, 238)
BLACK = (10, 10, 10)
LIME = (182, 255, 61)
CYAN = (76, 201, 240)
PINK = (255, 62, 165)
YELLOW = (255, 221, 61)


def spaced(draw, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x - spacing


def spaced_width(draw, text, font, spacing):
    return sum(draw.textlength(ch, font=font) for ch in text) + spacing * (len(text) - 1)


def photo_square(path, size, focus_y=0.25, dim=0.55):
    im = Image.open(path).convert("RGB")
    side = min(im.size)
    x0 = (im.width - side) // 2
    y0 = int((im.height - side) * focus_y)
    im = im.crop((x0, y0, x0 + side, y0 + side)).resize((size, size), Image.LANCZOS)
    return ImageEnhance.Brightness(im).enhance(dim)


def wordmark_stacked(accent):
    """Option W1: gestapelt, weiss, Akzent-Balken."""
    img = Image.new("RGBA", (900, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = S.font(150)
    for i, word in enumerate(("DEPOT", "DIARY")):
        w = spaced_width(d, word, f, 26)
        spaced(d, ((900 - w) / 2, 20 + i * 200), word, f, CREAM, 26)
    d.rectangle([150, 188, 750, 202], fill=accent)
    return img


def wordmark_twotone(accent):
    """Option W2: eine Zeile, DEPOT weiss / DIARY in Akzentfarbe."""
    img = Image.new("RGBA", (1500, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = S.font(170)
    x = spaced(d, (20, 30), "DEPOT", f, CREAM, 14)
    spaced(d, (x + 50, 30), "DIARY", f, accent, 14)
    return img


def wordmark_badge(accent):
    """Option W3: DD-Badge (abgerundetes Quadrat) + Schriftzug."""
    img = Image.new("RGBA", (1500, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([10, 10, 290, 290], radius=56, fill=accent)
    bf = S.font(170)
    w = d.textlength("DD", font=bf)
    d.text((150 - w / 2, 62), "DD", font=bf, fill=BLACK)
    f = S.font(120)
    spaced(d, (340, 28), "DEPOT", f, CREAM, 20)
    spaced(d, (340, 156), "DIARY", f, CREAM, 20)
    return img


def profile_photo(accent):
    """P1: Skyline-Foto, grosses DD, Akzent-Ring + Balken."""
    img = photo_square(ROOT / "assets" / "sk_nyc_wtc_sunset_still.jpg", 1080, 0.18, 0.62).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 90))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img)
    d.ellipse([40, 40, 1040, 1040], outline=accent, width=14)
    f = S.font(430)
    w = d.textlength("DD", font=f)
    d.text((540 - w / 2 + 6, 300), "DD", font=f, fill=(0, 0, 0, 255))
    d.text((540 - w / 2, 294), "DD", font=f, fill=CREAM)
    d.rectangle([340, 770, 740, 786], fill=accent)
    return img.convert("RGB")


def profile_chart(accent):
    """P2: fast schwarz, DD + steigende Kurve."""
    img = Image.new("RGB", (1080, 1080), (10, 10, 11))
    glow = Image.new("L", (1080, 1080), 0)
    ImageDraw.Draw(glow).ellipse([240, 200, 840, 800], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.paste(Image.new("RGB", (1080, 1080), tuple(int(c * 0.45) for c in accent)), (0, 0), glow)
    d = ImageDraw.Draw(img)
    pts = [(150, 820), (300, 700), (410, 760), (560, 560), (680, 620), (900, 330)]
    d.line(pts, fill=accent, width=20, joint="curve")
    r = 26
    d.ellipse([900 - r, 330 - r, 900 + r, 330 + r], fill=accent)
    f = S.font(400)
    w = d.textlength("DD", font=f)
    d.text((540 - w / 2, 330), "DD", font=f, fill=CREAM)
    return img


def profile_solid(accent):
    """P3: vivide Vollflaeche, schwarzes DD -- faellt im Feed/Highlights stark auf."""
    img = Image.new("RGB", (1080, 1080), accent)
    d = ImageDraw.Draw(img)
    f = S.font(500)
    w = d.textlength("DD", font=f)
    d.text((540 - w / 2, 250), "DD", font=f, fill=BLACK)
    d.rectangle([330, 800, 750, 822], fill=BLACK)
    return img


def circle(img, size):
    img = img.convert("RGB").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def main():
    marks = [("W1_gestapelt", wordmark_stacked(CYAN)),
             ("W2_zweifarbig", wordmark_twotone(PINK)),
             ("W3_badge", wordmark_badge(LIME))]
    profs = [("P1_foto", profile_photo(YELLOW)),
             ("P2_kurve", profile_chart(CYAN)),
             ("P3_vollflaeche", profile_solid(LIME))]
    for name, im in marks:
        im.save(OUT / f"{name}.png")
    for name, im in profs:
        im.save(OUT / f"{name}.png")

    bg = photo_square(ROOT / "assets" / "sk_frankfurt_night_still.jpg", 1800, 0.35, 0.5)
    sheet = Image.new("RGB", (1800, 1100), (14, 14, 14))
    sheet.paste(bg.crop((0, 0, 1800, 520)), (0, 0))
    cell_w = 600
    for i, (name, im) in enumerate(marks):
        w = cell_w - 60
        scale = w / im.width
        r = im.resize((w, int(im.height * scale)), Image.LANCZOS)
        sheet.paste(r, (i * cell_w + 30, 260 - r.height // 2), r)
    d = ImageDraw.Draw(sheet)
    for i, (name, _) in enumerate(marks):
        d.text((i * cell_w + 40, 490), name, font=S.font(24), fill=CREAM)
    for i, (name, im) in enumerate(profs):
        c = circle(im, 420)
        sheet.paste(c, (i * cell_w + 90, 560), c)
        d.text((i * cell_w + 90, 1000), name + " (Kreis-Ansicht wie auf Instagram)", font=S.font(24), fill=CREAM)
    sheet.save(OUT / "uebersicht.png")
    print("fertig", OUT)


if __name__ == "__main__":
    main()
