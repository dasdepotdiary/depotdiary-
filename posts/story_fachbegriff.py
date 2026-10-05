"""Taegliches (evergreen) Story-Format "FACHBEGRIFF DES TAGES" -- ein
Finanzbegriff kurz und einfach erklaert. Braucht keine tagesaktuellen Daten,
kann also auch an ruhigen Tagen laufen. Rein erklaerend, keine Bewertung.

v3 (2026-10-05, Nutzerwunsch "alle einfaerbigen Designs spannender, im Stil der
Finanzhafen-Feed-Posts"): komplett auf das depotdiary-Foto-Schema umgestellt
(posts/style_finanzhafen.py): Foto + dunkler Verlauf, fette Caps-Headline,
rotierende Akzentfarbe, Wortmarke als Anker, Story-Safe-Zones. Vorher: zentrierte
Bordeaux-Flashcard (v2).

Input: term, definition (1-2 Saetze), example (optional, 1 Satz).

Aufruf (Prototyp/Test):
  python posts/story_fachbegriff.py "TT.MM.JJJJ"
"""
import sys
from datetime import date
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

NAME = "story_fachbegriff"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def slide_fachbegriff(entry):
    key = "fachbegriff-" + DATE_LABEL
    accent = S.accent_for(key)
    img = S.story_background(S.photo_for(key))
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, "FACHBEGRIFF DES TAGES", DATE_LABEL[:6])

    max_w = W - 160
    term_f, term_lines = S.fit_lines(draw, entry["term"].upper(), max_w, 3, 104, 40)
    term_lh = int(term_f.size * 1.08)

    def_size = 38
    while True:
        def_f = S.font(def_size)
        def_lines = S.wrap_text(draw, entry["definition"], def_f, max_w)
        ex_f = S.font(32)
        ex_lines = S.wrap_text(draw, entry["example"], ex_f, max_w) if entry.get("example") else []
        total = len(term_lines) * term_lh + 34 + len(def_lines) * int(def_size * 1.36)
        if ex_lines:
            total += 34 + 6 + 30 + len(ex_lines) * 44
        if total <= 880 or def_size <= 30:
            break
        def_size -= 2

    y = 1440 - total
    for line in term_lines:
        draw.text((80, y), line, font=term_f, fill=S.CREAM)
        y += term_lh
    y += 34
    for line in def_lines:
        draw.text((80, y), line, font=def_f, fill=S.SOFT)
        y += int(def_size * 1.36)
    if ex_lines:
        y += 34
        draw.rectangle([80, y, 80 + 90, y + 6], fill=accent)
        y += 6 + 30
        for line in ex_lines:
            draw.text((80, y), line, font=ex_f, fill=accent)
            y += 44

    draw.text((80, S.SAFE_BOTTOM - 62), "Keine Anlageberatung -- nur eine kurze Erklaerung.",
              font=S.font(20), fill=S.MUTED)
    S.draw_wordmark(img)
    return img


def main():
    entry = {
        "term": "Market Cap-Klassen (Large/Mid/Small Cap)",
        "definition": "Unternehmen werden nach Marktkapitalisierung eingeteilt: Large Cap (grob ueber 10 Mrd. USD), Mid Cap (2-10 Mrd.) und Small Cap (unter 2 Mrd.).",
        "example": "Small Caps schwanken im Schnitt staerker als Large Caps -- in beide Richtungen.",
    }
    img = slide_fachbegriff(entry)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
