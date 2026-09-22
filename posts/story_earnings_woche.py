"""Woechentliches Story-Format "EARNINGS-WOCHE" -- alle Berichtstermine der
Woche auf EINER Slide (Nutzerwunsch 2026-09-22: "alle infos auf eine slide
und als story", kein mehrseitiges Karussell mehr fuer dieses Format).
Layout/Aufbau uebernommen von story_tagesereignisse.py (nummerierte Liste,
Zeitungs-Masthead), nur Titel und Inhalt sind Earnings-spezifisch.

Input: Liste von Dicts mit headline, body (1-2 Saetze, reine Fakten,
keine Kursziele/Bewertungen).

Aufruf:
  python posts/story_earnings_woche.py <post_name>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from story_aktiencheck import font

ROOT = Path(__file__).parent.parent

W, H = B.STORY_SIZE
BG = "#F2F0EA"
INK = B.INK
SUBTEXT = B.SUBTEXT
DIVIDER = B.DIVIDER
ACCENT = B.GREEN
MASTHEAD_H = 340
INK_DARK = "#16181C"


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_masthead(img):
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, MASTHEAD_H], fill=INK_DARK)
    return draw


def draw_header(draw, y, date_label):
    eyebrow_font = font(B.SANS_BOLD, 18)
    draw.text((B.MARGIN_LEFT, y), "@DASDEPOTDIARY  —  " + date_label, font=eyebrow_font, fill="#9B9587")
    y += 44
    title_font = font(B.SERIF_BOLD, 56)
    draw.text((B.MARGIN_LEFT, y), "Earnings-Woche.", font=title_font, fill="#F5F2EA")
    y += 78
    draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=ACCENT)
    return y + 46


def draw_event_entry(draw, x, y, w, num, event):
    num_font = font(B.SERIF_BOLD, 40)
    num_text = f"{num:02d}"
    draw.text((x, y), num_text, font=num_font, fill=ACCENT)
    nw = draw.textlength(num_text, font=num_font)
    text_x = x + nw + 32

    headline_font = font(B.SANS_BOLD, 25)
    body_font = font(B.SANS_BOLD, 19)
    headline_lines = wrap_text(draw, event["headline"], headline_font, w - nw - 32)
    body_lines = wrap_text(draw, event["body"], body_font, w - nw - 32)

    ty = y - 2
    for line in headline_lines:
        draw.text((text_x, ty), line, font=headline_font, fill=INK)
        ty += 32
    ty += 8
    for line in body_lines:
        draw.text((text_x, ty), line, font=body_font, fill=SUBTEXT)
        ty += 26

    entry_h = max(48, ty - y)
    return entry_h


def slide_earnings_woche(events, date_label):
    img = Image.new("RGB", (W, H), BG)
    draw = draw_masthead(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=ACCENT)

    header_end_y = draw_header(draw, 56, date_label)
    header_end_y = max(header_end_y, MASTHEAD_H + 40)
    entry_gap = 40
    content_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    heights = []
    tmp = Image.new("RGB", (10, 10))
    tmp_draw = ImageDraw.Draw(tmp)
    for i, event in enumerate(events, 1):
        num_font = font(B.SERIF_BOLD, 40)
        nw = tmp_draw.textlength(f"{i:02d}", font=num_font)
        headline_lines = wrap_text(tmp_draw, event["headline"], font(B.SANS_BOLD, 25), content_w - nw - 32)
        body_lines = wrap_text(tmp_draw, event["body"], font(B.SANS_BOLD, 19), content_w - nw - 32)
        heights.append(max(48, len(headline_lines) * 32 + 8 + len(body_lines) * 26))
    block_h = sum(heights) + entry_gap * (len(events) - 1)
    footer_top = H - 140
    y = header_end_y + max(20, (footer_top - header_end_y - block_h) // 2)
    for i, event in enumerate(events, 1):
        entry_h = draw_event_entry(draw, B.MARGIN_LEFT, y, content_w, i, event)
        y += entry_h + entry_gap / 2
        if i < len(events):
            draw.line([(B.MARGIN_LEFT, y), (W - B.MARGIN_RIGHT, y)], fill=DIVIDER, width=1)
        y += entry_gap / 2

    text = "Keine Anlageberatung -- nur Zahlen/Fakten, die ich mir angeschaut habe."
    disclaimer_font = font(B.SANS_BOLD, 18)
    draw.line([(B.MARGIN_LEFT, H - 90), (W - B.MARGIN_RIGHT, H - 90)], fill=DIVIDER, width=1)
    draw.text((B.MARGIN_LEFT, H - 68), text, font=disclaimer_font, fill=SUBTEXT)

    return img


EVENTS = [
    {"headline": "General Mills -- Mittwoch, 23.9., vor US-Boersenoeffnung.",
     "body": "Kurs 35,41 USD (21.9.), Marktkap. 18,9 Mrd. USD. Analysten rechnen mit rund 0,72 USD Gewinn je Aktie."},
    {"headline": "Cracker Barrel -- Mittwoch, 23.9., vor US-Boersenoeffnung.",
     "body": "Kurs 44,87 USD (21.9.), Marktkap. 1,0 Mrd. USD. Analysten rechnen mit rund 0,20 USD Gewinn je Aktie."},
    {"headline": "Costco -- Donnerstag, 24.9., nach US-Boersenschluss.",
     "body": "Kurs 898,48 USD (21.9.), Marktkap. 420,3 Mrd. USD. Analysten rechnen mit rund 6,48 USD Gewinn je Aktie."},
]


def main():
    post_name = sys.argv[1] if len(sys.argv) > 1 else "earnings_woche_2026-09-21"
    date_label = sys.argv[2] if len(sys.argv) > 2 else "21.09.2026"
    output = ROOT / "output" / post_name
    tt_dir = output / "tiktok_9x16"
    tt_dir.mkdir(parents=True, exist_ok=True)

    img = slide_earnings_woche(EVENTS, date_label)
    img.save(tt_dir / "slide_1.png")
    img.save(output / "uebersicht.png")
    print(f"Fertig: {output / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
