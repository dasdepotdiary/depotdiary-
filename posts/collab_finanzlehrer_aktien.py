"""Collab mit @finanzlehrer.at: "5 gegen 7 -- unsere Aktien-Sparplaene" (Teil 2).

v2 (2026-09-16, Nutzer: "gefaellt mir diesmal nicht, schoeneres catchenderes
besonderes Design"): komplett neu als KASSENBON-Optik -- monatliche
Sparplaene als "Einkaufsbeleg" mit Monospace-Schrift, gestrichelten
Trennlinien, gezacktem Papierrand und Zwischensumme/Gesamt wie auf einem
echten Kassenbon. Bewusst weder die dunklen Logo-Karten aus Teil 1 noch die
cremefarbene Statement-Liste der ersten Teil-2-Version.

Listen vom Nutzer (2026-09-16, monatliche Sparplan-Betraege):
  Partner (@finanzlehrer.at): Meta Platforms 50E, Coca-Cola 50E,
    Procter & Gamble 50E, Bitcoin 50E, Solana 50E.
  Eigene (@dasdepotdiary): JPMorgan Chase 80E, Visa 50E, TSMC 40E,
    RTX Corporation 60E, Modine Manufacturing 15E, Eaton Corporation 35E,
    IES Holdings 30E.

Reine Fakten (Betraege, Positionen) -- keine Bewertung, keine Empfehlung.

WICHTIG: bleibt reiner lokaler Entwurf, erst nach expliziter Nutzer-
Bestaetigung (native Instagram-Collab-Einrichtung) in die Publish-Queue.

Aufruf:
  python posts/collab_finanzlehrer_aktien.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "collab_finanzlehrer_aktien"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

TABLE_BG = "#15130F"
PAPER = "#FAF7F0"
PAPER_SHADOW = "#EDE8DA"
INK = "#211E19"
FAINT = "#8A8478"
DASH = "#C9C2B0"
RED_STAMP = "#B5453A"
GREEN_STAMP = "#3F6B4E"

MONO = str(ROOT / "assets" / "fonts" / "SpaceMono-Regular.ttf")
MONO_BOLD = str(ROOT / "assets" / "fonts" / "SpaceMono-Bold.ttf")

PARTNER_HANDLE = "@FINANZLEHRER.AT"
OWN_HANDLE = "@DASDEPOTDIARY"

PARTNER_ROWS = [("Meta Platforms", 50), ("Coca-Cola", 50), ("Procter & Gamble", 50),
                ("Bitcoin", 50), ("Solana", 50)]
OWN_ROWS = [("JPMorgan Chase", 80), ("Visa", 50), ("TSMC", 40), ("RTX Corporation", 60),
            ("Modine Manufacturing", 15), ("Eaton Corporation", 35), ("IES Holdings", 30)]


def font(path, size):
    return ImageFont.truetype(path, size)


def eur(v):
    return f"{v:,.2f} E".replace(",", "X").replace(".", ",").replace("X", ".")


def zigzag_edge(draw, y, width_start, direction=1):
    """Gezackter Papierrand (oben oder unten am Bon)."""
    tooth = 22
    n = W // tooth
    pts = []
    for i in range(n + 1):
        x = i * tooth
        ty = y + (10 if i % 2 == 0 else 0) * direction
        pts.append((x, ty))
    poly = pts + [(W, y + 40 * direction), (0, y + 40 * direction)]
    draw.polygon(poly, fill=PAPER if direction == -1 else "#00000000")


def receipt_canvas():
    img = Image.new("RGB", (W, H), TABLE_BG)
    draw = ImageDraw.Draw(img)
    # Papier-Rechteck mit Schattenkante
    draw.rectangle([40, 30, W - 40, H - 30], fill=PAPER_SHADOW)
    draw.rectangle([30, 20, W - 50, H - 40], fill=PAPER)
    return img, draw


def dashed_line(draw, x1, x2, y, fill=DASH, dash=8, gap=6, width=2):
    x = x1
    while x < x2:
        draw.line([(x, y), (min(x + dash, x2), y)], fill=fill, width=width)
        x += dash + gap


def draw_receipt_header(draw, title_lines, subtitle):
    y = 90
    f_brand = font(MONO_BOLD, 30)
    tw = draw.textlength("DEPOT DIARY x FINANZLEHRER", font=f_brand)
    draw.text((W / 2 - tw / 2, y), "DEPOT DIARY x FINANZLEHRER", font=f_brand, fill=INK)
    y += 44
    f_small = font(MONO, 17)
    tw = draw.textlength("SPARPLAN-BELEG  //  MONATLICH", font=f_small)
    draw.text((W / 2 - tw / 2, y), "SPARPLAN-BELEG  //  MONATLICH", font=f_small, fill=FAINT)
    y += 36
    dashed_line(draw, 80, W - 80, y)
    y += 36
    f_title = font(MONO_BOLD, 34)
    for line in title_lines:
        tw = draw.textlength(line, font=f_title)
        draw.text((W / 2 - tw / 2, y), line, font=f_title, fill=INK)
        y += 42
    if subtitle:
        y += 8
        f_sub = font(MONO, 18)
        sub_lines = wrap_mono(draw, subtitle, f_sub, W - 160)
        for line in sub_lines:
            tw = draw.textlength(line, font=f_sub)
            draw.text((W / 2 - tw / 2, y), line, font=f_sub, fill=FAINT)
            y += 26
    y += 20
    dashed_line(draw, 80, W - 80, y)
    return y + 30


def wrap_mono(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_receipt_rows(draw, y, rows, accent=INK):
    row_font = font(MONO, 22)
    x_left, x_right = 80, W - 80
    for name, amount in rows:
        amt_text = eur(amount)
        aw = draw.textlength(amt_text, font=row_font)
        name_max = x_right - x_left - aw - 20
        name_disp = name
        while draw.textlength(name_disp, font=row_font) > name_max and len(name_disp) > 3:
            name_disp = name_disp[:-1]
        if name_disp != name:
            name_disp = name_disp[:-1] + "."
        draw.text((x_left, y), name_disp, font=row_font, fill=INK)
        draw.text((x_right - aw, y), amt_text, font=row_font, fill=accent)
        # gepunktete Fuehrungslinie
        nw = draw.textlength(name_disp, font=row_font)
        dot_font = font(MONO, 22)
        dx = x_left + nw + 10
        while dx < x_right - aw - 10:
            draw.text((dx, y), ".", font=dot_font, fill=DASH)
            dx += 9
        y += 40
    return y


def draw_total_row(draw, y, label, amount, accent):
    dashed_line(draw, 80, W - 80, y)
    y += 24
    f = font(MONO_BOLD, 30)
    draw.text((80, y), label, font=f, fill=INK)
    amt_text = eur(amount)
    aw = draw.textlength(amt_text, font=f)
    draw.text((W - 80 - aw, y), amt_text, font=f, fill=accent)
    return y + 50


def draw_footer(draw, idx, n_total):
    y = H - 150
    dashed_line(draw, 80, W - 80, y)
    y += 24
    f = font(MONO, 16)
    lines = ["KEINE ANLAGEBERATUNG -- NUR", "UNSERE PERSOENLICHEN SPARPLAENE."]
    for line in lines:
        tw = draw.textlength(line, font=f)
        draw.text((W / 2 - tw / 2, y), line, font=f, fill=FAINT)
        y += 22
    y += 10
    page_text = f"BELEG {idx:02d}/{n_total:02d}"
    tw = draw.textlength(page_text, font=f)
    draw.text((W / 2 - tw / 2, y), page_text, font=f, fill=FAINT)


def stamp(img, cx, cy, text, color, angle=-12):
    stamp_font = font(MONO_BOLD, 30)
    tmp = Image.new("RGBA", (400, 100), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)
    tdraw.rounded_rectangle([4, 4, 396, 96], radius=14, outline=color, width=5)
    tw = tdraw.textlength(text, font=stamp_font)
    tdraw.text((200 - tw / 2, 34), text, font=stamp_font, fill=color)
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)


def slide_intro():
    img, draw = receipt_canvas()
    y = draw_receipt_header(draw, ["5 GEGEN 7", "UNSERE AKTIEN-", "SPARPLAENE"],
                             "Nach den ETFs jetzt die Einzelaktien-Seite -- zwei komplette Belege, ein Vergleich.")
    y += 20
    f = font(MONO, 19)
    lines = ["> " + PARTNER_HANDLE + ": 5 Positionen",
             "> " + OWN_HANDLE + ": 7 Positionen"]
    for line in lines:
        draw.text((W / 2 - draw.textlength(line, font=f) / 2, y), line, font=f, fill=FAINT)
        y += 30
    stamp(img, W - 190, H - 280, "TEIL 2", RED_STAMP)
    draw_footer(draw, 1, 4)
    return img


def slide_partner():
    img, draw = receipt_canvas()
    y = draw_receipt_header(draw, ["BELEG: " + PARTNER_HANDLE], "5 Positionen, je 50 Euro im Monat.")
    y = draw_receipt_rows(draw, y, PARTNER_ROWS)
    y += 10
    draw_total_row(draw, y, "GESAMT/MONAT", 250, RED_STAMP)
    stamp(img, W - 170, H - 260, "GLEICH-\nGEWICHTET".replace("\n", " "), RED_STAMP, angle=-10)
    draw_footer(draw, 2, 4)
    return img


def slide_own():
    img, draw = receipt_canvas()
    y = draw_receipt_header(draw, ["BELEG: " + OWN_HANDLE], "7 Positionen, unterschiedlich gewichtet.")
    y = draw_receipt_rows(draw, y, OWN_ROWS)
    y += 10
    draw_total_row(draw, y, "GESAMT/MONAT", 310, GREEN_STAMP)
    draw_footer(draw, 3, 4)
    return img


def slide_outro():
    img, draw = receipt_canvas()
    y = draw_receipt_header(draw, ["ENDSUMME"], "Keine Rangfolge, keine Bewertung -- nur zwei unterschiedliche Ansaetze.")
    y += 10
    f_label = font(MONO, 20)
    f_val = font(MONO_BOLD, 46)
    for handle, total, color in [(PARTNER_HANDLE, 250, RED_STAMP), (OWN_HANDLE, 310, GREEN_STAMP)]:
        draw.text((80, y), handle, font=f_label, fill=FAINT)
        y += 28
        val_text = eur(total)
        draw.text((80, y), val_text, font=f_val, fill=color)
        y += 66
    dashed_line(draw, 80, W - 80, y)
    y += 30
    f_cta = font(MONO_BOLD, 22)
    lines = wrap_mono(draw, "WELCHE DER 12 AKTIEN HAST DU SELBST IM DEPOT?", f_cta, W - 160)
    for line in lines:
        draw.text((W / 2 - draw.textlength(line, font=f_cta) / 2, y), line, font=f_cta, fill=INK)
        y += 30
    y += 10
    f_body = font(MONO, 18)
    for line in wrap_mono(draw, "Schreib's uns in die Kommentare -- bei beiden Accounts.", f_body, W - 160):
        draw.text((W / 2 - draw.textlength(line, font=f_body) / 2, y), line, font=f_body, fill=FAINT)
        y += 24
    draw_footer(draw, 4, 4)
    return img


def main():
    slides = [slide_intro, slide_partner, slide_own, slide_outro]
    for i, fn in enumerate(slides, start=1):
        fn().save(IG_DIR / f"slide_{i}.png")

    n = len(slides)
    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, TABLE_BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 4
    sheet = Image.new("RGB", (W * cols + 16 * (cols + 1), H + 32), (25, 25, 25))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        sheet.paste(im, (16 + (i - 1) * (W + 16), 16))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")

    sentences = [
        "Fuenf gegen sieben. Unsere Aktien-Sparplaene -- nach den ETFs jetzt die Einzelaktien-Seite.",
        "Der Beleg von Finanzlehrer punkt at: fuenf Positionen, je fuenfzig Euro im Monat -- zusammen zweihundertfuenfzig Euro.",
        "Mein Beleg: sieben Positionen, unterschiedlich gewichtet -- zusammen dreihundertzehn Euro im Monat.",
        "Zweihundertfuenfzig Euro gegen dreihundertzehn Euro -- keine Bewertung, nur zwei unterschiedliche Ansaetze. Welche der zwoelf Aktien hast du selbst im Depot?",
    ]
    voiceover.write(NAME, sentences)
    print("Voiceover-Skript:", OUTPUT / "script.md")


if __name__ == "__main__":
    main()
