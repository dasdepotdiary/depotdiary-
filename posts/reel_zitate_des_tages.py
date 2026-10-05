"""Reel-Variante des neuen Story-Formats "Zitat des Tages" -- drei echte
Investoren-Zitate nacheinander, gleiches Waldgruen/Gold-Design. Nutzt die
Slide-Karten selbst als Video-Hintergrund (kein Pure-Footage noetig).

Aufruf:
  python posts/reel_zitate_des_tages.py
Danach:
  python scripts/generate_voiceover_elevenlabs.py reel_zitate_des_tages
  python video/assemble.py reel_zitate_des_tages --audio output/reel_zitate_des_tages/voiceover_elevenlabs.mp3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import story_zitat_des_tages as z
import voiceover

NAME = "reel_zitate_des_tages"
ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

QUOTES = [
    {
        "quote": "Preis ist, was du bezahlst. Wert ist, was du bekommst.",
        "author": "Warren Buffett",
        "context": "Eine der bekanntesten Unterscheidungen im Value-Investing.",
    },
    {
        "quote": "Zeit ist dein Freund, Impulsivitaet dein Feind.",
        "author": "John C. Bogle",
        "context": "Der Vanguard-Gruender ueber Geduld als wichtigste Anleger-Eigenschaft.",
    },
    {
        "quote": "Risiko entsteht, wenn man nicht weiss, was man tut.",
        "author": "Warren Buffett",
        "context": "Ein Plaedoyer dafuer, nur in Dinge zu investieren, die man wirklich versteht.",
    },
]


def _center_slide(lines, label):
    import style_finanzhafen as S
    from PIL import ImageDraw
    key = "reel-" + label + lines[0]
    accent = S.accent_for(key)
    img = S.story_background(S.photo_for(key))
    draw = ImageDraw.Draw(img)
    S.draw_top(draw, accent, label)
    f = S.font(96)
    y = 1440 - len(lines) * 108
    for line in lines:
        draw.text((80, y), line, font=f, fill=S.CREAM)
        y += 108
    S.draw_wordmark(img)
    return img


def main():
    intro = _center_slide(["3 ZITATE.", "ZUM NACHDENKEN."], "ZITAT DES TAGES")
    outro = _center_slide(["FOLGE FUER MEHR", "BOERSENWISSEN."], "ZITAT DES TAGES")

    slides = [intro]
    for q in QUOTES:
        card = z.slide_zitat(q)
        slides.append(card)
        slides.append(card)
    slides.append(outro)

    for i, img in enumerate(slides, start=1):
        img.save(TT_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = 4
    rows = (n + cols - 1) // cols
    gap = 16
    tw, th = 1080 // 3, 1920 // 3
    from PIL import Image
    sheet = Image.new("RGB", (tw * cols + gap * (cols + 1), th * rows + gap * (rows + 1)), (10, 18, 14))
    for i in range(1, n + 1):
        im = Image.open(TT_DIR / f"slide_{i}.png").resize((tw, th))
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = ["Drei Zitate bekannter Investoren zum Nachdenken -- keine Anlageberatung."]
    for q in QUOTES:
        sentences.append(f"{q['quote']} -- {q['author']}.")
        sentences.append(q["context"])
    sentences.append("Folge mir fuer mehr Boersenwissen und Zitate.")
    assert len(sentences) == n, f"{len(sentences)} Saetze vs {n} Slides"
    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md")


if __name__ == "__main__":
    main()
