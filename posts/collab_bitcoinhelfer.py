"""Co-Post mit @bitcoinhelfer: 5 Gruende fuer Bitcoin (seine Sicht oben im
Bitcoinhelfer-Stil, meine unten im depotdiary-Stil) + 1 Allokations-Vergleich.

Aufruf:
  python posts/collab_bitcoinhelfer.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

NAME = "collab_bitcoinhelfer"
OUTPUT = Path(__file__).parent.parent / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE
MID = H // 2

BH_BG = (14, 12, 10)
BH_ORANGE = (247, 147, 26)
BH_ORANGE_SOFT = (140, 90, 40)
BH_WHITE = (250, 248, 244)
BH_GREY = (170, 162, 150)


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_stroked_text(draw, xy, text, font_obj, fill, stroke_fill, stroke_w=3):
    x, y = xy
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx * dx + dy * dy <= stroke_w * stroke_w:
                draw.text((x + dx, y + dy), text, font=font_obj, fill=stroke_fill)
    draw.text((x, y), text, font=font_obj, fill=fill)


def draw_partner_half(img, rank, headline_lines, body):
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MID], fill=BH_BG)

    pad = 40
    card_top, card_bottom = 150, MID - 40
    draw.rounded_rectangle([pad, card_top, W - pad, card_bottom], radius=18, fill=(22, 18, 15),
                            outline=BH_ORANGE_SOFT, width=1)

    label_font = font(B.SANS_BOLD, 20)
    badge_font = font(B.SANS_BOLD, 26)
    headline_font = font(B.SANS_BOLD, 34)
    body_font = font(B.SANS_BOLD, 20)

    badge_r = 26
    bcx, bcy = W - pad - 44, card_top + 44
    draw.ellipse([bcx - badge_r, bcy - badge_r, bcx + badge_r, bcy + badge_r],
                 outline=BH_ORANGE, width=3)
    bt = str(rank)
    btw = draw.textlength(bt, font=badge_font)
    draw.text((bcx - btw / 2, bcy - 16), bt, font=badge_font, fill=BH_ORANGE)

    x = pad + 32
    y = card_top + 30
    draw.text((x, y), "@BITCOINHELFER", font=label_font, fill=BH_ORANGE)
    y += 46
    for line in headline_lines:
        draw_stroked_text(draw, (x, y), line, headline_font, BH_WHITE, (0, 0, 0), stroke_w=2)
        y += 42
    y += 14
    for line in body:
        draw.text((x, y), line, font=body_font, fill=BH_GREY)
        y += 27

    wm_font = font(B.SANS_BOLD, 18)
    draw.text((x, card_bottom + 14), "BITCOINHELFER ₿", font=wm_font, fill=BH_ORANGE)


def draw_depotdiary_half(draw, headline_lines, body):
    pad_x = B.MARGIN_LEFT
    max_w_right = W - B.MARGIN_RIGHT

    owner_font = font(B.SANS_BOLD, 20)
    headline_font = font(B.SERIF_BOLD, 30)
    body_font = font(B.SERIF_REGULAR, 20)

    y = MID + 40
    draw.text((pad_x, y), "@DASDEPOTDIARY", font=owner_font, fill=B.GREEN)
    y += 44
    for line in headline_lines:
        draw.text((pad_x, y), line, font=headline_font, fill=B.INK)
        y += 40
    y += 12
    for line in body:
        draw.text((pad_x, y), line, font=body_font, fill=B.SUBTEXT)
        y += 29


def build_slide(n_total, idx, rank, his, mine):
    img = Image.new("RGB", (W, H), B.BG)
    draw_partner_half(img, rank, his["headline"], his["body"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)
    draw.line([(0, MID), (W, MID)], fill=B.DIVIDER, width=3)

    draw_depotdiary_half(draw, mine["headline"], mine["body"])

    disclaimer_font = font(B.SERIF_REGULAR, 17)
    draw.text((B.MARGIN_LEFT, H - 44), "Keine Anlageberatung. Beide Seiten: eigene Meinung, keine Empfehlung.",
               font=disclaimer_font, fill=B.SUBTEXT)

    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 70), page_text, font=page_font, fill=B.SUBTEXT)

    return img


def build_intro():
    img = Image.new("RGB", (W, H), BH_BG)
    draw = ImageDraw.Draw(img)
    draw.text((B.MARGIN_LEFT, 90), "CO-POST", font=font(B.SANS_BOLD, 22), fill=BH_ORANGE)
    draw_stroked_text(draw, (B.MARGIN_LEFT, 380), "5 Gruende.",
                       font(B.SANS_BOLD, 66), BH_WHITE, (0, 0, 0), stroke_w=3)
    draw_stroked_text(draw, (B.MARGIN_LEFT, 460), "2 Perspektiven.",
                       font(B.SANS_BOLD, 66), BH_WHITE, (0, 0, 0), stroke_w=3)
    draw.text((B.MARGIN_LEFT, 590), "Warum wir beide Bitcoin halten.",
               font=font(B.SANS_BOLD, 26), fill=BH_ORANGE)
    draw.text((B.MARGIN_LEFT, H - 120), "@BITCOINHELFER  x  @DASDEPOTDIARY",
               font=font(B.SANS_BOLD, 22), fill=BH_ORANGE)
    draw.text((B.MARGIN_LEFT, H - 80), "Keine Anlageberatung -- eigene Meinung, keine Empfehlung.",
               font=font(B.SANS_BOLD, 18), fill=BH_GREY)
    return img


def build_allocation_slide(idx, n_total):
    img = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MID], fill=BH_BG)

    pad = 40
    card_top, card_bottom = 150, MID - 40
    draw.rounded_rectangle([pad, card_top, W - pad, card_bottom], radius=18, fill=(22, 18, 15),
                            outline=BH_ORANGE_SOFT, width=1)
    x = pad + 32
    y = card_top + 30
    draw.text((x, y), "@BITCOINHELFER", font=font(B.SANS_BOLD, 20), fill=BH_ORANGE)
    y += 46
    draw_stroked_text(draw, (x, y), "96-98% Bitcoin-Anteil", font(B.SANS_BOLD, 34), BH_WHITE, (0, 0, 0), stroke_w=2)
    y += 56
    for line in ["Bewusste Entscheidung, damit", "absolut zufrieden.",
                 "Fuer mich zaehlt vor allem", "das langfristige Prinzip dahinter,",
                 "nicht die kurzfristige Schwankung."]:
        draw.text((x, y), line, font=font(B.SANS_BOLD, 20), fill=BH_GREY)
        y += 27
    draw.text((x, card_bottom + 14), "BITCOINHELFER ₿", font=font(B.SANS_BOLD, 18), fill=BH_ORANGE)

    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)
    draw.line([(0, MID), (W, MID)], fill=B.DIVIDER, width=3)

    pad_x = B.MARGIN_LEFT
    y = MID + 40
    draw.text((pad_x, y), "@DASDEPOTDIARY", font=font(B.SANS_BOLD, 20), fill=B.GREEN)
    y += 44
    draw.text((pad_x, y), "~15% Bitcoin-Anteil", font=font(B.SERIF_BOLD, 30), fill=B.INK)
    y += 52
    for line in ["Als ein Baustein von mehreren --", "nicht mein einziger Fokus.",
                 "Daneben Einzelaktien, ETFs/Fonds", "und ein kleiner Goldanteil."]:
        draw.text((pad_x, y), line, font=font(B.SERIF_REGULAR, 20), fill=B.SUBTEXT)
        y += 29
    y += 14
    draw.text((pad_x, y), "Allokation ist individuell.", font=font(B.SERIF_BOLD, 22), fill=B.INK)
    y += 32
    for line in ["Was fuer den einen passt, kann fuer", "den anderen zu viel Volatilitaet sein.",
                 "Beide Wege koennen fuer die jeweilige", "Person richtig sein -- es gibt kein",
                 "pauschal richtiges Verhaeltnis."]:
        draw.text((pad_x, y), line, font=font(B.SERIF_REGULAR, 19), fill=B.SUBTEXT)
        y += 27

    disclaimer_font = font(B.SERIF_REGULAR, 17)
    draw.text((B.MARGIN_LEFT, H - 44), "Keine Anlageberatung. Beide Seiten: eigene Meinung, keine Empfehlung.",
               font=disclaimer_font, fill=B.SUBTEXT)
    page_font = font(B.SANS_BOLD, 20)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, H - 70), page_text, font=page_font, fill=B.SUBTEXT)
    return img


PAIRS = [
    (
        {"headline": ["Wertspeicher fuer", "Kaufkraft & Lebenszeit"],
         "body": ["Bitcoin bewahrt den Gegenwert", "geleisteter Arbeit ueber Zeit.",
                   "Anders als bei klassischem Sparen", "ohne staendige Kaufkraft-Verwaesserung.",
                   "Fuer mich einer der Hauptgruende,", "warum ich langfristig dabei bleibe."]},
        {"headline": ["Chance auf ueberdurch-", "schnittliche Wertentwicklung"],
         "body": ["Meine persoenliche Einschaetzung --", "keine Garantie, keine Prognose.",
                   "Ich sehe darin einen moeglichen", "Baustein fuer langfristiges Wachstum.",
                   "Wichtig ist mir dabei: kein Ersatz", "fuer breit gestreute Investments."]},
    ),
    (
        {"headline": ["Dezentral,", "nicht zensierbar"],
         "body": ["Keine zentrale Stelle kann", "Transaktionen verhindern oder",
                   "Konten einfrieren -- das Netzwerk", "laeuft unabhaengig von Behoerden.",
                   "Tausende Teilnehmer weltweit", "halten das System am Laufen."]},
        {"headline": ["Wertspeicher mit", "begrenztem Angebot"],
         "body": ["Nicht beliebig entwertbar --", "anders als bei unbegrenzter Geldmenge.",
                   "Das feste Angebot ist fuer mich", "ein interessanter Unterschied zu Fiat.",
                   "Ob das langfristig so bleibt,", "kann niemand mit Sicherheit sagen."]},
    ),
    (
        {"headline": ["Absolute Knappheit:", "21 Millionen Coins"],
         "body": ["Die Obergrenze steht im Code fest,", "niemand kann sie aendern.",
                   "Rund 94% der 21 Millionen Coins", "sind bereits im Umlauf.",
                   "Die letzten Coins werden erst", "um das Jahr 2140 geschuerft."]},
        {"headline": ["Baustein meiner", "Diversifikation"],
         "body": ["Ein gesunder Anteil neben", "anderen Anlageklassen.",
                   "Nicht mein groesster Posten,", "aber bewusst mit dabei.",
                   "Diversifikation heisst fuer mich:", "nicht alles auf eine Karte setzen."]},
    ),
    (
        {"headline": ["Nicht zentral", "ausweitbar (vs. Fiat)"],
         "body": ["Im Gegensatz zu Zentralbankgeld", "kann niemand einfach mehr drucken.",
                   "Die Geldpolitik ist im Protokoll", "festgelegt, nicht politisch steuerbar.",
                   "Das schafft fuer mich eine andere", "Art von Verlaesslichkeit."]},
        {"headline": ["Praktisch im", "Ernstfall"],
         "body": ["Vermoegen bleibt zugaenglich,", "selbst bei Zugriff auf anderes Vermoegen.",
                   "Ein Grund, warum ich es als", "eigene Anlageklasse betrachte.",
                   "Trotzdem bleibt es fuer mich", "nur ein Baustein, kein Ersatz."]},
    ),
    (
        {"headline": ["Portabel:", "12-24 Wörter im Kopf"],
         "body": ["Vermoegen laesst sich gedanklich", "ueber jede Landesgrenze bringen.",
                   "Nur die Merkliste im Kopf reicht,", "kein Bankkonto noetig.",
                   "Fuer mich ein echter Unterschied", "zu klassischem Vermoegen."]},
        {"headline": ["Fuer mich die", "relevanteste Kryptowaehrung"],
         "body": ["Deckt das Thema ab, ohne dass ich", "mich staendig damit beschaeftigen muss.",
                   "Fuer mich der einzige Krypto-Wert,", "den ich aktuell halte.",
                   "Ich beobachte das Thema, ohne", "staendig zu handeln oder zu traden."]},
    ),
]


def main():
    n = len(PAIRS) + 2
    build_intro().save(IG_DIR / "slide_1.png")
    for i, (his, mine) in enumerate(PAIRS, start=1):
        img = build_slide(n, i + 1, i, his, mine)
        img.save(IG_DIR / f"slide_{i + 1}.png")
    build_allocation_slide(n, n).save(IG_DIR / f"slide_{n}.png")

    for i in range(1, n + 1):
        src = Image.open(IG_DIR / f"slide_{i}.png")
        canvas = Image.new("RGB", B.STORY_SIZE, B.BG)
        x = (B.STORY_SIZE[0] - src.width) // 2
        y = (B.STORY_SIZE[1] - src.height) // 2
        canvas.paste(src, (x, y))
        canvas.save(TT_DIR / f"slide_{i}.png")

    cols = 3
    rows = (n + cols - 1) // cols
    gap = 20
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (245, 245, 245))
    for i in range(1, n + 1):
        im = Image.open(IG_DIR / f"slide_{i}.png")
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
