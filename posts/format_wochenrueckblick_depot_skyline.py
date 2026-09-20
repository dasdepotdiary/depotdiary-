"""Design-Alternative C fuer "Wochenrueckblick -- Mein Depot" (2026-09-20,
Nutzerwunsch): helles Tages-Skyline-Foto als Hintergrund (assets/
skyline_day_still.png -- bisher fuer Tagesereignisse getestet und dort
verworfen, laut Memory "fuer ein anderes Format aufheben"). Fuenf Slides,
alle Infos (Performance, Kaeufe, Verkaeufe) + eine Engagement-Slide
(Like/Kommentar/Teilen, wie beim Deep-Dive-Format).

Lesbarkeit: dunkle halbtransparente Karten ueber dem Foto (wie schon bei
story_damals_investiert.py bewaehrt) statt eines duennen Verlaufs-Scrims,
der bei einem detailreichen Foto zuvor nicht ausreichte.

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
MUTED = "#5A564C"
GOLD = "#B08A2E"
GREEN = "#1A4D3C"
RED = "#C0392B"
CARD = (16, 16, 14, 168)
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
    # dezente helle Vignette oben/unten, damit Header/Footer-Text immer
    # lesbar bleibt, auch ausserhalb der dunklen Info-Karten
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
    draw.text((W / 2 - tw / 2, H - 56), text, font=disclaimer_font, fill=MUTED)
    page_font = font(B.SANS_BOLD, 18)
    page_text = f"{idx:02d} / {n_total:02d}"
    pw = draw.textlength(page_text, font=page_font)
    draw.text((W - B.MARGIN_RIGHT - pw, 56), page_text, font=page_font, fill=INK)


def slide_intro(date_label):
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

    footer(draw, 1, 5)
    return img


def slide_performance(pct):
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
    sub_lines = wrap_text(draw, "So hat sich mein Depot diese Woche entwickelt -- reine Prozentangabe.",
                           sub_font, cw - 80)
    sy = cy + 220
    for line in sub_lines:
        draw.text((cx + 40, sy), line, font=sub_font, fill=CREAM)
        sy += 30

    footer(draw, 2, 5)
    return img


def slide_kaeufe(rows):
    img = skyline_background()
    draw = ImageDraw.Draw(img)
    header(draw)

    row_h, gap = 88, 14
    ch = 70 + len(rows) * (row_h + gap)
    cx, cy, cw = 60, 400, W - 120
    card(img, draw, cx, cy, cw, ch)
    label_font = font(B.SANS_BOLD, 22)
    draw.text((cx + 40, cy + 30), "KÄUFE DIESE WOCHE", font=label_font, fill=GOLD)

    y = cy + 74
    for r in rows:
        draw.rounded_rectangle([cx + 30, y, cx + cw - 30, y + row_h], radius=14,
                                outline=CARD_BORDER, width=1)
        name_font = font(B.SANS_BOLD, 26)
        draw.text((cx + 54, y + 14), r["label"], font=name_font, fill=CREAM)
        note_font = font(B.SANS_BOLD, 17)
        draw.text((cx + 54, y + 50), r["note"], font=note_font, fill="#C9C4B6")
        if r.get("price"):
            price_font = font(B.SANS_BOLD, 24)
            pw = draw.textlength(r["price"], font=price_font)
            draw.text((cx + cw - 60 - pw, y + 30), r["price"], font=price_font, fill=GOLD)
        y += row_h + gap

    footer(draw, 3, 5)
    return img


def slide_verkaeufe(sells):
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

    footer(draw, 4, 5)
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


def slide_engagement():
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
        draw.text((cx + 40, ty), line, font=sub_font, fill="#C9C4B6")
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

    footer(draw, 5, 5)
    return img


def main(date_label, performance_pct, buys, sells):
    slides = [
        slide_intro(date_label),
        slide_performance(performance_pct),
        slide_kaeufe(buys),
        slide_verkaeufe(sells),
        slide_engagement(),
    ]
    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")
    n = len(slides)
    gap = 16
    sheet = Image.new("RGB", (W * n + gap * (n + 1), H + gap * 2), (240, 238, 232))
    for i, img in enumerate(slides, start=1):
        sheet.paste(img, (gap + (i - 1) * (W + gap), gap))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    buys = [
        {"label": "Sparplan", "note": "Wie jeden Monat -- automatische Ausführung.", "price": ""},
        {"label": "Broadcom (AVGO)", "note": "Einzelkauf diesen Monat.", "price": "297 USD"},
        {"label": "Vistra (VST)", "note": "Einzelkauf diesen Monat.", "price": "301 USD"},
        {"label": "Uber (UBER)", "note": "Bereits letzte Woche gekauft.", "price": "400 USD"},
    ]
    main("20.09.2026", 1.61, buys, sells=[])
