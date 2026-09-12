"""Guess the Stock #2 (2026-09-12): ASML.

Gleiche Struktur/Optik wie guess_the_stock_netflix.py (Format bewusst
konsistent gehalten, da es die etablierte Serie ist -- anders als bei
komplett neuen Formaten, wo Design-Experimente erwuenscht sind).

Fakten recherchiert (Tavily, mehrere Quellen): 100% Marktanteil bei EUV-
Lithographie, Maschinen kosten 200-400 Mio. USD pro Stueck, ~553 Mrd. USD
Marktkapitalisierung (Europas wertvollstes Tech-Unternehmen), niederlaendisch.

Aufruf:
  python posts/guess_the_stock_asml.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "guess_the_stock_asml"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (24, 20, 30)
BG_BOTTOM = (10, 9, 12)
CARD = "#221D2C"
CARD_BORDER = "#443A5A"
CREAM = "#F2F0EA"
MUTED = "#A79FC0"
ACCENT = "#E63946"

OWN_HANDLE = "@DASDEPOTDIARY"

CLUES = [
    "Ein einziges Unternehmen hat ein 100%-Monopol auf eine Technologie, die JEDER moderne Hochleistungs-Chip braucht.",
    "Eine einzelne Maschine von ihm kostet zwischen 200 und 400 Millionen US-Dollar.",
    "Kein Konkurrent kann bei Praezision und Genauigkeit mithalten -- die noetige Forschung ist schlicht zu teuer.",
    "Das Unternehmen kommt aus den Niederlanden -- und ist Europas wertvollstes Technologieunternehmen.",
]

REVEAL_NAME = "ASML"
REVEAL_TICKER = "ASML"
REVEAL_LOGO = "asml_logo_icon.png"


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


def add_radial_glow(img, cx, cy, radius, color, strength=90):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.55))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def base_slide(glow_cxy=None):
    img = gradient_background(BG_TOP, BG_BOTTOM)
    add_radial_glow(img, *(glow_cxy or (W // 2, H * 0.25)), 520, (110, 40, 55), strength=70)
    draw = ImageDraw.Draw(img)
    return img, draw


def build_header(draw, y=60):
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, y), OWN_HANDLE, font=handle_font, fill=MUTED)
    return y + 50


def draw_progress_dots(draw, cy, active_idx, total):
    r = 9
    gap = 30
    total_w = (total - 1) * gap
    start_x = W / 2 - total_w / 2
    for i in range(total):
        cx = start_x + i * gap
        if i <= active_idx:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
        else:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=MUTED, width=2)


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    y = H * 0.30
    title_font = font(B.SANS_BOLD, 74)
    for line in ["GUESS THE", "STOCK #2"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 86

    y += 30
    sub_font = font(B.SANS_BOLD, 34)
    sub_lines = wrap_text(draw, "4 echte Hinweise. 1 Unternehmen.", sub_font, W - 140)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=ACCENT)
        y += 44

    y += 10
    sub2_font = font(B.SANS_BOLD, 30)
    tw = draw.textlength("Schaffst du's?", font=sub2_font)
    draw.text((W / 2 - tw / 2, y), "Schaffst du's?", font=sub2_font, fill=CREAM)

    note_font = font(B.SANS_BOLD, 22)
    note = "Keine Anlageberatung -- nur ein Ratespiel mit echten Fakten."
    note_lines = wrap_text(draw, note, note_font, W - 160)
    ny = H - 140
    for line in note_lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, ny), line, font=note_font, fill=MUTED)
        ny += 28

    return img


def slide_clue(idx, text):
    img, draw = base_slide()
    y = build_header(draw)

    draw_progress_dots(draw, y + 20, idx, len(CLUES))
    y += 70

    label_font = font(B.SANS_BOLD, 26)
    label = f"HINWEIS {idx + 1} / {len(CLUES)}"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=ACCENT)
    y += 70

    card_top = y
    card_bottom = H * 0.72
    draw.rounded_rectangle([70, card_top, W - 70, card_bottom], radius=24, fill=CARD, outline=CARD_BORDER, width=2)

    clue_font = font(B.SANS_BOLD, 38)
    lines = wrap_text(draw, text, clue_font, W - 200)
    line_h = 50
    total_h = len(lines) * line_h
    ty = (card_top + card_bottom) / 2 - total_h / 2
    for line in lines:
        tw = draw.textlength(line, font=clue_font)
        draw.text((W / 2 - tw / 2, ty), line, font=clue_font, fill=CREAM)
        ty += line_h

    note_font = font(B.SANS_BOLD, 22)
    note = "Keine Anlageberatung -- nur ein Ratespiel mit echten Fakten."
    ny = H - 100
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, ny), note, font=note_font, fill=MUTED)

    return img


def slide_reveal():
    img, draw = base_slide(glow_cxy=(W // 2, H * 0.35))

    y = build_header(draw)
    y += 20

    label_font = font(B.SANS_BOLD, 26)
    label = "AUFLOESUNG"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=ACCENT)
    y += 60

    logo_r = 100
    logo_cx = W // 2
    logo_cy = y + logo_r
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
                 fill=CREAM, outline=ACCENT, width=4)
    logo = Image.open(ROOT / "assets" / REVEAL_LOGO).convert("RGBA")
    target = int(logo_r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (logo_cx - logo.width // 2, logo_cy - logo.height // 2), logo)
    draw = ImageDraw.Draw(img)

    y = logo_cy + logo_r + 50
    name_font = font(B.SANS_BOLD, 58)
    tw = draw.textlength(REVEAL_NAME, font=name_font)
    draw.text((W / 2 - tw / 2, y), REVEAL_NAME, font=name_font, fill=CREAM)
    y += 68

    ticker_font = font(B.SANS_BOLD, 30)
    tw = draw.textlength(REVEAL_TICKER, font=ticker_font)
    draw.text((W / 2 - tw / 2, y), REVEAL_TICKER, font=ticker_font, fill=ACCENT)
    y += 70

    cta_font = font(B.SANS_BOLD, 30)
    cta_lines = ["Wie viele Hinweise", "hast du gebraucht?"]
    for line in cta_lines:
        tw = draw.textlength(line, font=cta_font)
        draw.text((W / 2 - tw / 2, y), line, font=cta_font, fill=MUTED)
        y += 40

    note_font = font(B.SANS_BOLD, 22)
    note = "Keine Anlageberatung -- nur ein Ratespiel mit echten Fakten."
    ny = H - 100
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, ny), note, font=note_font, fill=MUTED)

    return img


def main():
    slides = [slide_intro]
    for i, clue in enumerate(CLUES):
        slides.append(lambda i=i, c=clue: slide_clue(i, c))
    slides.append(slide_reveal)

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
    sheet = Image.new("RGB", (tw * cols + gap * (cols + 1), th * rows + gap * (rows + 1)), (20, 18, 24))
    for i in range(1, n + 1):
        im = Image.open(TT_DIR / f"slide_{i}.png").resize((tw, th))
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = [
        "Guess the Stock, Runde zwei. Vier echte Hinweise, du versuchst, das Unternehmen zu erraten. Pausier zwischendurch, wenn du raten willst.",
        "Hinweis eins: Ein einziges Unternehmen hat ein hundert Prozent Monopol auf eine Technologie, die jeder moderne Hochleistungs-Chip braucht.",
        "Hinweis zwei: Eine einzelne Maschine von ihm kostet zwischen 200 und 400 Millionen US-Dollar.",
        "Hinweis drei: Kein Konkurrent kann bei Praezision mithalten -- die noetige Forschung ist schlicht zu teuer.",
        "Hinweis vier: Das Unternehmen kommt aus den Niederlanden -- und ist Europas wertvollstes Technologieunternehmen.",
        f"Die Aufloesung: {REVEAL_NAME}. Wie viele Hinweise hast du gebraucht? Schreib's in die Kommentare und folge fuer mehr Ratespiele.",
    ]
    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md + timing.json")


if __name__ == "__main__":
    main()
