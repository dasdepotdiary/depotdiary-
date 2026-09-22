"""Taegliches Morgen-Story-Format "WAS STEHT HEUTE AN" -- Gegenstueck zu
story_tagesereignisse.py (das ist der Abend-Rueckblick, das hier ist der
Morgen-Ausblick): recherchierte Termine/Ereignisse, die HEUTE anstehen
(Zentralbank-Termine, bekannte Earnings, ggf. eigene Posts des Tages als
Cross-Promo). Rein faktisch, keine Prognosen/Kursziele.

Eigene visuelle Identitaet: Morgendaemmerungs-Verlauf (warmes Orange oben,
tiefes Navy unten) statt der bisherigen Paletten (Schwarz/Creme/Bordeaux/Gruen).

Input: Liste von Dicts mit time (str, z.B. "HEUTE" oder "09:00"), headline,
body (1 Satz).

Aufruf (Prototyp/Test):
  python posts/story_heute_agenda.py
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font

NAME = "story_heute_agenda"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
DAWN_TOP = (232, 148, 82)
DAWN_MID = (94, 74, 110)
DAWN_BOTTOM = (18, 20, 42)
INK = "#FBF3EA"
SUBTEXT = "#C9C3D8"
GOLD = "#F2B872"
CARD = "#22203A"
CARD_BORDER = "#3A3660"
DIVIDER = "#3A3660"

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
        if t < 0.35:
            tt = t / 0.35
            r = int(DAWN_TOP[0] + (DAWN_MID[0] - DAWN_TOP[0]) * tt)
            g = int(DAWN_TOP[1] + (DAWN_MID[1] - DAWN_TOP[1]) * tt)
            b = int(DAWN_TOP[2] + (DAWN_MID[2] - DAWN_TOP[2]) * tt)
        else:
            tt = (t - 0.35) / 0.65
            r = int(DAWN_MID[0] + (DAWN_BOTTOM[0] - DAWN_MID[0]) * tt)
            g = int(DAWN_MID[1] + (DAWN_BOTTOM[1] - DAWN_MID[1]) * tt)
            b = int(DAWN_MID[2] + (DAWN_BOTTOM[2] - DAWN_MID[2]) * tt)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_sun_glow(img):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([W / 2 - 260, -180, W / 2 + 260, 180], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    color_layer = Image.new("RGB", (W, H), (255, 210, 150))
    img.paste(color_layer, (0, 0), glow)


def draw_header(draw, y):
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + DATE_LABEL, font=eyebrow_font, fill=SUBTEXT)
    y += 40
    title_font = font(B.SANS_BOLD, 46)
    draw.text((B.MARGIN_LEFT, y), "Was steht heute an.", font=title_font, fill=INK)
    y += 62
    draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=GOLD)
    return y + 46


def draw_agenda_item(draw, x, y, w, item):
    time_font = font(B.SANS_BOLD, 20)
    headline_font = font(B.SANS_BOLD, 25)
    body_font = font(B.SANS_BOLD, 19)

    draw.ellipse([x, y + 6, x + 12, y + 18], fill=GOLD)
    draw.text((x + 26, y), item["time"], font=time_font, fill=GOLD)

    ty = y + 32
    headline_lines = wrap_text(draw, item["headline"], headline_font, w - 26)
    for line in headline_lines:
        draw.text((x + 26, ty), line, font=headline_font, fill=INK)
        ty += 32
    body_lines = wrap_text(draw, item["body"], body_font, w - 26)
    for line in body_lines:
        draw.text((x + 26, ty), line, font=body_font, fill=SUBTEXT)
        ty += 26

    return ty - y + 20


def slide_agenda(items):
    img = gradient_background()
    add_sun_glow(img)
    draw = ImageDraw.Draw(img)

    header_end_y = draw_header(draw, 70)
    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT

    tmp = Image.new("RGB", (10, 10))
    tmp_draw = ImageDraw.Draw(tmp)
    heights = [draw_agenda_item(tmp_draw, 0, 0, content_w, it) for it in items]
    # zweiter Pass ohne Zeichnen ist nicht noetig, draw_agenda_item zeichnet
    # direkt -- daher hier Hoehe separat schaetzen via Dry-Run auf Dummy-Bild
    block_h = sum(heights)
    footer_top = H - 140
    y = header_end_y + max(20, (footer_top - header_end_y - block_h) // 2)

    line_x = B.MARGIN_LEFT + 5
    line_top = y + 12
    line_bottom = y + block_h - 20
    draw.line([(line_x, line_top), (line_x, line_bottom)], fill=CARD_BORDER, width=2)
    for item in items:
        h = draw_agenda_item(draw, B.MARGIN_LEFT, y, content_w, item)
        y += h

    text = "Keine Anlageberatung -- nur Termine, die ich mir angeschaut habe."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=DIVIDER, width=1)
    draw.text((B.MARGIN_LEFT, H - 68), text, font=disclaimer_font, fill=SUBTEXT)

    return img


def main():
    items = [
        {"time": "VORBOERSLICH", "headline": "AutoZone (AZO) veroeffentlicht Quartalszahlen.",
         "body": "Bericht vor US-Boersenoeffnung -- einer der wenigen bekannten Namen im heutigen Kalender."},
        {"time": "13:00", "headline": "EZB-Praesidentin Lagarde haelt eine Rede.",
         "body": "Ausserdem sprechen heute gleich mehrere Fed-Vertreter (Williams, Jefferson, Barkin)."},
        {"time": "NACHBOERSLICH", "headline": "KB Home (KBH) legt Zahlen nach Handelsschluss vor.",
         "body": "Der US-Hausbauer berichtet fuer das abgelaufene Quartal nach US-Boersenschluss."},
        {"time": "RUHIG", "headline": "Keine grossen Konjunkturdaten heute.",
         "body": "Der Tag wird eher von Notenbank-Reden geprägt als von harten Zahlen."},
    ]
    img = slide_agenda(items)
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
