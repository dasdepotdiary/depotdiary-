"""Neues Format "Aktienquiz" -- Nutzerwunsch 2026-09-09 (siehe
[[project_depotdiary_engagement_brainstorm]]: Quiz-Idee war seit 2026-09-06
angekuendigt, aber bewusst zurueckgehalten bis der Nutzer es aktiv anstoesst
-- ist jetzt der Fall). Multiple-Choice-Wissensfragen zu Marktmechanik/
Kennzahlen (KGV, Quartalszahlen-Rhythmus, Aktiensplit, VIX, Diversifikation)
-- bewusst KEINE Fragen zu "welche Aktie steigt als naechstes" o.ae., damit
das Format BaFin/MAR-konform bleibt (reines Wissensquiz, keine Prognose).

Visuelle Sprache bewusst neu (Kahoot-artige farbige Antwort-Kacheln,
dunkles Indigo statt der bisherigen Gold/Rot/Schwarz-Paletten der anderen
Formate) -- Design-Experimentier-Regel, siehe [[feedback_depotdiary_design_experimentation]].

Aufruf:
  python posts/format_aktienquiz.py
Danach Audio + Video wie ueblich:
  python scripts/generate_voiceover_elevenlabs.py format_aktienquiz
  python video/assemble.py format_aktienquiz --audio output/format_aktienquiz/voiceover_elevenlabs.mp3 --pexels-clips output/format_aktienquiz/pexels_1.mp4,output/format_aktienquiz/pexels_2.mp4
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "format_aktienquiz"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (18, 14, 46)
BG_BOTTOM = (8, 6, 20)
CREAM = "#F2F0EA"
MUTED = "#9B93C9"
BLUE = "#3E63DD"
PINK = "#E4407A"
AMBER = "#F5A623"
GREEN = "#22C55E"
GRAY = "#4A4560"

OWN_HANDLE = "@DASDEPOTDIARY"

QUESTIONS = [
    {
        "q": "Was bedeutet das KGV (Kurs-Gewinn-Verhaeltnis)?",
        "options": [
            "Wie teuer eine Aktie im Verhaeltnis zum Gewinn ist",
            "Wie viel Dividende gezahlt wird",
            "Wie stark eine Aktie schwankt",
        ],
        "correct": 0,
        "explain": "Das KGV setzt den Aktienkurs ins Verhaeltnis zum Gewinn je Aktie -- eine von vielen Kennzahlen zur Einordnung, kein Kaufsignal fuer sich allein.",
    },
    {
        "q": "Wie oft veroeffentlichen die meisten US-Unternehmen ihre Quartalszahlen?",
        "options": [
            "Einmal im Jahr",
            "Alle drei Monate",
            "Alle sechs Monate",
        ],
        "correct": 1,
        "explain": "Vier Berichte pro Jahr -- daher auch 'Earnings Season' viermal im Jahr, wenn viele Unternehmen kurz hintereinander berichten.",
    },
    {
        "q": "Was passiert bei einem Aktiensplit?",
        "options": [
            "Die Aktie wird in mehr, guenstigere Stuecke aufgeteilt",
            "Das Unternehmen verkauft die Haelfte des Geschaefts",
            "Der Aktienkurs faellt dauerhaft",
        ],
        "correct": 0,
        "explain": "Die Marktkapitalisierung bleibt gleich -- es gibt nur mehr Aktien zu einem niedrigeren Stueckpreis, am Unternehmenswert selbst aendert sich nichts.",
    },
]


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


def gradient_background(top_rgb, bottom_rgb, w=W, h=H):
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((w, h))


def add_radial_glow(img, cx, cy, radius, color, strength=70):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def base_slide():
    img = gradient_background(BG_TOP, BG_BOTTOM)
    add_radial_glow(img, W // 2, H * 0.2, 480, (60, 40, 120), strength=60)
    return img, ImageDraw.Draw(img)


def build_header(draw, y=60):
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, y), OWN_HANDLE, font=handle_font, fill=MUTED)
    return y + 50


def footer_disclaimer(draw):
    note_font = font(B.SANS_BOLD, 20)
    note = "Wissensquiz -- keine Anlageberatung, keine Prognose."
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, H - 60), note, font=note_font, fill=MUTED)


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    y = H * 0.30
    label_font = font(B.SANS_BOLD, 28)
    label = "AKTIENQUIZ"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=AMBER)
    y += 64

    title_font = font(B.SANS_BOLD, 60)
    for line in ["3 FRAGEN.", "SCHAFFST DU ALLE?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 72

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    sub_lines = wrap_text(draw, "Boersenwissen statt Kursziele -- reines Ratespiel.", sub_font, W - 160)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 40

    footer_disclaimer(draw)
    return img


OPTION_COLORS = [BLUE, PINK, AMBER]
OPTION_LETTERS = ["A", "B", "C"]


def slide_question(idx, item):
    img, draw = base_slide()
    y = build_header(draw)
    y += 60

    badge_font = font(B.SANS_BOLD, 26)
    badge = f"FRAGE {idx + 1} / {len(QUESTIONS)}"
    tw = draw.textlength(badge, font=badge_font)
    draw.text((W / 2 - tw / 2, y), badge, font=badge_font, fill=AMBER)
    y += 80

    q_font = font(B.SANS_BOLD, 46)
    q_lines = wrap_text(draw, item["q"], q_font, W - 160)
    for line in q_lines:
        tw = draw.textlength(line, font=q_font)
        draw.text((W / 2 - tw / 2, y), line, font=q_font, fill=CREAM)
        y += 60
    y += 90

    opt_font = font(B.SANS_BOLD, 32)
    tile_h = 190
    gap = 36
    for i, opt in enumerate(item["options"]):
        color = OPTION_COLORS[i]
        draw.rounded_rectangle([80, y, W - 80, y + tile_h], radius=22, fill=color)
        letter_font = font(B.SANS_BOLD, 44)
        draw.text((115, y + tile_h / 2 - 26), OPTION_LETTERS[i], font=letter_font, fill=CREAM)
        lines = wrap_text(draw, opt, opt_font, W - 280)
        line_h = 38
        ty = y + tile_h / 2 - (len(lines) * line_h) / 2
        for line in lines:
            draw.text((185, ty), line, font=opt_font, fill=CREAM)
            ty += line_h
        y += tile_h + gap

    footer_disclaimer(draw)
    return img


def draw_check(draw, cx, cy, size, color):
    # LiberationSans-Bold hat kein Unicode-Haekchen-Glyph (rendert als Tofu-Box)
    # -- deshalb per Linienzug gezeichnet statt als Text.
    pts = [(cx - size, cy), (cx - size * 0.3, cy + size * 0.7), (cx + size, cy - size * 0.8)]
    draw.line(pts, fill=color, width=max(4, size // 5), joint="curve")


def draw_cross(draw, cx, cy, size, color):
    w = max(4, size // 5)
    draw.line([(cx - size, cy - size), (cx + size, cy + size)], fill=color, width=w)
    draw.line([(cx - size, cy + size), (cx + size, cy - size)], fill=color, width=w)


def slide_answer(idx, item):
    img, draw = base_slide()
    y = build_header(draw)
    y += 40

    badge_font = font(B.SANS_BOLD, 26)
    badge = "AUFLOESUNG"
    tw = draw.textlength(badge, font=badge_font)
    draw.text((W / 2 - tw / 2, y), badge, font=badge_font, fill=GREEN)
    y += 70

    q_font = font(B.SANS_BOLD, 36)
    q_lines = wrap_text(draw, item["q"], q_font, W - 160)
    for line in q_lines:
        tw = draw.textlength(line, font=q_font)
        draw.text((W / 2 - tw / 2, y), line, font=q_font, fill=MUTED)
        y += 46
    y += 60

    opt_font = font(B.SANS_BOLD, 32)
    tile_h = 160
    gap = 30
    for i, opt in enumerate(item["options"]):
        is_correct = i == item["correct"]
        color = GREEN if is_correct else GRAY
        draw.rounded_rectangle([80, y, W - 80, y + tile_h], radius=24, fill=color)
        mark_color = CREAM
        mark_cy = y + tile_h / 2
        if is_correct:
            draw_check(draw, 128, mark_cy, 22, mark_color)
        else:
            draw_cross(draw, 128, mark_cy, 18, mark_color)
        lines = wrap_text(draw, opt, opt_font, W - 300)
        line_h = 40
        ty = y + tile_h / 2 - (len(lines) * line_h) / 2
        text_color = CREAM if is_correct else "#C8C2E0"
        for line in lines:
            draw.text((190, ty), line, font=opt_font, fill=text_color)
            ty += line_h
        y += tile_h + gap

    y += 40

    y += 20
    explain_font = font(B.SANS_BOLD, 28)
    explain_lines = wrap_text(draw, item["explain"], explain_font, W - 180)
    for line in explain_lines:
        tw = draw.textlength(line, font=explain_font)
        draw.text((W / 2 - tw / 2, y), line, font=explain_font, fill=CREAM)
        y += 38

    footer_disclaimer(draw)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)
    y += 100

    title_font = font(B.SANS_BOLD, 52)
    for line in ["WIE VIELE RICHTIG?", "SCHREIB'S UNTEN REIN."]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 62

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    sub = "Und folge fuer mehr Quiz-Runden."
    tw = draw.textlength(sub, font=sub_font)
    draw.text((W / 2 - tw / 2, y), sub, font=sub_font, fill=AMBER)

    footer_disclaimer(draw)
    return img


def main():
    slides = [slide_intro]
    for i, item in enumerate(QUESTIONS):
        slides.append(lambda i=i, item=item: slide_question(i, item))
        slides.append(lambda i=i, item=item: slide_answer(i, item))
    slides.append(slide_outro)

    for i, fn in enumerate(slides, start=1):
        img = fn()
        img.save(TT_DIR / f"slide_{i}.png")
        feed_w, feed_h = B.FEED_SIZE
        crop_h = int(feed_w * H / W)
        top = max(0, (H - crop_h) // 3)
        cropped = img.crop((0, top, W, min(H, top + crop_h))).resize((feed_w, feed_h))
        cropped.save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = 4
    rows = (n + cols - 1) // cols
    gap = 16
    tw, th = W // 3, H // 3
    sheet = Image.new("RGB", (tw * cols + gap * (cols + 1), th * rows + gap * (rows + 1)), (14, 12, 30))
    for i in range(1, n + 1):
        im = Image.open(TT_DIR / f"slide_{i}.png").resize((tw, th))
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    # Optionen werden NICHT vorgelesen (stehen gut lesbar auf der Karte) --
    # nur Frage + kurze Denkpause-Ansage, dann Aufloesung. Haelt die Laenge
    # im 35-45s-Zielkorridor statt bei ueber 60s wie in der ersten Fassung.
    sentences = ["Aktienquiz: drei Fragen, schaffst du alle? Boersenwissen statt Kursziele."]
    for item in QUESTIONS:
        sentences.append(f"{item['q']} Pausier kurz und ueberleg.")
        correct_letter = OPTION_LETTERS[item["correct"]]
        sentences.append(f"Richtig ist {correct_letter}. {item['explain']}")
    sentences.append("Wie viele hattest du richtig? Schreib's in die Kommentare und folge fuer mehr Quiz-Runden.")

    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md + timing.json")


if __name__ == "__main__":
    main()
