"""Collab mit @finanzlehrer.at: "3 gegen 3 -- unsere ETF-Sparplaene" (Teil 1).
Nutzerwunsch 2026-09-10: gleiches "Verschmelzung unserer Formate"-Prinzip wie
bei collab_finanzboerse_ewigkeit.py (oben Partner-Pick, unten eigener Pick,
Logo-Karten, KEIN VS-Badge -- Nutzer-Feedback von damals gilt weiter), aber
fuer 3 ETF-Paare statt 5 Aktien-Paare, explizit als "Teil 1" markiert (Teil 2
mit den Aktien-Sparplaenen folgt, sobald der Nutzer seine Picks nennt).

ETF-Listen vom Nutzer bestaetigt (2026-09-10, nach Rueckfrage zu zwei
zunaechst unklar transkribierten Namen):
  Partner (@finanzlehrer.at): iShares Core MSCI World, Vanguard FTSE
    All-World, Amundi MSCI Emerging Markets.
  Eigene (@dasdepotdiary): S&P 500, MSCI World ex USA, Core MSCI Emerging
    Markets (Fondsgesellschaft fuer die eigenen drei nicht spezifiziert --
    iShares als Platzhalter-Logo verwendet, siehe Hinweis unten).

Bewusst nur TER/Zusammensetzung/Anzahl-Unternehmen als Fakten -- keine
Performance-Vergleiche, keine Bewertung "besser/schlechter".

WICHTIG (siehe project_depotdiary_earnings_followups): bleibt reiner
lokaler Entwurf, erst nach expliziter Nutzer-Bestaetigung (native
Instagram-Collab-Einrichtung) in die Publish-Queue aufnehmen.

Aufruf:
  python posts/collab_finanzlehrer_sparplaene.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "collab_finanzlehrer_sparplaene"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

BG = (4, 4, 6)  # echtes Schwarz statt Dunkelnavy -- Nutzerwunsch 2026-09-10
CARD_BORDER = (44, 44, 50)
GOLD = (201, 162, 57)
CREAM = (240, 238, 230)
MUTED = (150, 150, 158)
GREEN = (74, 222, 128)
# Zusaetzliche bunte Akzente fuer die TER/Fondsgroesse-Badges (Nutzerwunsch
# "mehr Kontext" + "bunte Akzente") -- eigene Farben statt nur Gold/Gruen,
# damit die Fakten-Badges auf einen Blick auseinanderzuhalten sind.
CYAN = (56, 189, 248)
AMBER = (245, 166, 35)

PARTNER_HANDLE = "@FINANZLEHRER.AT"
OWN_HANDLE = "@DASDEPOTDIARY"

PAIRS = json.loads((ROOT / "posts" / "inputs" / "collab_finanzlehrer_sparplaene.json").read_text(encoding="utf-8"))["pairs"]


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


def build_header(draw, y=36):
    handle_font = font(B.SANS_BOLD, 18)
    text = f"{OWN_HANDLE}  x  {PARTNER_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=GOLD)
    y += 28
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=CARD_BORDER, width=1)
    return y + 18


def _scatter_particles(img, seed):
    """Dezente bunte Akzent-Punkte/Rauten im Hintergrund -- Anlehnung an den
    @rendite.radar.official-Look (Nutzerwunsch 2026-09-10), aber eigenstaendig
    statt kopiert: sehr kleine, gedaempfte Formen, stoeren den Text nie."""
    import random
    rnd = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    colors = [(*GOLD, 60), (*GREEN, 55), (*CYAN, 55), (*AMBER, 55)]
    for _ in range(14):
        x = rnd.randint(40, W - 40)
        y = rnd.randint(40, H - 40)
        r = rnd.randint(3, 7)
        color = rnd.choice(colors)
        if rnd.random() < 0.5:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        else:
            draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=color)


def base_slide(seed=1):
    img = Image.new("RGB", (W, H), BG)
    _scatter_particles(img, seed)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=GOLD)
    return img, draw


def draw_badge(draw, x, y, label, color):
    badge_font = font(B.SANS_BOLD, 15)
    tw = draw.textlength(label, font=badge_font)
    pad_x, pad_y = 12, 6
    draw.rounded_rectangle([x, y, x + tw + pad_x * 2, y + 15 + pad_y * 2], radius=12,
                            outline=color, width=2)
    draw.text((x + pad_x, y + pad_y), label, font=badge_font, fill=color)
    return tw + pad_x * 2


def draw_pick_half(img, draw, top, bottom, pick, who_label, accent):
    draw.text((B.MARGIN_LEFT, top), who_label, font=font(B.SANS_BOLD, 15), fill=accent)

    logo_r = 46
    logo_cx = B.MARGIN_LEFT + logo_r
    logo_cy = top + 34 + logo_r
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
                 fill=CREAM, outline=accent, width=2)
    logo = Image.open(ROOT / "assets" / pick["logo"]).convert("RGBA")
    target = int(logo_r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (logo_cx - logo.width // 2, logo_cy - logo.height // 2), logo)
    draw = ImageDraw.Draw(img)

    text_x = logo_cx + logo_r + 24
    name_font = font(B.SANS_BOLD, 26)
    draw.text((text_x, top + 30), pick["name"], font=name_font, fill=CREAM)
    ticker_font = font(B.SANS_BOLD, 17)
    draw.text((text_x, top + 62), pick["ticker"], font=ticker_font, fill=accent)

    # Bunte Fakten-Badges (TER/Fondsgroesse) -- "mehr Kontext" auf einen Blick,
    # eigene Akzentfarben statt nur Gold/Gruen (Nutzerwunsch 2026-09-10).
    badge_y = logo_cy + logo_r + 14
    bx = B.MARGIN_LEFT
    if pick.get("ter"):
        bx += draw_badge(draw, bx, badge_y, f"TER {pick['ter']}", CYAN) + 10
    if pick.get("aum"):
        draw_badge(draw, bx, badge_y, f"Volumen {pick['aum']}", AMBER)

    why_font = font(B.SANS_BOLD, 17)
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    lines = wrap_text(draw, pick["why"], why_font, max_w)
    y = badge_y + 38
    for line in lines[:6]:
        draw.text((B.MARGIN_LEFT, y), line, font=why_font, fill=MUTED)
        y += 23
    return draw


def draw_mini_logo(img, cx, cy, r, logo_path, ring_color):
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=ring_color, width=3)
    logo = Image.open(ROOT / "assets" / logo_path).convert("RGBA")
    target = int(r * 1.4)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def draw_footer(draw, idx, n_total, text="Keine Anlageberatung -- persoenliche Sparplaene, kein Ratschlag."):
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


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, 90), "COLLAB · TEIL 1: ETFs", font=eyebrow_font, fill=GOLD)

    y = 128
    draw.text((B.MARGIN_LEFT, y), "3 gegen 3.", font=font(B.SANS_BOLD, 56), fill=CREAM)
    y += 66
    draw.text((B.MARGIN_LEFT, y), "Unsere ETF-Sparplaene.", font=font(B.SANS_BOLD, 32), fill=GOLD)
    y += 46
    lines = wrap_text(draw, "Je drei ETFs pro Seite -- Teil 2 mit unseren Aktien-Sparplaenen folgt bald.",
                       font(B.SANS_BOLD, 20), W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 20), fill=MUTED)
        y += 26
    y += 20

    col_w = (W - B.MARGIN_LEFT - B.MARGIN_RIGHT - 60) / 2
    left_x = B.MARGIN_LEFT
    right_x = B.MARGIN_LEFT + col_w + 60
    draw.text((left_x, y), PARTNER_HANDLE, font=font(B.SANS_BOLD, 19), fill=GOLD)
    draw.text((right_x, y), OWN_HANDLE, font=font(B.SANS_BOLD, 19), fill=GREEN)
    y += 36

    mid_x = left_x + col_w + 30
    rows_top = y
    row_gap = 150
    logo_r = 46
    name_font = font(B.SANS_BOLD, 18)

    for i, pair in enumerate(PAIRS):
        cy = rows_top + logo_r + i * row_gap
        draw_mini_logo(img, int(left_x + col_w / 2), cy, logo_r, pair["partner"]["logo"], GOLD)
        tw = draw.textlength(pair["partner"]["name"], font=name_font)
        draw.text((left_x + col_w / 2 - tw / 2, cy + logo_r + 10), pair["partner"]["name"], font=name_font, fill=CREAM)

        draw_mini_logo(img, int(right_x + col_w / 2), cy, logo_r, pair["own"]["logo"], GREEN)
        tw = draw.textlength(pair["own"]["name"], font=name_font)
        draw.text((right_x + col_w / 2 - tw / 2, cy + logo_r + 10), pair["own"]["name"], font=name_font, fill=CREAM)

    rows_bottom = rows_top + logo_r + (len(PAIRS) - 1) * row_gap + logo_r + 30
    draw.line([(mid_x, rows_top - 6), (mid_x, rows_bottom)], fill=CARD_BORDER, width=2)

    draw_footer(draw, 1, 5)
    return img


def slide_pair(pair, idx, n_total):
    img, draw = base_slide(seed=idx)
    top = build_header(draw)

    footer_h = 70
    footer_top = H - footer_h
    usable_bottom = footer_top - 10
    half_h = (usable_bottom - top - 16) // 2
    mid_y = top + half_h + 8

    draw = draw_pick_half(img, draw, top, mid_y - 8, pair["partner"], f"SPARPLAN VON {PARTNER_HANDLE}", GOLD)
    draw.line([(B.MARGIN_LEFT, mid_y), (W - B.MARGIN_RIGHT, mid_y)], fill=CARD_BORDER, width=2)
    draw = draw_pick_half(img, draw, mid_y + 14, usable_bottom, pair["own"], f"MEIN SPARPLAN ({OWN_HANDLE})", GREEN)

    draw_footer(draw, idx, n_total)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)

    y += 20
    title_font = font(B.SANS_BOLD, 36)
    lines = wrap_text(draw, "Welchen der 6 ETFs hast du", title_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=title_font, fill=CREAM)
        y += 46
    draw.text((B.MARGIN_LEFT, y), "selbst im Depot?", font=title_font, fill=CREAM)
    y += 66

    body_font = font(B.SANS_BOLD, 22)
    lines2 = wrap_text(draw, "Schreib's uns in die Kommentare -- bei beiden Accounts.",
                        body_font, W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines2:
        draw.text((B.MARGIN_LEFT, y), line, font=body_font, fill=GOLD)
        y += 30

    y += 30
    lines3 = wrap_text(draw, "Teil 2 mit unseren Aktien-Sparplaenen folgt in Kuerze.",
                        font(B.SANS_BOLD, 22), W - B.MARGIN_LEFT - B.MARGIN_RIGHT)
    for line in lines3:
        draw.text((B.MARGIN_LEFT, y), line, font=font(B.SANS_BOLD, 22), fill=GREEN)
        y += 30

    y += 34
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 90, y)], fill=GOLD, width=3)
    y += 24
    draw.text((B.MARGIN_LEFT, y), "Keine Rangfolge, keine Bewertung --", font=font(B.SANS_BOLD, 22), fill=CREAM)
    y += 32
    draw.text((B.MARGIN_LEFT, y), "nur unsere persoenlichen Sparplaene.", font=font(B.SANS_BOLD, 22), fill=CREAM)

    draw_footer(draw, 5, 5)
    return img


def main():
    slides = [slide_intro]
    for i, pair in enumerate(PAIRS, start=2):
        slides.append(lambda p=pair, i=i: slide_pair(p, i, 5))
    slides.append(slide_outro)

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

    cols = 3
    rows = (n + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    main()
