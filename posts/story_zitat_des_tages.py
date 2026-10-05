"""Story-Format "Zitat des Tages" (2026-09-30, Nutzerwunsch: "ueberleg dir noch
ein weiteres Format fuer die Stories").

Echte, historische Zitate bekannter Investoren (Buffett, Bogle, Graham, Lynch)
mit deutscher Uebersetzung + korrekter Namensnennung + kurzer, rein
erklaerender Einordnung. KEINE eigene Bewertung/Empfehlung -- die Zitate sind
historische Aussagen Dritter. Evergreen, gut vorproduzierbar.

v2 (2026-10-05): vom einfaerbigen Waldgruen auf das depotdiary-Foto-Schema
umgestellt (posts/style_finanzhafen.py) -- passend zu den Finanzhafen-Posts.

Aufruf (Prototyp/Test):
  python posts/story_zitat_des_tages.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

NAME = "story_zitat_des_tages"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

DATE_LABEL = (sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%d.%m.%Y"))


def slide_zitat(entry):
    key = f"zitat-{DATE_LABEL}-{entry['author']}"
    accent = S.accent_for(key)
    img = S.story_background(S.photo_for(key))
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, "ZITAT DES TAGES", DATE_LABEL[:6])

    max_w = W - 160
    q_f, q_lines = S.fit_lines(draw, entry["quote"], max_w, 6, 68, 44)
    q_lh = int(q_f.size * 1.2)
    a_f = S.font(36)
    c_f = S.font(30)
    c_lines = S.wrap_text(draw, entry.get("context", ""), c_f, max_w) if entry.get("context") else []

    total = len(q_lines) * q_lh + 34 + 46
    if c_lines:
        total += 40 + 6 + 28 + len(c_lines) * 42
    y = 1440 - total

    draw.text((74, y - 190), "“", font=S.font(240, B.SERIF_BOLD), fill=accent)

    for line in q_lines:
        draw.text((80, y), line, font=q_f, fill=S.CREAM)
        y += q_lh
    y += 34
    draw.text((80, y), "— " + entry["author"].upper(), font=a_f, fill=accent)
    y += 46
    if c_lines:
        y += 40
        draw.rectangle([80, y, 80 + 90, y + 6], fill=accent)
        y += 6 + 28
        for line in c_lines:
            draw.text((80, y), line, font=c_f, fill=S.SOFT)
            y += 42

    draw.text((80, S.SAFE_BOTTOM - 62), "Historisches Zitat -- keine Anlageberatung, keine aktuelle Empfehlung.",
              font=S.font(20), fill=S.MUTED)
    S.draw_wordmark(img)
    return img


def main():
    entry = {
        "quote": "Preis ist, was du bezahlst. Wert ist, was du bekommst.",
        "author": "Warren Buffett",
        "context": "Eine der bekanntesten Unterscheidungen im Value-Investing -- Kurs und Unternehmenswert sind nicht automatisch dasselbe.",
    }
    img = slide_zitat(entry)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
