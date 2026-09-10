"""Neues Format "Depot-Ranking" (2026-09-10) -- Nutzer-Idee als Reaktion auf
die Frage nach Formaten, die tatsaechlich Reichweite bringen (nicht nur
Vertrauen bei bestehenden Followern): 4-5 FIKTIVE Beispiel-Depots werden
strukturell in eine Tier-Liste (S/A/B/C/F) einsortiert.

WICHTIG (Compliance): Bewertet wird ausschliesslich die STRUKTUR
(Diversifikation, Konzentrationsrisiko, Ueberschneidung) -- nie, ob
einzelne Aktien/Anlagen an sich gut oder schlecht sind. Alle Depots sind
erfunden (keine echten Personen, keine echten Positionsgroessen). Spaeter
denkbar: echte, von Followern freiwillig eingeschickte Depots -- dann nur
anonymisiert und weiterhin nur strukturell bewertet.

Aufruf:
  python posts/format_depotranking.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
import voiceover

ROOT = Path(__file__).parent.parent
NAME = "format_depotranking"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "instagram_4x5"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (26, 29, 36)
BG_BOTTOM = (13, 15, 20)
CREAM = "#F2F0EA"
MUTED = "#9B9BA8"
CARD = "#23262F"
CARD_BORDER = "#3A3E4A"

TIER_COLORS = {
    "S": "#F5C518", "A": "#4ADE80", "B": "#60A5FA", "C": "#F5A623", "F": "#E5484D",
}
TIER_LABELS = {
    "S": "MEISTERKLASSE", "A": "SOLIDE", "B": "OKAY, MIT SCHWAECHE",
    "C": "RISKANT", "F": "CHAOS",
}

OWN_HANDLE = "@DASDEPOTDIARY"

DEPOTS = [
    {
        "label": "DEPOT A",
        "allocation": ["95% eine einzelne Tech-Aktie", "5% Cash"],
        "tier": "F",
        "why": "Extreme Konzentration auf eine einzige Position -- faellt diese Aktie stark, faellt praktisch das ganze Depot mit.",
    },
    {
        "label": "DEPOT B",
        "allocation": ["70% Bitcoin", "20% eine Einzelaktie", "10% Cash"],
        "tier": "C",
        "why": "Zwei sehr unterschiedliche Risiken (Krypto + Einzelaktie), aber keine breite Streuung -- beide Positionen koennen gleichzeitig stark schwanken.",
    },
    {
        "label": "DEPOT C",
        "allocation": ["12 Einzelaktien", "alle aus dem gleichen Sektor"],
        "tier": "B",
        "why": "Wirkt auf den ersten Blick breit gestreut (12 Positionen!) -- ist es aber nicht, wenn alle am selben Branchenrisiko haengen.",
    },
    {
        "label": "DEPOT D",
        "allocation": ["8 verschiedene ETFs", "90% davon ueberschneiden sich (US-Tech-lastig)"],
        "tier": "B",
        "why": "Viele Fondsnamen taeuschen Streuung vor -- schaut man in die Holdings, stecken oft dieselben 10-15 Aktien in fast jedem ETF.",
    },
    {
        "label": "DEPOT E",
        "allocation": ["60% breiter Welt-ETF", "20% Einzelaktien", "15% Anleihen", "5% Cash"],
        "tier": "A",
        "why": "Breite Basis durch den Welt-ETF, Einzelaktien als bewusste Beimischung, Anleihen zur Abfederung -- strukturell solide aufgestellt.",
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


def add_radial_glow(img, cx, cy, radius, color, strength=60):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def base_slide(glow_color=(60, 60, 80)):
    img = gradient_background(BG_TOP, BG_BOTTOM)
    add_radial_glow(img, W // 2, H * 0.15, 500, glow_color, strength=50)
    return img, ImageDraw.Draw(img)


def build_header(draw, y=60):
    handle_font = font(B.SANS_BOLD, 24)
    tw = draw.textlength(OWN_HANDLE, font=handle_font)
    draw.text((W / 2 - tw / 2, y), OWN_HANDLE, font=handle_font, fill=MUTED)
    return y + 50


def footer_disclaimer(draw):
    note_font = font(B.SANS_BOLD, 20)
    note = "Alle Depots frei erfunden -- bewertet wird nur die Struktur, keine Anlageberatung."
    lines = wrap_text(draw, note, note_font, W - 140)
    ny = H - 30 - len(lines) * 26
    for line in lines:
        tw = draw.textlength(line, font=note_font)
        draw.text((W / 2 - tw / 2, ny), line, font=note_font, fill=MUTED)
        ny += 26


def slide_intro():
    img, draw = base_slide()
    build_header(draw)

    y = H * 0.26
    label_font = font(B.SANS_BOLD, 28)
    label = "DEPOT-RANKING"
    tw = draw.textlength(label, font=label_font)
    draw.text((W / 2 - tw / 2, y), label, font=label_font, fill=TIER_COLORS["S"])
    y += 62

    title_font = font(B.SANS_BOLD, 58)
    for line in ["5 ERFUNDENE DEPOTS.", "VON CHAOS BIS", "MEISTERKLASSE."]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 66

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    sub_lines = wrap_text(draw, "Wo waere deins? Rein strukturell bewertet.", sub_font, W - 160)
    for line in sub_lines:
        tw = draw.textlength(line, font=sub_font)
        draw.text((W / 2 - tw / 2, y), line, font=sub_font, fill=MUTED)
        y += 40

    # Tier-Skala als Vorschau -- macht das Ranking-Konzept sofort lesbar
    y += 50
    scale_font = font(B.SANS_BOLD, 30)
    x = 100
    for tier in ["S", "A", "B", "C", "F"]:
        color = TIER_COLORS[tier]
        draw.rounded_rectangle([x, y, x + 64, y + 64], radius=14, fill=color)
        tw = draw.textlength(tier, font=scale_font)
        draw.text((x + 32 - tw / 2, y + 32 - 18), tier, font=scale_font, fill="#14151A")
        x += 90

    footer_disclaimer(draw)
    return img


def slide_depot(idx, depot, n_total):
    img, draw = base_slide(glow_color=tuple(int(TIER_COLORS[depot["tier"]][i:i+2], 16) for i in (1, 3, 5)))
    y = build_header(draw)

    badge_font = font(B.SANS_BOLD, 26)
    badge = f"{depot['label']}  --  {idx} / {n_total}"
    tw = draw.textlength(badge, font=badge_font)
    draw.text((W / 2 - tw / 2, y), badge, font=badge_font, fill=MUTED)
    y += 70

    alloc_font = font(B.SANS_BOLD, 34)
    card_top = y
    line_h = 46
    card_h = len(depot["allocation"]) * line_h + 60
    draw.rounded_rectangle([80, card_top, W - 80, card_top + card_h], radius=24, fill=CARD, outline=CARD_BORDER, width=2)
    ty = card_top + 30
    for line in depot["allocation"]:
        tw = draw.textlength(line, font=alloc_font)
        draw.text((W / 2 - tw / 2, ty), line, font=alloc_font, fill=CREAM)
        ty += line_h
    y = card_top + card_h + 50

    # Tier-Badge -- grosse farbige Kachel, zentrales Reveal-Element
    tier = depot["tier"]
    color = TIER_COLORS[tier]
    badge_size = 140
    bx = W / 2 - badge_size / 2
    draw.rounded_rectangle([bx, y, bx + badge_size, y + badge_size], radius=28, fill=color)
    tier_font = font(B.SANS_BOLD, 84)
    tw = draw.textlength(tier, font=tier_font)
    draw.text((W / 2 - tw / 2, y + badge_size / 2 - 50), tier, font=tier_font, fill="#14151A")
    y += badge_size + 20

    tier_label_font = font(B.SANS_BOLD, 26)
    label_text = TIER_LABELS[tier]
    tw = draw.textlength(label_text, font=tier_label_font)
    draw.text((W / 2 - tw / 2, y), label_text, font=tier_label_font, fill=color)
    y += 60

    why_font = font(B.SANS_BOLD, 28)
    why_lines = wrap_text(draw, depot["why"], why_font, W - 180)
    for line in why_lines:
        tw = draw.textlength(line, font=why_font)
        draw.text((W / 2 - tw / 2, y), line, font=why_font, fill=CREAM)
        y += 38

    footer_disclaimer(draw)
    return img


def slide_outro():
    img, draw = base_slide()
    y = build_header(draw)
    y += 100

    title_font = font(B.SANS_BOLD, 52)
    for line in ["WELCHES DEPOT", "WAER DEINS?"]:
        tw = draw.textlength(line, font=title_font)
        draw.text((W / 2 - tw / 2, y), line, font=title_font, fill=CREAM)
        y += 62

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    sub = "Schreib's in die Kommentare."
    tw = draw.textlength(sub, font=sub_font)
    draw.text((W / 2 - tw / 2, y), sub, font=sub_font, fill=TIER_COLORS["S"])

    footer_disclaimer(draw)
    return img


def main():
    slides = [slide_intro]
    n = len(DEPOTS)
    for i, depot in enumerate(DEPOTS, start=1):
        slides.append(lambda i=i, depot=depot: slide_depot(i, depot, n))
    slides.append(slide_outro)

    for i, fn in enumerate(slides, start=1):
        img = fn()
        img.save(TT_DIR / f"slide_{i}.png")
        feed_w, feed_h = B.FEED_SIZE
        crop_h = int(feed_w * H / W)
        top = max(0, (H - crop_h) // 3)
        cropped = img.crop((0, top, W, min(H, top + crop_h))).resize((feed_w, feed_h))
        cropped.save(IG_DIR / f"slide_{i}.png")

    total = len(slides)
    cols = 4
    rows = (total + cols - 1) // cols
    gap = 16
    tw, th = W // 3, H // 3
    sheet = Image.new("RGB", (tw * cols + gap * (cols + 1), th * rows + gap * (rows + 1)), (16, 17, 22))
    for i in range(1, total + 1):
        im = Image.open(TT_DIR / f"slide_{i}.png").resize((tw, th))
        r, c = divmod(i - 1, cols)
        sheet.paste(im, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {total} Folien")

    # Allokation wird NICHT vorgelesen (steht gut lesbar auf der Karte) --
    # nur Tier + kurze Begruendung, haelt die Laenge im Zielkorridor statt
    # bei ueber 70s wie in der ersten Fassung mit voller Allokations-Ansage.
    sentences = ["Depot-Ranking: fuenf erfundene Depots, von Chaos bis Meisterklasse. Wo waere deins?"]
    for depot in DEPOTS:
        sentences.append(f"{depot['label']}: Tier {depot['tier']} -- {TIER_LABELS[depot['tier']]}. {depot['why']}")
    sentences.append("Welches Depot waer deins? Schreib's in die Kommentare und folge fuer mehr Rankings.")

    voiceover.write(NAME, sentences, output_root=ROOT / "output")
    print(f"Voiceover-Skript geschrieben: output/{NAME}/script.md + timing.json")


if __name__ == "__main__":
    main()
