"""Collab mit @der_vermoegensingenieur: "10.000 Euro aufteilen" -- wie wuerden
wir beide ein hypothetisches 10.000-Euro-Depot strukturieren?

Design-Update 2026-09-13 (zweite Runde, Nutzerfeedback "Design gefaellt mir
nicht, an ihn anpassen, fifty-fifty auch an mich"): sein Account
(@der_vermoegensingenieur) nutzt dunkle, echte Foto-Hintergruende (naechtliche
Skyline, Rauch/Chart-Texturen), fette weisse Grossbuchstaben-Headlines und
Teal/Cyan als Akzentfarbe mit Pinselstrich-Unterstreichung. Umgesetzt als
Fifty-Fifty-Blend: seine dunkle Foto-Optik + Teal fuer seine Seite, Rot
(depotdiarys etablierte Collab-Farbe) fuer die eigene Seite.

Alle "Warum"-Texte fuer die Partner-Seite sind WORTWOERTLICH aus seinen
eigenen Nachrichten uebernommen (Nutzerwunsch), nicht paraphrasiert.

Aufruf:
  python posts/collab_vermoegensingenieur_10k.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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

CARD_BORDER = (60, 62, 64)
TEAL = (46, 214, 199)
RED = (214, 69, 65)
CREAM = (245, 245, 242)
MUTED = (185, 185, 182)

PARTNER_HANDLE = "@DER_VERMOEGENSINGENIEUR"
OWN_HANDLE = "@DASDEPOTDIARY"

DATA = json.loads((ROOT / "posts" / "inputs" / "collab_vermoegensingenieur_10k.json").read_text(encoding="utf-8"))
PARTNER_POS = DATA["partner_positions"]
OWN_POS = DATA["own_positions"]
PARTNER_CLOSING = DATA.get("partner_closing", "")

_SKYLINE_SRC = Image.open(ROOT / "assets" / "skyline_still_1.png").convert("RGB")


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


def photo_background(seed=1):
    """Dunkle, echte Foto-Textur (naechtliche Skyline) stark abgedunkelt --
    Anlehnung an @der_vermoegensingenieurs Stil, aber eigenstaendig zugeschnitten
    statt kopiert."""
    src = _SKYLINE_SRC
    sw, sh = src.size
    scale = max(W / sw, H / sh)
    resized = src.resize((int(sw * scale), int(sh * scale)))
    x_off = int((resized.width - W) * (0.3 + 0.1 * (seed % 3)))
    y_off = int((resized.height - H) * 0.2)
    cropped = resized.crop((x_off, y_off, x_off + W, y_off + H))
    darkened = ImageEnhance.Brightness(cropped).enhance(0.42)
    darkened = ImageEnhance.Contrast(darkened).enhance(1.15)
    # leichte dunkle Vignette oben/unten fuer Textkontrast
    img = darkened.convert("RGB")
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, W, 260], fill=180)
    vdraw.rectangle([0, H - 220, W, H], fill=180)
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    black = Image.new("RGB", (W, H), (5, 6, 8))
    img.paste(black, (0, 0), vignette)
    return img


def brush_underline(draw, x, y, w, color, thickness=7):
    draw.line([(x, y), (x + w, y)], fill=color, width=thickness)


def base_slide(seed=1):
    img = photo_background(seed)
    draw = ImageDraw.Draw(img)
    return img, draw


def build_header(draw, y=36):
    handle_font = font(B.SANS_BOLD, 20)
    text = f"{OWN_HANDLE}  x  {PARTNER_HANDLE}"
    tw = draw.textlength(text, font=handle_font)
    draw.text((W / 2 - tw / 2, y), text, font=handle_font, fill=CREAM)
    y += 30
    return y + 12


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- persoenliche Auswahl, kein Ratschlag."):
    disclaimer_font = font(B.SANS_BOLD, 18)
    lines = wrap_text(draw, text, disclaimer_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 100)
    dy = H - 36 - 24 * len(lines)
    for line in lines:
        draw.text((B.MARGIN_LEFT, dy), line, font=disclaimer_font, fill=MUTED)
        dy += 24
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 36 - 24 * len(lines)), page_text, font=page_font, fill=MUTED)


def draw_position_card(img, draw, top, pos, accent):
    logo_r = 52
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = top + logo_r + 4
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
                 fill=CREAM, outline=accent, width=4)
    if pos.get("logo"):
        logo = Image.open(ROOT / "assets" / pos["logo"]).convert("RGBA")
        target = int(logo_r * 1.5)
        ratio = min(target / logo.width, target / logo.height)
        logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
        img.paste(logo, (logo_cx - logo.width // 2, logo_cy - logo.height // 2), logo)
        draw = ImageDraw.Draw(img)
    else:
        etf_font = font(B.SANS_BOLD, 18)
        tw = draw.textlength("ETF", font=etf_font)
        draw.text((logo_cx - tw / 2, logo_cy - 10), "ETF", font=etf_font, fill=accent)

    text_x = logo_cx + logo_r + 24
    name_font = font(B.SANS_BOLD, 34)
    draw.text((text_x, top + 4), pos["name"].upper(), font=name_font, fill=CREAM)
    amt_font = font(B.SANS_BOLD, 25)
    draw.text((text_x, top + 44), pos["amount"], font=amt_font, fill=accent)
    brush_underline(draw, text_x, top + 78, 70, accent, thickness=6)

    why_font = font(B.SANS_BOLD, 21)
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    lines = wrap_text(draw, pos["why"], why_font, max_w)
    y = logo_cy + logo_r + 26
    for line in lines[:5]:
        draw.text((B.MARGIN_LEFT, y), line, font=why_font, fill=MUTED)
        y += 27
    return y


def slide_intro():
    img, draw = base_slide(seed=1)
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, 100), "COLLAB · GEDANKENEXPERIMENT", font=eyebrow_font, fill=TEAL)

    y = 142
    draw.text((B.MARGIN_LEFT, y), "10.000 EURO.", font=font(B.SANS_BOLD, 72), fill=CREAM)
    y += 82
    draw.text((B.MARGIN_LEFT, y), "WIE WUERDEN WIR SIE", font=font(B.SANS_BOLD, 42), fill=CREAM)
    y += 50
    draw.text((B.MARGIN_LEFT, y), "AUFTEILEN?", font=font(B.SANS_BOLD, 42), fill=CREAM)
    y += 54
    brush_underline(draw, B.MARGIN_LEFT, y, 160, TEAL, thickness=9)
    y += 48
    sub_lines = wrap_text(draw, "Zwei komplett unterschiedliche Ansaetze -- ein Welt-ETF als Basis vs. gezielte Einzelaktien.",
                           font(B.SANS_BOLD, 24), W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in sub_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 24), fill=MUTED)
        y += 32

    y += 50
    draw.text((B.MARGIN_LEFT, y), PARTNER_HANDLE, font=font(B.SANS_BOLD, 22), fill=TEAL)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "50% ETF · 30% Wachstum · 20% Bitcoin", font=font(B.SANS_BOLD, 26), fill=CREAM)
    y += 56
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=font(B.SANS_BOLD, 22), fill=RED)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "5x 20% -- Einzelaktien + Bitcoin, gleich gewichtet", font=font(B.SANS_BOLD, 26), fill=CREAM)

    draw_footer(draw, 1, 9)
    return img


def slide_positions(seed, idx, n_total, label, handle, accent, positions):
    img, draw = base_slide(seed=seed)
    y = build_header(draw)

    badge_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), f"{label} -- {handle}", font=badge_font, fill=accent)
    y += 34
    brush_underline(draw, B.MARGIN_LEFT, y, 100, accent, thickness=6)
    y += 36

    for pos in positions:
        y = draw_position_card(img, draw, y, pos, accent)
        draw = ImageDraw.Draw(img)
        y += 48

    draw_footer(draw, idx, n_total)
    return img


def slide_closing_quote(idx, n_total):
    img, draw = base_slide(seed=42)
    y = build_header(draw)
    y += 50

    eyebrow_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), f"{PARTNER_HANDLE} DAZU", font=eyebrow_font, fill=TEAL)
    y += 52

    quote_font = font(B.SANS_BOLD, 36)
    lines = wrap_text(draw, f'"{PARTNER_CLOSING}"', quote_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=quote_font, fill=CREAM)
        y += 46

    draw_footer(draw, idx, n_total)
    return img


def slide_overlap(idx, n_total):
    img, draw = base_slide(seed=99)
    y = build_header(draw)
    y += 50

    eyebrow_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), "ZUFALL?", font=eyebrow_font, fill=RED)
    y += 50

    title_lines = ["BEIDE HABEN", "UNABHAENGIG VONEINANDER", "AUF SERVICENOW GESETZT."]
    for line in title_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 44), fill=CREAM)
        y += 54
    brush_underline(draw, B.MARGIN_LEFT, y + 4, 160, RED, thickness=9)
    y += 54

    body_lines = wrap_text(
        draw,
        "Ohne Absprache sind wir beide bei derselben Aktie gelandet -- ein Zeichen dafuer, dass die Story hinter dem Unternehmen bei mehreren unabhaengig ueberzeugt.",
        font(B.SANS_BOLD, 26), W - B.MARGIN_LEFT - B.MARGIN_RIGHT,
    )
    for line in body_lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 26), fill=MUTED)
        y += 34

    draw_footer(draw, idx, n_total)
    return img


def slide_outro(idx, n_total):
    img, draw = base_slide(seed=7)
    y = build_header(draw)
    y += 50

    title_font = font(B.SANS_BOLD, 48)
    for line in ["WELCHEN ANSATZ", "WUERDEST DU WAEHLEN?"]:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 58
    brush_underline(draw, B.MARGIN_LEFT, y + 4, 160, TEAL, thickness=9)
    y += 60

    body_font = font(B.SANS_BOLD, 26)
    lines = wrap_text(draw, "Schreib's uns in die Kommentare -- bei beiden Accounts.", body_font,
                       W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=CREAM)
        y += 34

    y += 60
    draw.text((B.MARGIN_LEFT, y), "Rein hypothetisch, keine Rangfolge --", font=font(B.SANS_BOLD, 24), fill=MUTED)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur zwei persoenliche Denkweisen.", font=font(B.SANS_BOLD, 24), fill=MUTED)

    draw_footer(draw, idx, n_total)
    return img


def main():
    slides = [slide_intro]
    slides.append(lambda: slide_positions(2, 2, 9, "SEIN 10K", PARTNER_HANDLE, TEAL, PARTNER_POS[0:2]))
    slides.append(lambda: slide_positions(3, 3, 9, "SEIN 10K", PARTNER_HANDLE, TEAL, PARTNER_POS[2:4]))
    slides.append(lambda: slide_closing_quote(4, 9))
    slides.append(lambda: slide_positions(5, 5, 9, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[0:2]))
    slides.append(lambda: slide_positions(6, 6, 9, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[2:4]))
    slides.append(lambda: slide_positions(7, 7, 9, "MEIN 10K", OWN_HANDLE, RED, OWN_POS[4:5]))
    slides.append(lambda: slide_overlap(8, 9))
    slides.append(lambda: slide_outro(9, 9))

    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, (8, 8, 10))
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 3
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (12, 12, 14))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = ["10.000 Euro -- wie wuerden wir sie aufteilen? Zwei komplett unterschiedliche Ansaetze."]
    for pos in PARTNER_POS:
        sentences.append(f"{pos['name']}, {pos['amount']}. {pos['why']}")
    sentences.append(PARTNER_CLOSING)
    for pos in OWN_POS:
        sentences.append(f"{pos['name']}, {pos['amount']}. {pos['why']}")
    sentences.append("Beide haben unabhaengig voneinander auf ServiceNow gesetzt.")
    sentences.append("Welchen Ansatz wuerdest du waehlen? Schreib's uns in die Kommentare.")
    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md")


if __name__ == "__main__":
    main()
