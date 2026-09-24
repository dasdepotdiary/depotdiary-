"""Neues Feed-Format "Diese Woche im Check" (2026-09-25) -- inspiriert von
@derfinanzhafen (Nutzer-Referenzvideo 2026-09-22, siehe Memory
depotdiary-derfinanzhafen-referenz): grosse fette Caps-Headline auf dem
Hook-Thumbnail + echte Marken-/Aktienlogos als Kreis-Raster statt reiner
Textliste. BEWUSST NICHT 1:1 kopiert -- kein Avatar-Icon (Nutzerwunsch,
das war ihm ohnehin egal), stattdessen die eigene depotdiary-Wortmarke
klein in der Ecke als Wiedererkennungs-Anker auf jedem Slide (der Punkt,
der bei depotdiary bisher fehlte).

Eigene Farbidentitaet: fast schwarz + Off-White + ein punchiges Rot-Orange
als Akzent -- keine der bisherigen Formate nutzt genau diese Kombination.

Input: week_label, ticker-Liste (name, ticker, logo_path).

Aufruf (Prototyp/Test):
  python posts/format_wochenlogos.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "format_wochenlogos"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

BG = "#0A0A0A"
CARD = "#161616"
CARD_BORDER = "#2C2C2C"
CREAM = "#F5F3EE"
MUTED = "#8C8C88"
ACCENT = "#FF5A36"

OWN_HANDLE = "@DASDEPOTDIARY"
WORDMARK = ROOT / "assets" / "logo_depotdiary_stacked_transparent.png"


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


def draw_wordmark_anchor(img, draw):
    """Fixer Wiedererkennungs-Anker unten rechts auf jedem Slide -- die
    depotdiary-Wortmarke statt eines Avatar-Icons."""
    try:
        logo = Image.open(WORDMARK).convert("RGBA")
        target_h = 46
        ratio = target_h / logo.height
        logo = logo.resize((max(1, int(logo.width * ratio)), target_h))
        img.paste(logo, (W - logo.width - 40, H - logo.height - 40), logo)
    except FileNotFoundError:
        pass


def base_slide():
    img = Image.new("RGB", (W, H), BG)
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([W / 2 - 500, -350, W / 2 + 500, 400], fill=45)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    red_layer = Image.new("RGB", (W, H), (70, 24, 14))
    img.paste(red_layer, (0, 0), glow)
    draw = ImageDraw.Draw(img)
    return img, draw


def slide_hook(week_label, n_stocks):
    img, draw = base_slide()
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, 64), OWN_HANDLE, font=handle_font, fill=MUTED)

    y = H * 0.30
    label_font = font(B.SANS_BOLD, 28)
    label = "DIESE WOCHE"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=ACCENT)
    y += 62

    title_font = font(B.SANS_BOLD, 84)
    for line in [f"{n_stocks} AKTIEN", "IM CHECK."]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 92

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    sub = f"Alle Aktien aus meinem Aktien-Check {week_label} -- auf einen Blick."
    for line in wrap_text(draw, sub, sub_font, W - 180):
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 40

    note_font = font(B.SANS_BOLD, 20)
    note = "Keine Anlageberatung -- reine Uebersicht."
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, H - 140), note, font=note_font, fill=MUTED)

    draw_wordmark_anchor(img, draw)
    return img


def draw_logo_grid_slide(stocks, page_label):
    img, draw = base_slide()
    handle_font = font(B.SANS_BOLD, 22)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, 56), OWN_HANDLE, font=handle_font, fill=MUTED)

    title_font = font(B.SANS_BOLD, 34)
    tw = draw.textlength(page_label, font=title_font)
    draw.text((W / 2 - tw / 2, 106), page_label, font=title_font, fill=CREAM)

    cols = 3
    gap = 28
    top = 190
    cell_w = (W - 2 * 70 - (cols - 1) * gap) / cols
    r = int(cell_w / 2) - 6
    name_font = font(B.SANS_BOLD, 19)

    for i, s in enumerate(stocks):
        row, col = divmod(i, cols)
        cx = 70 + col * (cell_w + gap) + cell_w / 2
        cy = top + row * (cell_w + 54) + r

        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFFFFF", outline=CARD_BORDER, width=2)
        try:
            logo = Image.open(s["logo_path"]).convert("RGBA")
            target = int(r * 1.35)
            ratio = min(target / logo.width, target / logo.height)
            logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
            img.paste(logo, (int(cx - logo.width / 2), int(cy - logo.height / 2)), logo)
        except FileNotFoundError:
            tf = font(B.SANS_BOLD, 22)
            tw2 = draw.textlength(s["ticker"], font=tf)
            draw.text((cx - tw2 / 2, cy - 12), s["ticker"], font=tf, fill="#111111")

        label = s["ticker"]
        lw = draw.textlength(label, font=name_font)
        draw.text((cx - lw / 2, cy + r + 12), label, font=name_font, fill=MUTED)

    draw_wordmark_anchor(img, draw)
    return img


def slide_cta():
    img, draw = base_slide()
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, 64), OWN_HANDLE, font=handle_font, fill=MUTED)

    y = H * 0.36
    title_font = font(B.SANS_BOLD, 54)
    for line in ["WELCHE WAR FUER", "DICH AM SPANNENDSTEN?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 64

    y += 40
    cta_font = font(B.SANS_BOLD, 32)
    cta = "Schreib's in die Kommentare."
    tw = draw.textlength(cta, font=cta_font)
    draw.text((W / 2 - tw / 2, y), cta, font=cta_font, fill=ACCENT)

    note_font = font(B.SANS_BOLD, 20)
    note = "Keine Anlageberatung -- reine Uebersicht, keine Bewertung."
    tw = draw.textlength(note, font=note_font)
    draw.text((W / 2 - tw / 2, H - 140), note, font=note_font, fill=MUTED)

    draw_wordmark_anchor(img, draw)
    return img


def main(week_label, stocks):
    slides = [slide_hook(week_label, len(stocks))]
    per_page = 9
    pages = [stocks[i:i + per_page] for i in range(0, len(stocks), per_page)]
    for i, page in enumerate(pages, start=1):
        label = "DIE AKTIEN" if len(pages) == 1 else f"DIE AKTIEN ({i}/{len(pages)})"
        slides.append(draw_logo_grid_slide(page, label))
    slides.append(slide_cta())

    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")

    for i in range(1, len(slides) + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    n = len(slides)
    cols = 3
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (20, 20, 20))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    stocks = [
        {"name": "SAP", "ticker": "SAP", "logo_path": ROOT / "assets" / "sap_logo_icon.png"},
        {"name": "Alphabet", "ticker": "GOOGL", "logo_path": ROOT / "assets" / "googl_logo_icon.png"},
        {"name": "Costco", "ticker": "COST", "logo_path": ROOT / "assets" / "cost_logo_icon.png"},
        {"name": "Meta", "ticker": "META", "logo_path": ROOT / "assets" / "meta_logo_icon.png"},
        {"name": "Visa", "ticker": "V", "logo_path": ROOT / "assets" / "v_logo_icon.png"},
        {"name": "ASML", "ticker": "ASML", "logo_path": ROOT / "assets" / "asml_logo_icon.png"},
        {"name": "Intel", "ticker": "INTC", "logo_path": ROOT / "assets" / "intc_logo_icon.png"},
        {"name": "Warner Bros Discovery", "ticker": "WBD", "logo_path": ROOT / "assets" / "wbd_logo_icon.png"},
        {"name": "Bank of America", "ticker": "BAC", "logo_path": ROOT / "assets" / "bac_logo_icon.png"},
        {"name": "Oracle", "ticker": "ORCL", "logo_path": ROOT / "assets" / "orcl_logo_icon.png"},
        {"name": "McDonald's", "ticker": "MCD", "logo_path": ROOT / "assets" / "mcd_logo_icon.png"},
        {"name": "JPMorgan Chase", "ticker": "JPM", "logo_path": ROOT / "assets" / "jpm_logo_icon.png"},
        {"name": "Netflix", "ticker": "NFLX", "logo_path": ROOT / "assets" / "nflx_logo_icon.png"},
        {"name": "Home Depot", "ticker": "HD", "logo_path": ROOT / "assets" / "hd_logo_icon.png"},
        {"name": "PayPal", "ticker": "PYPL", "logo_path": ROOT / "assets" / "pypl_logo_icon.png"},
    ]
    main("15.-24.09.", stocks)
