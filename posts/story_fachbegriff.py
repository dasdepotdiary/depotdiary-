"""Taegliches (evergreen) Story-Format "FACHBEGRIFF DES TAGES" -- ein
Finanzbegriff kurz und einfach erklaert. Braucht keine tagesaktuellen Daten,
kann also auch an ruhigen Tagen laufen. Rein erklaerend, keine Bewertung.

Input: term, definition (1-2 Saetze), example (optional, 1 Satz).

Aufruf (Prototyp/Test):
  python posts/story_fachbegriff.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font

NAME = "story_fachbegriff"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
BG = B.GREEN
INK = "#F2F0EA"
SUBTEXT = "#C7D8CE"
OCHRE = B.OCHRE
DIVIDER = "#3A6350"

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


def slide_fachbegriff(entry):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=OCHRE)

    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    y = 70
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + DATE_LABEL, font=eyebrow_font, fill=SUBTEXT)
    y += 44
    label_font = font(B.SANS_BOLD, 22)
    draw.text((B.MARGIN_LEFT, y), "FACHBEGRIFF DES TAGES", font=label_font, fill=OCHRE)
    y += 56
    draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=OCHRE)
    y += 70

    # Vertikal zentrierter Block: Begriff (gross, serif) + Definition + Beispiel
    term_font = font(B.SERIF_BOLD, 72)
    def_font = font(B.SANS_BOLD, 30)
    ex_font = font(B.SERIF_BOLD_ITALIC, 24)

    term_lines = wrap_text(draw, entry["term"], term_font, content_w)
    def_lines = wrap_text(draw, entry["definition"], def_font, content_w)
    ex_lines = wrap_text(draw, entry.get("example", ""), ex_font, content_w) if entry.get("example") else []

    block_h = len(term_lines) * 82 + 36 + len(def_lines) * 42
    if ex_lines:
        block_h += 40 + len(ex_lines) * 32
    footer_top = H - 140
    by = y + max(20, (footer_top - y - block_h) // 2)

    for line in term_lines:
        draw.text((B.MARGIN_LEFT, by), line, font=term_font, fill=INK)
        by += 82
    by += 36
    for line in def_lines:
        draw.text((B.MARGIN_LEFT, by), line, font=def_font, fill=INK)
        by += 42
    if ex_lines:
        by += 40
        draw.line([(B.MARGIN_LEFT, by), (B.MARGIN_LEFT + 60, by)], fill=OCHRE, width=3)
        by += 20
        for line in ex_lines:
            draw.text((B.MARGIN_LEFT, by), line, font=ex_font, fill=SUBTEXT)
            by += 32

    text = "Keine Anlageberatung -- nur eine kurze Erklaerung."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=DIVIDER, width=1)
    draw.text((B.MARGIN_LEFT, H - 68), text, font=disclaimer_font, fill=SUBTEXT)

    return img


def main():
    entry = {
        "term": "Basispunkt",
        "definition": "Ein Basispunkt ist ein Hundertstel Prozent (0,01%). Wenn die Fed den Leitzins um 25 Basispunkte anhebt, heisst das: um 0,25 Prozentpunkte.",
        "example": "Beispiel von heute: Die Fed hat den Leitzins um 25 Basispunkte auf 3,75-4,00% angehoben.",
    }
    img = slide_fachbegriff(entry)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
