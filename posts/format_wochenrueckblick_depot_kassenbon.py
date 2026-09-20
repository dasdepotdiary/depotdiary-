"""Design-Alternative B fuer "Wochenrueckblick -- Mein Depot" (2026-09-20):
Kassenbon/Beleg-Optik, wie schon bei collab_finanzlehrer_aktien.py bewaehrt
(Monospace, gestrichelte Linien, Stempel-Grafik) -- hier als SOLO-Fassung
(kein Collab-Header) fuer den woechentlichen persoenlichen Depot-Rueckblick.

Design-Alternative A (Erklaerstueck-Optik ueber render.Post) liegt in
posts/format_wochenrueckblick_depot_v2.py -- beide werden dem Nutzer als
Vorschau geschickt, bevor eine davon gequeued wird.

Aufruf (Prototyp/Test):
  python posts/format_wochenrueckblick_depot_kassenbon.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
NAME = "format_wochenrueckblick_depot_kassenbon"
OUTPUT = ROOT / "output" / NAME
IG_DIR = OUTPUT / "posts_multi"
TT_DIR = OUTPUT / "tiktok_9x16"
IG_DIR.mkdir(parents=True, exist_ok=True)
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.FEED_SIZE

TABLE_BG = "#050504"
PAPER = "#211E19"
PAPER_SHADOW = "#141210"
INK = "#F2EFE8"
FAINT = "#9C948A"
DASH = "#4A453C"
GOLD = "#C9A24B"
GREEN_STAMP = "#7FBF9E"
RED_STAMP = "#D9776B"

MONO = str(ROOT / "assets" / "fonts" / "SpaceMono-Regular.ttf")
MONO_BOLD = str(ROOT / "assets" / "fonts" / "SpaceMono-Bold.ttf")

OWN_HANDLE = "@DASDEPOTDIARY"


def font(path, size):
    return ImageFont.truetype(path, size)


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


def dashed_line(draw, x1, x2, y, fill=DASH, dash=8, gap=6, width=2):
    x = x1
    while x < x2:
        draw.line([(x, y), (min(x + dash, x2), y)], fill=fill, width=width)
        x += dash + gap


def receipt_canvas():
    img = Image.new("RGB", (W, H), TABLE_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 30, W - 40, H - 30], fill=PAPER_SHADOW)
    draw.rectangle([30, 20, W - 50, H - 40], fill=PAPER)
    return img, draw


def draw_header(draw, title_lines, subtitle):
    y = 90
    f_brand = font(MONO_BOLD, 28)
    tw = draw.textlength(OWN_HANDLE, font=f_brand)
    draw.text((W / 2 - tw / 2, y), OWN_HANDLE, font=f_brand, fill=INK)
    y += 42
    f_small = font(MONO, 17)
    label = "WOCHENBELEG  //  MEIN DEPOT"
    tw = draw.textlength(label, font=f_small)
    draw.text((W / 2 - tw / 2, y), label, font=f_small, fill=FAINT)
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
        for line in wrap_mono(draw, subtitle, f_sub, W - 160):
            tw = draw.textlength(line, font=f_sub)
            draw.text((W / 2 - tw / 2, y), line, font=f_sub, fill=FAINT)
            y += 26
    y += 20
    dashed_line(draw, 80, W - 80, y)
    return y + 30


def draw_receipt_rows(draw, y, rows):
    row_font = font(MONO, 21)
    x_left, x_right = 80, W - 80
    for label, value in rows:
        vw = draw.textlength(value, font=row_font)
        name_max = x_right - x_left - vw - 20
        name_disp = label
        while draw.textlength(name_disp, font=row_font) > name_max and len(name_disp) > 3:
            name_disp = name_disp[:-1]
        if name_disp != label:
            name_disp = name_disp[:-1] + "."
        draw.text((x_left, y), name_disp, font=row_font, fill=INK)
        draw.text((x_right - vw, y), value, font=row_font, fill=GOLD)
        nw = draw.textlength(name_disp, font=row_font)
        dx = x_left + nw + 10
        while dx < x_right - vw - 10:
            draw.text((dx, y), ".", font=font(MONO, 21), fill=DASH)
            dx += 9
        y += 42
    return y


def draw_footer(draw, idx, n_total, note):
    y = H - 150
    dashed_line(draw, 80, W - 80, y)
    y += 24
    f = font(MONO, 16)
    for line in note:
        tw = draw.textlength(line, font=f)
        draw.text((W / 2 - tw / 2, y), line, font=f, fill=FAINT)
        y += 22
    y += 10
    page_text = f"BELEG {idx:02d}/{n_total:02d}"
    tw = draw.textlength(page_text, font=f)
    draw.text((W / 2 - tw / 2, y), page_text, font=f, fill=FAINT)


def stamp(img, cx, cy, text, color, angle=-12):
    stamp_font = font(MONO_BOLD, 28)
    tmp = Image.new("RGBA", (420, 100), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)
    tdraw.rounded_rectangle([4, 4, 416, 96], radius=14, outline=color, width=5)
    tw = tdraw.textlength(text, font=stamp_font)
    tdraw.text((210 - tw / 2, 34), text, font=stamp_font, fill=color)
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)


def slide_intro(date_label):
    img, draw = receipt_canvas()
    draw_header(draw, ["WOCHENRUECKBLICK", "MEIN DEPOT"], date_label)
    draw_footer(draw, 1, 4, ["KEINE ANLAGEBERATUNG -- NUR,", "WAS ICH SELBST GEMACHT HABE."])
    return img


def slide_performance(pct):
    img, draw = receipt_canvas()
    y = draw_header(draw, ["PERFORMANCE"], "Veraenderung meines Depots diese Woche.")
    y += 40
    color = GREEN_STAMP if pct >= 0 else RED_STAMP
    perf_font = font(MONO_BOLD, 96)
    text = f"{'+' if pct >= 0 else ''}{pct:.2f}".replace(".", ",") + "%"
    tw = draw.textlength(text, font=perf_font)
    draw.text((W / 2 - tw / 2, y), text, font=perf_font, fill=color)
    stamp(img, W / 2, y + 260, "DIESE WOCHE", color, angle=-8)
    draw_footer(draw, 2, 4, ["KEINE ANLAGEBERATUNG -- NUR,", "WAS ICH SELBST GEMACHT HABE."])
    return img


def slide_kaeufe(rows):
    img, draw = receipt_canvas()
    y = draw_header(draw, ["KAEUFE"], "Was diese Woche dazugekommen ist.")
    draw_receipt_rows(draw, y, rows)
    draw_footer(draw, 3, 4, ["KEINE ANLAGEBERATUNG -- NUR,", "WAS ICH SELBST GEMACHT HABE."])
    return img


def slide_verkaeufe():
    img, draw = receipt_canvas()
    y = draw_header(draw, ["VERKAEUFE"], "")
    y += 60
    f = font(MONO_BOLD, 30)
    text = "KEINE VERKAEUFE"
    tw = draw.textlength(text, font=f)
    draw.text((W / 2 - tw / 2, y), text, font=f, fill=INK)
    stamp(img, W / 2, y + 180, "0 TRADES", FAINT, angle=6)
    draw_footer(draw, 4, 4, ["KEINE ANLAGEBERATUNG -- NUR,", "WAS ICH SELBST GEMACHT HABE."])
    return img


def main(date_label, performance_pct, buys):
    slides = [
        slide_intro(date_label),
        slide_performance(performance_pct),
        slide_kaeufe(buys),
        slide_verkaeufe(),
    ]
    for i, img in enumerate(slides, start=1):
        img.save(IG_DIR / f"slide_{i}.png")
    n = len(slides)
    gap = 16
    sheet = Image.new("RGB", (W * n + gap * (n + 1), H + gap * 2), (10, 10, 10))
    for i, img in enumerate(slides, start=1):
        sheet.paste(img, (gap + (i - 1) * (W + gap), gap))
    sheet.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}, {n} Folien")


if __name__ == "__main__":
    buys = [
        ("Sparplan", "regulaer"),
        ("Broadcom (AVGO)", "297 USD"),
        ("Vistra (VST)", "301 USD"),
        ("Uber (UBER)", "400 USD*"),
    ]
    main("20.09.2026  *letzte Woche gekauft", 1.61, buys)
