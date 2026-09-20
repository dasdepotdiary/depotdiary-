"""Design-Alternative C fuer "Wochenrueckblick -- Mein Depot", v2
(2026-09-20, Nutzer-Feedback zu v1: "Hintergrund ist schoen, aber das
Design ist extrem schlecht -- Kaeufe separat auf einer Seite mit Logo,
jeden einzelnen Kauf einzeln"): helles Tages-Skyline-Foto als Hintergrund
bleibt (assets/skyline_day_still.png), aber JEDER Kauf bekommt jetzt eine
eigene volle Slide mit Firmenlogo (wie personal_portfolio_update.py/
personal_deep_dive*.py), der Sparplan einmal als eigene Uebersichts-Slide
ohne Logo (kein einzelnes Wertpapier).

Aufruf (Prototyp/Test):
  python posts/format_wochenrueckblick_depot_skyline.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "format_wochenrueckblick_depot_skyline"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "posts_multi"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

INK = "#16181C"
CREAM = "#F2F0EA"
MUTED_LIGHT = "#C9C4B6"
GOLD = "#B08A2E"
CARD = (16, 16, 14, 172)
CARD_BORDER = "#D8D2C2"

OWN_HANDLE = "@DASDEPOTDIARY"


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


def skyline_background():
    photo = Image.open(ROOT / "assets" / "skyline_day_still.png").convert("RGB")
    photo = photo.resize((W, H)) if photo.size != (W, H) else photo
    img = ImageEnhance.Brightness(photo).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, W, 170], fill=90)
    vdraw.rectangle([0, H - 140, W, H], fill=110)
    vignette = vignette.filter(ImageFilter.GaussianBlur(70))
    white = Image.new("RGB", (W, H), (245, 243, 236))
    img = Image.composite(white, img, vignette)
    return img


def card(img, draw, x, y, w, h, radius=20):
    overlay = Image.new("RGBA", (w, h), CARD)
    img.paste(overlay, (x, y), overlay)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=CARD_BORDER, width=1)


def header(draw, y=56):
    handle_font = font(B.SANS_BOLD, 20)
    draw.text((B.MARGIN_LEFT, y), OWN_HANDLE, font=handle_font, fill=INK)
    return y + 32


def footer(draw, idx, n_total):
    disclaimer_font = font(B.SANS_BOLD, 18)
    text = "Keine Anlageberatung -- nur, was ich selbst gemacht habe."
    tw = draw.textlength(text, font=disclaimer_font)
    draw.text((W / 2 - tw / 2, H - 56), text, font=disclaimer_font, fill=INK)
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, 56), page_text, font=page_font, fill=INK)


def draw_logo_circle(img, draw, cx, cy, r, logo_path):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFFFFF", outline=GOLD, width=3)
    logo = Image.open(logo_path).convert("RGBA")
    target = int(r * 1.5)
    ratio = min(target / logo.width, target / logo.height)
    logo = logo.resize((max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio))))
    img.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def slide_intro(date_label, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 640, W - 120, 300
    card(img, draw, cx, cy, cw, ch)
    ty = cy + 40
    title_font = font(B.SERIF_BOLD, 52)
    for line in ["Wochenrückblick", "— Mein Depot."]:
        draw.text((cx + 40, ty), line, font=title_font, fill=CREAM)
        ty += 62
    ty += 10
    sub_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, ty), date_label, font=sub_font, fill=GOLD)

    footer(draw, 1, n_total)
    return img


def slide_performance(pct, idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 700, W - 120, 340
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 32), "PERFORMANCE DIESER WOCHE", font=label_font, fill=GOLD)

    color = "#7FBF9E" if pct >= 0 else "#D9776B"
    perf_font = font(B.SERIF_BOLD, 96)
    text = f"{'+' if pct >= 0 else ''}{pct:.2f}".replace(".", ",") + " %"
    draw.text((cx + 40, cy + 80), text, font=perf_font, fill=color)

    sub_font = font(B.SANS_BOLD, 24)
    sy = cy + 220
    for line in wrap_text(draw, "So hat sich mein Depot diese Woche entwickelt -- reine Prozentangabe.",
                           sub_font, cw - 80):
        draw.text((cx + 40, sy), line, font=sub_font, fill=MUTED_LIGHT)
        sy += 30

    footer(draw, idx, n_total)
    return img


def slide_sparplan(idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 620, W - 120, 340
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 32), "KAUF 1 VON 5", font=label_font, fill=GOLD)

    title_font = font(B.SERIF_BOLD, 44)
    draw.text((cx + 40, cy + 80), "Mein Sparplan.", font=title_font, fill=CREAM)

    sub_font = font(B.SANS_BOLD, 24)
    sy = cy + 150
    for line in wrap_text(draw, "Wie jeden Monat -- automatische Ausfuehrung, unabhaengig von "
                                 "Kurs oder Tagesform. Laeuft im Hintergrund weiter, ohne dass "
                                 "ich manuell eingreife.", sub_font, cw - 80):
        draw.text((cx + 40, sy), line, font=sub_font, fill=MUTED_LIGHT)
        sy += 32

    footer(draw, idx, n_total)
    return img


def slide_position(pos, kauf_nr, idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 560, W - 120, 400
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 32), f"KAUF {kauf_nr} VON 5", font=label_font, fill=GOLD)

    logo_r = 56
    logo_cx, logo_cy = cx + 40 + logo_r, cy + 100 + logo_r
    draw_logo_circle(img, draw, logo_cx, logo_cy, logo_r, pos["logo_path"])
    draw = ImageDraw.Draw(img)

    name_x = logo_cx + logo_r + 24
    name_font = font(B.SANS_BOLD, 32)
    draw.text((name_x, logo_cy - 30), pos["name"], font=name_font, fill=CREAM)
    ticker_font = font(B.SANS_BOLD, 19)
    draw.text((name_x, logo_cy + 8), pos["ticker"], font=ticker_font, fill=GOLD)

    y = logo_cy + logo_r + 40
    price_font = font(B.SERIF_BOLD, 56)
    draw.text((cx + 40, y), pos["price"], font=price_font, fill=CREAM)
    y += 74
    note_font = font(B.SANS_BOLD, 22)
    for line in wrap_text(draw, pos["note"], note_font, cw - 80):
        draw.text((cx + 40, y), line, font=note_font, fill=MUTED_LIGHT)
        y += 30

    footer(draw, idx, n_total)
    return img


def slide_verkaeufe(sells, idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 760, W - 120, 220
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 30), "VERKÄUFE", font=label_font, fill=GOLD)
    text_font = font(B.SANS_BOLD, 30)
    text = "Keine Verkäufe diese Woche." if not sells else ", ".join(sells)
    for line in wrap_text(draw, text, text_font, cw - 80):
        draw.text((cx + 40, cy + 84), line, font=text_font, fill=CREAM)

    footer(draw, idx, n_total)
    return img


def draw_heart_icon(draw, cx, cy, size, color):
    r = size * 0.28
    draw.ellipse([cx - size * 0.5, cy - size * 0.28, cx - size * 0.5 + 2 * r, cy - size * 0.28 + 2 * r], fill=color)
    draw.ellipse([cx, cy - size * 0.28, cx + 2 * r, cy - size * 0.28 + 2 * r], fill=color)
    draw.polygon([(cx - size * 0.5, cy), (cx + size * 0.5, cy), (cx, cy + size * 0.55)], fill=color)


def draw_comment_icon(draw, cx, cy, size, color):
    draw.rounded_rectangle([cx - size * 0.55, cy - size * 0.4, cx + size * 0.55, cy + size * 0.35],
                            radius=size * 0.18, outline=color, width=max(3, int(size * 0.09)))
    draw.polygon([(cx - size * 0.15, cy + size * 0.3), (cx + size * 0.1, cy + size * 0.3),
                  (cx - size * 0.2, cy + size * 0.62)], fill=color)


def draw_share_icon(draw, cx, cy, size, color):
    w = max(3, int(size * 0.1))
    draw.line([(cx - size * 0.5, cy + size * 0.35), (cx - size * 0.5, cy - size * 0.15),
               (cx + size * 0.5, cy - size * 0.15)], fill=color, width=w, joint="curve")
    draw.polygon([(cx + size * 0.5, cy - size * 0.42), (cx + size * 0.5, cy + size * 0.12),
                  (cx + size * 0.82, cy - size * 0.15)], fill=color)


def slide_engagement(idx, n_total):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    cx, cy, cw, ch = 60, 520, W - 120, 560
    card(img, draw, cx, cy, cw, ch)

    title_font = font(B.SERIF_BOLD, 38)
    ty = cy + 46
    for line in ["Gefällt dir dieses", "Format?"]:
        draw.text((cx + 40, ty), line, font=title_font, fill=CREAM)
        ty += 48
    ty += 10
    sub_font = font(B.SANS_BOLD, 22)
    for line in wrap_text(draw, "Dann liken, kommentieren und teilen -- hilft dem Account wirklich weiter.",
                           sub_font, cw - 80):
        draw.text((cx + 40, ty), line, font=sub_font, fill=MUTED_LIGHT)
        ty += 30

    icon_size = 70
    gap = 118
    total_w = 3 * icon_size + 2 * (gap - icon_size)
    start_x = cx + cw / 2 - total_w / 2 + icon_size / 2
    icon_y = ty + 70
    draw_heart_icon(draw, start_x, icon_y, icon_size, GOLD)
    draw_comment_icon(draw, start_x + gap, icon_y, icon_size, GOLD)
    draw_share_icon(draw, start_x + 2 * gap, icon_y, icon_size, GOLD)
    label_font = font(B.SANS_BOLD, 16)
    for i, label in enumerate(["LIKE", "KOMMENTAR", "TEILEN"]):
        lw = draw.textlength(label, font=label_font)
        draw.text((start_x + i * gap - lw / 2, icon_y + icon_size / 2 + 22), label, font=label_font, fill=CREAM)

    footer(draw, idx, n_total)
    return img


def main(date_label, performance_pct, positions, sells):
    # Gesamtzahl: Intro(1) + Performance(1) + je Position(len, inkl. Sparplan) + Verkaeufe(1) + Engagement(1)
    total = 2 + len(positions) + 1 + 1
    slides = [slide_intro(date_label, total)]
    slides.append(slide_performance(performance_pct, 2, total))
    kauf_nr = 1
    for i, pos in enumerate(positions, start=3):
        if pos.get("is_sparplan"):
            slides.append(slide_sparplan(i, total))
        else:
            slides.append(slide_position(pos, kauf_nr, i, total))
        kauf_nr += 1
    slides.append(slide_verkaeufe(sells, len(positions) + 3, total))
    slides.append(slide_engagement(len(positions) + 4, total))

    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")
    n = len(slides)
    gap = 16
    cols = 5
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols + gap * (cols + 1), H * rows + gap * (rows + 1)), (240, 238, 232))
    for i, img in enumerate(slides, start=1):
        r, c = divmod(i - 1, cols)
        sheet.paste(img, (gap + c * (W + gap), gap + r * (H + gap)))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    positions = [
        {"is_sparplan": True},
        {"name": "Broadcom", "ticker": "AVGO", "price": "297 EUR",
         "note": "Einzelkauf diesen Monat.", "logo_path": ROOT / "assets" / "avgo_logo_icon.png"},
        {"name": "Vistra", "ticker": "VST", "price": "301 EUR",
         "note": "Einzelkauf diesen Monat.", "logo_path": ROOT / "assets" / "vst_logo_icon.png"},
        {"name": "Uber", "ticker": "UBER", "price": "400 EUR",
         "note": "Bereits letzte Woche gekauft.", "logo_path": ROOT / "assets" / "uber_logo_icon.png"},
        {"name": "Bitcoin", "ticker": "BTC", "price": "64.000 EUR",
         "note": "Einzelkauf diesen Monat.", "logo_path": ROOT / "assets" / "btc_logo_icon.png"},
    ]
    main("20.09.2026", 1.61, positions, sells=[])
