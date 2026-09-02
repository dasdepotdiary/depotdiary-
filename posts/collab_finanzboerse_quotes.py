"""Co-Post mit @finanzboerse: "20 Boersen-Weisheiten" -- 10 Zitate von ihm,
10 von mir ausgesucht. GEPAART: ein Zitat von ihm oben, eins von mir unten,
auf derselben Folie -- macht genau 10 Folien statt 21 (Instagram-Carousel-
Limit ist 10 Bilder, 21 Einzel-Zitat-Folien gingen sich nicht aus).

Reine Zitat-Sammlung (bekannte Investoren-/Volksweisheiten), keine eigene
Bewertung, kein Bezug zu konkreten Einzelaktien -- compliance-technisch
unkritisch.

Design: dunkle, editoriale Zitat-Karte mit grossem transparenten
Anfuehrungszeichen als Hintergrund-Flourish je Haelfte, serifige Kursiv-
schrift fuer das Zitat, Autor in Gold darunter, wechselnde Akzentfarbe pro
Folie fuer Rhythmus. Farbwelt uebernommen von posts/collab_finanzboerse.py.

QUOTES_PARTNER: vom Nutzer per Screenshot geliefert (10 Zitate von
@finanzboerse, 2026-09-02) -- hier 1:1 uebernommen, in genau dieser
Reihenfolge mit QUOTES_OWN gepaart (Position i oben, Position i unten).
QUOTES_OWN: von Claude ausgesucht, keine Ueberschneidung mit den Partner-
Zitaten.

Aufruf:
  python posts/collab_finanzboerse_quotes.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

NAME = "collab_finanzboerse_quotes"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE
MID = H // 2

FB_BG = (9, 13, 22)
FB_CARD = (17, 23, 37)
FB_GOLD = (201, 162, 57)
FB_GOLD_SOFT = (150, 128, 78)
FB_WHITE = (245, 245, 240)
FB_GREY = (150, 158, 175)
FB_QUOTE_MARK = (30, 38, 56)

PARTNER_HANDLE = "@FINANZBOERSE"
OWN_HANDLE = "@DASDEPOTDIARY"
SERIES_TITLE = "20 BOERSEN-WEISHEITEN"

QUOTES_PARTNER = [
    ("Kaufe nicht die Aktie, sondern das Unternehmen.", ""),
    ("Zeit im Markt schlaegt das Timing des Marktes.", ""),
    ("Hin und her macht Taschen leer.", ""),
    ("Lege niemals alle Eier in einen Korb.", ""),
    ("Sei gierig, wenn andere aengstlich sind, und aengstlich, wenn andere gierig sind.", "Warren Buffett"),
    ("An der Boerse wird zum Einstieg nicht geklingelt.", ""),
    ("Gewinne laufen lassen, Verluste begrenzen.", ""),
    ("Die Boerse belohnt Geduldige und bestraft Impulsive.", ""),
    ("Investiere nur in etwas, das du auch verstehst.", ""),
    ("Kaufen, wenn die Kanonen donnern -- verkaufen, wenn die Violinen spielen.", "Nathan Rothschild (zugeschrieben)"),
]

QUOTES_OWN = [
    ("Preis ist, was du zahlst. Wert ist, was du bekommst.", "Warren Buffett"),
    ("Der Markt kann laenger irrational bleiben, als du solvent bleiben kannst.", "John Maynard Keynes"),
    ("Die vier gefaehrlichsten Woerter beim Investieren: „Dieses Mal ist es anders.“", "Sir John Templeton"),
    ("Diversifikation ist der einzige Free Lunch an der Boerse.", "Harry Markowitz"),
    ("Man muss nicht besonders klug sein, um an der Boerse Erfolg zu haben -- man muss nur nicht dumm sein.", "Charlie Munger"),
    ("Der Zinseszins ist die staerkste Kraft im Universum.", "Albert Einstein (zugeschrieben)"),
    ("Der beste Zeitpunkt, einen Baum zu pflanzen, war vor 20 Jahren. Der zweitbeste ist heute.", "Chinesisches Sprichwort"),
    ("An der Boerse verdient man sein Geld eher durchs Sitzen als durchs Handeln.", "frei nach Jesse Livermore"),
    ("Sicherheit ist wichtiger als Rendite.", "Benjamin Graham"),
    ("Wisse, was du besitzt, und wisse, warum du es besitzt.", "Peter Lynch"),
]

ACCENTS = [FB_GOLD, (196, 130, 84), (110, 168, 150), FB_GOLD, (170, 110, 200)]


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_rotated_mark(img, cx, cy, size, angle, color):
    mark_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(mark_img)
    f = font(B.SERIF_BOLD, int(size * 0.9))
    d.text((0, -size * 0.12), "„", font=f, fill=color + (255,))
    rotated = mark_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)), rotated)


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


def build_header(draw, subtitle=SERIES_TITLE):
    y = 36
    handle_font = font(B.SANS_BOLD, 18)
    title_font = font(B.SANS_BOLD, 19)
    text = f"{PARTNER_HANDLE}  x  {OWN_HANDLE}"
    draw.text((B.MARGIN_LEFT, y), text, font=handle_font, fill=FB_GOLD)
    y += 27
    draw.text((B.MARGIN_LEFT, y), subtitle, font=title_font, fill=FB_WHITE)
    y += 29
    draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=FB_CARD, width=1)
    return y + 16


def draw_quote_half(img, draw, top, bottom, quote, author, who_label, accent, mark_angle):
    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    half_h = bottom - top

    draw.text((B.MARGIN_LEFT, top), who_label, font=font(B.SANS_BOLD, 15), fill=accent)

    mark_size = 210
    draw_rotated_mark(img, W - B.MARGIN_RIGHT - 70, top + half_h - 60, mark_size, mark_angle, FB_QUOTE_MARK)
    draw = ImageDraw.Draw(img)

    is_punchy = len(quote) < 50
    quote_font_size = 32 if is_punchy else (26 if len(quote) < 90 else (21 if len(quote) < 120 else 18))
    quote_font = font(B.SERIF_BOLD_ITALIC, quote_font_size)
    lines = wrap_text(draw, quote, quote_font, max_w - 40)
    line_h = int(quote_font_size * 1.24)

    y = top + 44
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=quote_font, fill=FB_WHITE)
        y += line_h

    y += 14
    draw.line([(B.MARGIN_LEFT, y), (B.MARGIN_LEFT + 56, y)], fill=accent, width=3)
    y += 12
    author_text = f"-- {author}" if author else "-- Boersenweisheit"
    draw.text((B.MARGIN_LEFT, y), author_text, font=font(B.SANS_BOLD, 17), fill=accent)
    return draw


def build_paired_slide(partner_q, own_q, idx, n_total):
    img = Image.new("RGB", (W, H), FB_BG)
    draw = ImageDraw.Draw(img)
    top = build_header(draw)
    accent = ACCENTS[idx % len(ACCENTS)]
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=accent)

    footer_top = H - 88
    usable_bottom = footer_top - 10
    half_h = (usable_bottom - top - 20) // 2
    mid_y = top + half_h + 10

    draw = draw_quote_half(img, draw, top, mid_y - 10, partner_q[0], partner_q[1],
                            f"VON {PARTNER_HANDLE}", accent, -6)
    draw.line([(B.MARGIN_LEFT, mid_y), (W - B.MARGIN_RIGHT, mid_y)], fill=FB_CARD, width=1)
    draw = draw_quote_half(img, draw, mid_y + 14, usable_bottom, own_q[0], own_q[1],
                            f"MEIN PICK ({OWN_HANDLE})", B.GREEN_MID, 5)

    draw.line([(B.MARGIN_LEFT, footer_top), (W - B.MARGIN_RIGHT, footer_top)], fill=FB_CARD, width=1)
    draw.text((B.MARGIN_LEFT, footer_top + 14), "Bekannte Boersenweisheiten -- keine Anlageberatung.",
               font=font(B.SANS_BOLD, 15), fill=FB_GREY)
    page_font = font(B.SANS_BOLD, 17)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, footer_top + 14), page_text, font=page_font, fill=FB_GREY)

    return img


def main():
    n = len(QUOTES_PARTNER)
    assert n == len(QUOTES_OWN)
    for i in range(n):
        img = build_paired_slide(QUOTES_PARTNER[i], QUOTES_OWN[i], i + 1, n)
        img.save(IG_DIR / f"slide_{i + 1}.png")

    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, FB_BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 5
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
