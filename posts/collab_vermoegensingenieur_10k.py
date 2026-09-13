"""Collab mit @der_vermoegensingenieur: "10.000 Euro aufteilen" -- wie wuerden
wir beide ein hypothetisches 10.000-Euro-Depot strukturieren?

Bewusst UNTERSCHIEDLICHE Strukturen (Nutzerwunsch 2026-09-13, "ich wuerd's
nicht ganz gleich machen"): Partner setzt auf einen breiten Welt-ETF als
Basis (50%) + zwei Wachstumsaktien (30%) + Bitcoin (20%). Eigene Seite ist
bewusst stock-picker-lastiger (spiegelt den echten, Einzelaktien-lastigen
Depot-Stil, siehe echte August-Allokation): drei grosse Einzelaktien (60%)
+ eine spekulative Beimischung (10%) + Bitcoin (20%) -- kein ETF.

Rein qualitative, persoenliche Begruendungen pro Position -- keine
Kursziele, keine "kaufen"-Sprache, keine Performance-Versprechen.

Design: gleiche reduzierte Palette wie collab_finanzlehrer_sparplaene.py
(dunkelgrau + ein Rot) -- vom Nutzer explizit bestaetigt ("so stark passt
mir so").

Aufruf:
  python posts/collab_vermoegensingenieur_10k.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "collab_vermoegensingenieur_10k"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

BG = (30, 30, 32)
CARD_BORDER = (58, 56, 58)
RED = (214, 69, 65)
CREAM = (240, 238, 230)
MUTED = (168, 165, 168)

PARTNER_HANDLE = "@DER_VERMOEGENSINGENIEUR"
OWN_HANDLE = "@DASDEPOTDIARY"

DATA = json.loads((ROOT / "posts" / "inputs" / "collab_vermoegensingenieur_10k.json").read_text(encoding="utf-8"))
PARTNER_POS = DATA["partner_positions"]
OWN_POS = DATA["own_positions"]


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


def _scatter_particles(img, seed):
    import random
    rnd = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    color = (*RED, 55)
    for _ in range(12):
        x = rnd.randint(40, W - 40)
        y = rnd.randint(40, H - 40)
        r = rnd.randint(3, 7)
        if rnd.random() < 0.5:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        else:
            draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=color)


def base_slide(seed=1):
    img = Image.new("RGB", (W, H), BG)
    _scatter_particles(img, seed)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=RED)
    return img, draw


def build_header(draw, y=36):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {PARTNER_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=RED)
    y += 28
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 18


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- persoenliche Auswahl, kein Ratschlag."):
    disclaimer_font = font(B.SANS_BOLD, 17)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    divider_y = H - 36 - 24 * len(lines) - 10
    draw.line([(B.MARGIN_LEFT, divider_y), (W - B.MARGIN_RIGHT, divider_y)], fill=CARD_BORDER, width=1)
    dy = divider_y + 10
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 24
    page_font = font(B.SANS_BOLD, 17)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, divider_y + 10), page_text, font=page_font, fill=MUTED)


def draw_position_card(img, draw, top, bottom, pos, accent):
    logo_r = 42
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = top + logo_r + 6
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
                 fill=CREAM, outline=accent, width=2)
    if pos.get("logo"):
        logo = Image.open(ROOT / "assets" / pos["logo"]).convert("RGBA")
        target = int(logo_r * 1.5)
        ratio = min(target / logo.width, target / logo.height)
        logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
        img.paste(logo, (logo_cx - logo.width // 2, logo_cy - logo.height // 2), logo)
        draw = ImageDraw.Draw(img)
    else:
        etf_font = font(B.SANS_BOLD, 15)
        tw = draw.textlength("ETF", font=etf_font)
        draw.text((logo_cx - tw / 2, logo_cy - 9), "ETF", font=etf_font, fill=accent)

    text_x = logo_cx + logo_r + 22
    name_font = font(B.SANS_BOLD, 25)
    draw.text((text_x, top + 4), pos["name"], font=name_font, fill=CREAM)
    amt_font = font(B.SANS_BOLD, 18)
    draw.text((text_x, top + 34), pos["amount"], font=amt_font, fill=accent)

    why_font = font(B.SANS_BOLD, 17)
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    lines = wrap_text(draw, pos["why"], why_font, max_w)
    y = logo_cy + logo_r + 16
    for line in lines[:4]:
        draw.text((B.MARGIN_LEFT, y), line, font=why_font, fill=MUTED)
        y += 22
    return draw


def slide_intro():
    img, draw = base_slide(seed=1)
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 90), "COLLAB · GEDANKENEXPERIMENT", font=eyebrow_font, fill=RED)

    y = 128
    draw.text((B.MARGIN_LEFT, y), "10.000 Euro.", font=font(B.SANS_BOLD, 56), fill=CREAM)
    y += 66
    draw.text((B.MARGIN_LEFT, y), "Wie wuerden wir sie aufteilen?", font=font(B.SANS_BOLD, 30), fill=RED)
    y += 46
    sub_lines = wrap_text(draw, "Zwei komplett unterschiedliche Ansaetze -- ein Welt-ETF als Basis vs. gezielte Einzelaktien.",
                           font(B.SANS_BOLD, 19), W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in sub_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 19), fill=MUTED)
        y += 26

    y += 30
    draw.text((B.MARGIN_LEFT, y), f"{PARTNER_HANDLE}:", font=font(B.SANS_BOLD, 19), fill=RED)
    y += 28
    draw.text((B.MARGIN_LEFT, y), "50% ETF · 30% Wachstum · 20% Bitcoin", font=font(B.SANS_BOLD, 21), fill=CREAM)
    y += 44
    draw.text((B.MARGIN_LEFT, y), f"{OWN_HANDLE}:", font=font(B.SANS_BOLD, 19), fill=RED)
    y += 28
    draw.text((B.MARGIN_LEFT, y), "60% Einzelaktien · 20% Bitcoin · 10% Spekulativ", font=font(B.SANS_BOLD, 21), fill=CREAM)

    draw_footer(draw, 1, 8)
    return img


def slide_positions(seed, idx, n_total, label, handle, accent, positions):
    img, draw = base_slide(seed=seed)
    y = build_header(draw)

    badge_font = font(B.SANS_BOLD, 17)
    badge = f"{label} -- {handle}"
    draw.text((B.MARGIN_LEFT, y), badge, font=badge_font, fill=accent)
    y += 34

    footer_h = 70
    usable_bottom = H - footer_h - 10
    gap = 24
    card_h = (usable_bottom - y - gap) // 2

    for pos in positions:
        draw_position_card(img, draw, y, y + card_h, pos, accent)
        draw = ImageDraw.Draw(img)
        y += card_h + gap

    draw_footer(draw, idx, n_total)
    return img


def slide_overlap(idx, n_total):
    img, draw = base_slide(seed=99)
    y = build_header(draw)
    y += 40

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "ZUFALL?", font=eyebrow_font, fill=RED)
    y += 40

    title_lines = ["Beide haben unabhaengig", "voneinander auf ServiceNow", "gesetzt."]
    for line in title_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 38), fill=CREAM)
        y += 46

    y += 30
    body_lines = wrap_text(
        draw,
        "Ohne Absprache sind wir beide bei derselben Aktie gelandet -- ein Zeichen dafuer, dass die Story hinter dem Unternehmen bei mehreren unabhaengig ueberzeugt.",
        font(B.SANS_BOLD, 21), W - B.MARGIN_LEFT - B.MARGIN_RIGHT,
    )
    for line in body_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 21), fill=MUTED)
        y += 30

    draw_footer(draw, idx, n_total)
    return img


def slide_outro(idx, n_total):
    img, draw = base_slide(seed=7)
    y = build_header(draw)
    y += 30

    title_font = font(B.SANS_BOLD, 36)
    for line in ["Welchen Ansatz", "wuerdest du waehlen?"]:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 46

    y += 30
    body_font = font(B.SANS_BOLD, 21)
    lines = wrap_text(draw, "Schreib's uns in die Kommentare -- bei beiden Accounts.", body_font,
                       W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=RED)
        y += 28

    y += 40
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=RED, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Rein hypothetisch, keine Rangfolge --", font=font(B.SANS_BOLD, 20), fill=CREAM)
    y += 28
    draw.text((B.MARGIN_LEFT, y), "nur zwei persoenliche Denkweisen.", font=font(B.SANS_BOLD, 20), fill=CREAM)

    draw_footer(draw, idx, n_total)
    return img


def main():
    slides = [slide_intro]
    slides.append(lambda: slide_positions(2, 2, 8, "SEIN 10K", PARTNER_HANDLE, RED, PARTNER_POS[0:2]))
    slides.append(lambda: slide_positions(3, 3, 8, "SEIN 10K", PARTNER_HANDLE, RED, PARTNER_POS[2:4]))
    slides.append(lambda: slide_positions(4, 4, 8, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[0:2]))
    slides.append(lambda: slide_positions(5, 5, 8, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[2:4]))
    slides.append(lambda: slide_positions(6, 6, 8, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[4:6]))
    slides.append(lambda: slide_overlap(7, 8))
    slides.append(lambda: slide_outro(8, 8))

    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 4
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (20, 20, 20))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = ["10.000 Euro -- wie wuerden wir sie aufteilen? Zwei komplett unterschiedliche Ansaetze."]
    for pos in PARTNER_POS + OWN_POS:
        sentences.append(f"{pos['name']}, {pos['amount']}. {pos['why']}")
    sentences.append("Beide haben unabhaengig voneinander auf ServiceNow gesetzt.")
    sentences.append("Welchen Ansatz wuerdest du waehlen? Schreib's uns in die Kommentare.")
    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md")


if __name__ == "__main__":
    main()
