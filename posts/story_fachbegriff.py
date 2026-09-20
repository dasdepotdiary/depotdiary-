"""Taegliches (evergreen) Story-Format "FACHBEGRIFF DES TAGES" -- ein
Finanzbegriff kurz und einfach erklaert. Braucht keine tagesaktuellen Daten,
kann also auch an ruhigen Tagen laufen. Rein erklaerend, keine Bewertung.

v2 (2026-09-16, Nutzer-Feedback "gefaellt mir nicht, hoer auf mit dem Gelben
am Rand, neues schoeneres Design"): komplett neu -- zentrierte Flashcard-
Optik statt Linksbuendig+Akzentbalken, tiefes Bordeaux/Weinrot statt Gruen,
Rosegold-Akzent statt Ochre, keine linke Randleiste.

Input: term, definition (1-2 Saetze), example (optional, 1 Satz).

Aufruf (Prototyp/Test):
  python posts/story_fachbegriff.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font

NAME = "story_fachbegriff"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
BG_TOP = (58, 24, 34)
BG_BOTTOM = (28, 10, 16)
INK = "#F7EFE9"
SUBTEXT = "#D9B8B0"
ROSEGOLD = "#D9A06B"
DIVIDER = "#5C3038"

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def gradient_background():
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_glow(img, cx, cy, radius, color, strength=50):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.6))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def center_text(draw, text, fnt, y, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((W / 2 - tw / 2, y), text, font=fnt, fill=fill)


def slide_fachbegriff(entry):
    img = gradient_background()
    add_glow(img, W * 0.5, H * 0.32, 560, (150, 90, 60), strength=38)
    draw = ImageDraw.Draw(img)

    eyebrow_font = font(B.SANS_BOLD, 18)
    center_text(draw, "@DASDEPOTDIARY  —  " + DATE_LABEL, eyebrow_font, 64, SUBTEXT)

    label_font = font(B.SANS_BOLD, 22)
    label = "FACHBEGRIFF DES TAGES"
    center_text(draw, label, label_font, 120, ROSEGOLD)

    # Grosses dekoratives Anfuehrungszeichen als Badge statt Randleiste
    badge_font = font(B.SERIF_BOLD, 130)
    center_text(draw, "„", badge_font, 190, ROSEGOLD)

    term_font = font(B.SERIF_BOLD, 68)
    def_font = font(B.SANS_BOLD, 28)
    ex_font = font(B.SERIF_BOLD_ITALIC, 23)
    content_w = W - 2 * 90

    term_lines = wrap_text(draw, entry["term"], term_font, content_w)
    def_lines = wrap_text(draw, entry["definition"], def_font, content_w)
    ex_lines = wrap_text(draw, entry.get("example", ""), ex_font, content_w) if entry.get("example") else []

    block_h = len(term_lines) * 78 + 34 + len(def_lines) * 40
    if ex_lines:
        block_h += 46 + len(ex_lines) * 32
    footer_top = H - 140
    by = 340 + max(0, (footer_top - 340 - block_h) // 2)

    for line in term_lines:
        center_text(draw, line, term_font, by, INK)
        by += 78
    by += 34
    for line in def_lines:
        center_text(draw, line, def_font, by, INK)
        by += 40
    if ex_lines:
        by += 20
        line_w = 70
        draw.line([(W / 2 - line_w / 2, by), (W / 2 + line_w / 2, by)], fill=ROSEGOLD, width=3)
        by += 26
        for line in ex_lines:
            center_text(draw, line, ex_font, by, SUBTEXT)
            by += 32

    text = "Keine Anlageberatung -- nur eine kurze Erklaerung."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(90, H - 90), (W - 90, H - 90)], fill=DIVIDER, width=1)
    center_text(draw, text, disclaimer_font, H - 68, SUBTEXT)

    return img


def main():
    entry = {
        "term": "PEG-Ratio",
        "definition": "Das KGV (Kurs-Gewinn-Verhaeltnis) geteilt durch das erwartete Gewinnwachstum. Setzt eine Bewertung damit ins Verhaeltnis zum Wachstum -- ein hohes KGV kann bei starkem Wachstum trotzdem 'guenstig' im Verhaeltnis aussehen.",
        "example": "Beispiel von heute: Meta hat ein KGV von 25,1 -- klingt erstmal viel. Die PEG-Ratio liegt aber nur bei 0,88, weil das erwartete Gewinnwachstum hoch eingepreist ist.",
    }
    img = slide_fachbegriff(entry)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
