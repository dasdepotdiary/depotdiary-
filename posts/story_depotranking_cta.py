"""Call-to-Action-Story fuer echte Depot-Ranking-Einsendungen (2026-09-11).

Bittet Follower per DM ihr Depot zu schicken (nur Prozente/Struktur, keine
Aktiennamen noetig) -- Grundlage fuer eine spaetere ECHTE Ausgabe von
Depot-Ranking (bisher nur fiktive Beispiele). Gleiche dunkle Tier-Liste-
Optik wie format_depotranking.py, damit die Story klar dem Format
zugeordnet wird.

Aufruf:
  python posts/story_depotranking_cta.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "story_depotranking_cta"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (26, 29, 36)
BG_BOTTOM = (13, 15, 20)
CREAM = "#F2F0EA"
MUTED = "#9B9BA8"
GOLD = "#F5C518"
OWN_HANDLE = "@DASDEPOTDIARY"


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


def gradient_background(top_rgb, bottom_rgb):
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_radial_glow(img, cx, cy, radius, color, strength=55):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def main():
    """v2 (2026-10-05): depotdiary-Foto-Schema (posts/style_finanzhafen.py) statt dunkler Flaeche."""
    sys.path.insert(0, str(Path(__file__).parent))
    import style_finanzhafen as S
    img = S.draw_cta_story("depotranking", "DEPOT-RANKING", ['JETZT ECHT.', 'SCHICK UNS', 'DEIN DEPOT.'],
        "Nur die Struktur zaehlt: wie viel Prozent in Aktien, ETFs, Krypto, Cash. Keine Aktiennamen noetig, keine echten Betraege.",
        "Schick's uns per DM.", "Wird anonymisiert -- bewertet wird nur die Struktur, keine Anlageberatung.")
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
