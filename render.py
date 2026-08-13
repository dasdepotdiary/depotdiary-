"""Render-Engine fuer depotdiary Slides (siehe CLAUDE.md / PROMPTS.md Prompt 1).

Nutzung:
    from render import Post

    post = Post("post05_positionen", total_slides=6)
    post.slide_hook("ERKLAERSTUECK", "Was eine *Position* wirklich ist.", "Eine kurze Einordnung.")
    post.slide_text("ERKLAERSTUECK", "Warum ich das *so* sehe.", "Fliesstext ueber mehrere Zeilen ...")
    post.slide_rows("DEPOT-UPDATE", "Meine *Allokation*.", [
        ("Einzelaktien", "42%", brand.INK),
        ("ETFs & Fonds", "31%", brand.INK),
        ("Bitcoin & BTC-Treasuries", "18%", brand.GREEN),
        ("Gold & Silber", "9%", brand.OCHRE),
    ], "Ohne Cash gerechnet.")
    post.slide_cta("DEPOT-UPDATE", "Bis *naechsten* Monat.", "Ich zeig dir, was sich veraendert hat.")
    post.export()

Jeder Post wird automatisch in beiden Formaten exportiert:
    output/<name>/instagram_4x5/slide_1.png ...
    output/<name>/tiktok_9x16/slide_1.png ...
plus output/<name>/uebersicht.png als Kontaktabzug.
"""

from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

import brand as B

OUTPUT = Path(__file__).parent / "output"

LINE_SPACING = 14
BLOCK_GAP = 28

_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def _text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> float:
    if not text:
        return 0
    return draw.textlength(text, font=font)


def _line_height(font: ImageFont.FreeTypeFont) -> int:
    ascent, descent = font.getmetrics()
    return ascent + descent


def _draw_tracked(draw, xy, text, font, fill, tracking):
    """Zeichnet Text mit fester Buchstaben-Sperrung (fuer Eyebrow/Wordmark)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += _text_w(draw, ch, font) + tracking
    return x


def _tracked_width(draw, text, font, tracking):
    if not text:
        return 0
    w = sum(_text_w(draw, ch, font) for ch in text)
    return w + tracking * (len(text) - 1)


# --- *wort*-Markup: kursiv + gruen ---
_MARKUP_RE = re.compile(r"\*([^*]+)\*")


def _parse_markup(text):
    """['normal ', ('wort', italic), ' normal'] -> [(text, italic)]"""
    segments = []
    pos = 0
    for m in _MARKUP_RE.finditer(text):
        if m.start() > pos:
            segments.append((text[pos:m.start()], False))
        segments.append((m.group(1), True))
        pos = m.end()
    if pos < len(text):
        segments.append((text[pos:], False))
    return segments


_NO_SPACE_BEFORE = set(".,!?:;")


def _wrap_markup(draw, text, font_regular_path, font_italic_path, size, max_width,
                  max_lines=None, min_size=24, step=4):
    """Bricht Text (mit optionalem *wort*-Markup) auf max_width um.

    Reduziert die Schriftgroesse automatisch, wenn max_lines ueberschritten wird.
    Gibt (lines, size) zurueck; lines = Liste von Zeilen, Zeile = Liste von
    (text, italic) Woertern in Reihenfolge.
    """
    segments = _parse_markup(text)
    tokens = []  # (word, italic, glued_to_prev)
    for seg_text, italic in segments:
        parts = seg_text.split(" ")
        for i, part in enumerate(parts):
            if part == "":
                continue
            glued = bool(i == 0 and tokens and not seg_text.startswith(" ") and part[0] in _NO_SPACE_BEFORE)
            tokens.append((part, italic, glued))

    while True:
        font_reg = _font(font_regular_path, size)
        font_ital = _font(font_italic_path, size)
        space_w = _text_w(draw, " ", font_reg)

        lines = []
        current = []
        current_w = 0
        for word, italic, glued in tokens:
            f = font_ital if italic else font_reg
            w_width = _text_w(draw, word, f)
            add_w = w_width if (not current or glued) else w_width + space_w
            if current and current_w + add_w > max_width and not glued:
                lines.append(current)
                current = [(word, italic, glued)]
                current_w = w_width
            else:
                current.append((word, italic, glued))
                current_w += add_w
        if current:
            lines.append(current)

        if max_lines is None or len(lines) <= max_lines or size <= min_size:
            return lines, size
        size -= step


def _draw_wrapped(draw, lines, x, y, font_regular_path, font_italic_path, size,
                   color_regular, color_italic):
    font_reg = _font(font_regular_path, size)
    font_ital = _font(font_italic_path, size)
    space_w = _text_w(draw, " ", font_reg)
    line_h = _line_height(font_reg)
    cy = y
    for line in lines:
        cx = x
        for i, (word, italic, glued) in enumerate(line):
            f = font_ital if italic else font_reg
            color = color_italic if italic else color_regular
            if i > 0 and not glued:
                cx += space_w
            draw.text((cx, cy), word, font=f, fill=color)
            cx += _text_w(draw, word, f)
        cy += line_h + LINE_SPACING
    return cy - LINE_SPACING  # y nach der letzten Zeile


def _fit_row_font_size(draw, rows, card_w, start_size=34, min_size=20, step=2):
    """Reduziert die Zeilen-Schriftgroesse in slide_rows, bis Label+Wert nebeneinander passen."""
    usable = card_w - 56
    size = start_size
    while size > min_size:
        font = _font(B.SERIF_REGULAR, size)
        gap = 20
        if all(_text_w(draw, label, font) + _text_w(draw, value, font) + gap <= usable for label, value, _ in rows):
            return size
        size -= step
    return min_size


def _truncate_to_width(draw, text, font, max_width):
    """Kuerzt text mit '…', falls es bei max_width nicht passt."""
    if _text_w(draw, text, font) <= max_width:
        return text
    ellipsis = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        candidate = text[:mid].rstrip() + ellipsis
        if _text_w(draw, candidate, font) <= max_width:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ellipsis if lo > 0 else ellipsis


def _wrapped_height(n_lines, font_regular_path, size):
    if n_lines == 0:
        return 0
    line_h = _line_height(_font(font_regular_path, size))
    return n_lines * line_h + (n_lines - 1) * LINE_SPACING


# --- Canvas / Grundelemente ---

def _new_canvas():
    img = Image.new("RGB", B.FEED_SIZE, B.BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, B.FEED_SIZE[1]], fill=B.INK)
    return img, draw


def _draw_eyebrow(draw, eyebrow):
    if not eyebrow:
        return
    font = _font(B.SANS_BOLD, B.EYEBROW_SIZE)
    _draw_tracked(draw, (B.MARGIN_LEFT, 72), eyebrow.upper(), font, B.SUBTEXT, B.EYEBROW_TRACKING)


def _draw_footer(draw, page_no, total_pages):
    W, H = B.FEED_SIZE
    y_divider = int(H * 0.90)
    draw.line([(B.MARGIN_LEFT, y_divider), (W - B.MARGIN_RIGHT, y_divider)], fill=B.DIVIDER, width=2)

    font_word = _font(B.SANS_BOLD, B.FOOTER_SIZE)
    _draw_tracked(draw, (B.MARGIN_LEFT, y_divider + 18), B.WORDMARK, font_word, B.INK, 3)

    page_text = f"{page_no:02d} / {total_pages:02d}"
    pw = _text_w(draw, page_text, font_word)
    draw.text((W - B.MARGIN_RIGHT - pw, y_divider + 18), page_text, font=font_word, fill=B.SUBTEXT)

    font_disc = _font(B.SERIF_REGULAR, B.DISCLAIMER_SIZE)
    draw.text((B.MARGIN_LEFT, y_divider + 54), B.DISCLAIMER, font=font_disc, fill=B.SUBTEXT)


def _content_area():
    """(top, bottom) fuer den vertikal zu zentrierenden Inhaltsblock."""
    top = 170
    bottom = int(B.FEED_SIZE[1] * B.CONTENT_MAX_Y_RATIO)
    return top, bottom


def _headline_block(draw, headline, max_width, size=B.HEADLINE_SIZE, max_lines=3):
    lines, used_size = _wrap_markup(
        draw, headline, B.SERIF_BOLD, B.SERIF_BOLD_ITALIC, size, max_width, max_lines=max_lines
    )
    height = _wrapped_height(len(lines), B.SERIF_BOLD, used_size)
    return lines, used_size, height


def _draw_headline(draw, lines, size, x, y):
    return _draw_wrapped(draw, lines, x, y, B.SERIF_BOLD, B.SERIF_BOLD_ITALIC, size, B.INK, B.GREEN)


def _accent_line_height():
    return B.ACCENT_LINE_HEIGHT


def _draw_accent_line(draw, x, y):
    draw.rectangle([x, y, x + B.ACCENT_LINE_WIDTH, y + B.ACCENT_LINE_HEIGHT], fill=B.GREEN)
    return y + B.ACCENT_LINE_HEIGHT


def _body_block(draw, body, max_width, size=B.BODY_SIZE, max_lines=8):
    lines, used_size = _wrap_markup(
        draw, body, B.SERIF_REGULAR, B.SERIF_BOLD_ITALIC, size, max_width, max_lines=max_lines
    )
    height = _wrapped_height(len(lines), B.SERIF_REGULAR, used_size)
    return lines, used_size, height


def _draw_body(draw, lines, size, x, y):
    return _draw_wrapped(draw, lines, x, y, B.SERIF_REGULAR, B.SERIF_BOLD_ITALIC, size, B.BODY_TEXT, B.GREEN)


class Post:
    def __init__(self, name: str, total_slides: int):
        self.name = name
        self.total = total_slides
        self.slides: list[Image.Image] = []

    def _next_page(self):
        return len(self.slides) + 1

    def _max_width(self):
        return B.FEED_SIZE[0] - B.MARGIN_LEFT - B.MARGIN_RIGHT

    def _finish(self, img, draw):
        page_no = self._next_page()
        _draw_footer(draw, page_no, self.total)
        self.slides.append(img)

    # --- slide_hook(eyebrow, headline, subline) ---
    def slide_hook(self, eyebrow, headline, subline=""):
        img, draw = _new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = _content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w, size=76, max_lines=4)
        sub_lines, sub_size, sub_h = [], 32, 0
        if subline:
            sub_lines, sub_size = _wrap_markup(
                draw, subline, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC, 32, max_w, max_lines=3
            )
            sub_h = _wrapped_height(len(sub_lines), B.SERIF_BOLD_ITALIC, sub_size)

        block_h = h_h + (BLOCK_GAP + sub_h if subline else 0)
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        if subline:
            y += BLOCK_GAP
            _draw_wrapped(draw, sub_lines, B.MARGIN_LEFT, y, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC,
                          sub_size, B.GREEN, B.GREEN)

        self._finish(img, draw)
        return img

    # --- slide_text(eyebrow, headline, body) ---
    def slide_text(self, eyebrow, headline, body):
        img, draw = _new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = _content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w)
        b_lines, b_size, b_h = _body_block(draw, body, max_w)

        block_h = h_h + BLOCK_GAP + _accent_line_height() + BLOCK_GAP + b_h
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        _draw_body(draw, b_lines, b_size, B.MARGIN_LEFT, y)

        self._finish(img, draw)
        return img

    # --- slide_rows(eyebrow, headline, rows, note) ---
    # rows = [(Label, Wert, Farbe), ...]
    def slide_rows(self, eyebrow, headline, rows, note=""):
        img, draw = _new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = _content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w)

        row_size = _fit_row_font_size(draw, rows, max_w)
        row_font = _font(B.SERIF_REGULAR, row_size)
        row_h = _line_height(row_font) + 26
        card_pad = 32
        card_h = row_h * len(rows) + card_pad * 2

        note_lines, note_size, note_h = ([], B.DISCLAIMER_SIZE, 0)
        if note:
            note_lines, note_size = _wrap_markup(
                draw, note, B.SERIF_REGULAR, B.SERIF_BOLD_ITALIC, 24, max_w, max_lines=2
            )
            note_h = _wrapped_height(len(note_lines), B.SERIF_REGULAR, note_size)

        block_h = h_h + BLOCK_GAP + _accent_line_height() + BLOCK_GAP + card_h + (BLOCK_GAP + note_h if note else 0)
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        y += BLOCK_GAP

        card_w = max_w
        draw.rectangle([B.MARGIN_LEFT, y, B.MARGIN_LEFT + card_w, y + card_h], fill=B.CARD)
        ry = y + card_pad
        label_max_w = card_w - 56
        for i, (label, value, color) in enumerate(rows):
            vw = _text_w(draw, value, row_font)
            label_text = _truncate_to_width(draw, label, row_font, label_max_w - vw - 20)
            draw.text((B.MARGIN_LEFT + 28, ry), label_text, font=row_font, fill=B.BODY_TEXT)
            draw.text((B.MARGIN_LEFT + card_w - 28 - vw, ry), value, font=row_font, fill=color)
            if i < len(rows) - 1:
                draw.line(
                    [(B.MARGIN_LEFT + 28, ry + row_h - 8), (B.MARGIN_LEFT + card_w - 28, ry + row_h - 8)],
                    fill=B.DIVIDER, width=1,
                )
            ry += row_h
        y = y + card_h

        if note:
            y += BLOCK_GAP
            _draw_wrapped(draw, note_lines, B.MARGIN_LEFT, y, B.SERIF_REGULAR, B.SERIF_BOLD_ITALIC,
                          note_size, B.SUBTEXT, B.GREEN)

        self._finish(img, draw)
        return img

    # --- slide_card(eyebrow, headline, big, small, body) ---
    def slide_card(self, eyebrow, headline, big, small, body=""):
        img, draw = _new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = _content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w)

        big_color = B.INK
        if big.strip().startswith("+"):
            big_color = B.GREEN
        elif big.strip().startswith("-"):
            big_color = B.RED
        big_font = _font(B.SERIF_BOLD, 110)
        big_h = _line_height(big_font)

        small_font = _font(B.SANS_BOLD, B.EYEBROW_SIZE)
        small_h = _line_height(small_font)

        b_lines, b_size, b_h = ([], B.BODY_SIZE, 0)
        if body:
            b_lines, b_size, b_h = _body_block(draw, body, max_w, max_lines=5)

        block_h = (h_h + BLOCK_GAP + _accent_line_height() + BLOCK_GAP
                   + big_h + 12 + small_h + (BLOCK_GAP + b_h if body else 0))
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        y += BLOCK_GAP

        draw.text((B.MARGIN_LEFT, y), big, font=big_font, fill=big_color)
        y += big_h + 12
        _draw_tracked(draw, (B.MARGIN_LEFT, y), small.upper(), small_font, B.SUBTEXT, B.EYEBROW_TRACKING)
        y += small_h

        if body:
            y += BLOCK_GAP
            _draw_body(draw, b_lines, b_size, B.MARGIN_LEFT, y)

        self._finish(img, draw)
        return img

    # --- slide_cta(eyebrow, headline, body) ---
    def slide_cta(self, eyebrow, headline, body=""):
        img, draw = _new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = _content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w)
        b_lines, b_size, b_h = ([], B.BODY_SIZE, 0)
        if body:
            b_lines, b_size, b_h = _body_block(draw, body, max_w, max_lines=5)

        cta_font = _font(B.SERIF_BOLD_ITALIC, 38)
        cta_h = _line_height(cta_font)
        cta_text = "Folgen fuer die Fortsetzung"

        block_h = h_h + BLOCK_GAP + (b_h + BLOCK_GAP if body else 0) + cta_h
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        if body:
            y += BLOCK_GAP
            y = _draw_body(draw, b_lines, b_size, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        draw.text((B.MARGIN_LEFT, y), cta_text, font=cta_font, fill=B.GREEN)

        self._finish(img, draw)
        return img

    # --- slide_title(word, subtitle) — Titelkarte fuer Highlights ---
    def slide_title(self, word, subtitle=""):
        img, draw = _new_canvas()
        max_w = self._max_width()
        top, bottom = _content_area()

        title_text = word.rstrip(".") + "."
        title_font = _font(B.SERIF_BOLD, 120)
        title_h = _line_height(title_font)

        sub_lines, sub_size, sub_h = ([], 34, 0)
        if subtitle:
            sub_lines, sub_size = _wrap_markup(
                draw, subtitle, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC, 34, max_w, max_lines=2
            )
            sub_h = _wrapped_height(len(sub_lines), B.SERIF_BOLD_ITALIC, sub_size)

        block_h = title_h + BLOCK_GAP + _accent_line_height() + (BLOCK_GAP + sub_h if subtitle else 0)
        y = top + max(0, (bottom - top - block_h) // 2)

        draw.text((B.MARGIN_LEFT, y), title_text, font=title_font, fill=B.INK)
        y += title_h + BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        if subtitle:
            y += BLOCK_GAP
            _draw_wrapped(draw, sub_lines, B.MARGIN_LEFT, y, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC,
                          sub_size, B.GREEN, B.GREEN)

        self._finish(img, draw)
        return img

    # --- Export ---
    def export(self):
        ig_dir = OUTPUT / self.name / "instagram_4x5"
        tt_dir = OUTPUT / self.name / "tiktok_9x16"
        ig_dir.mkdir(parents=True, exist_ok=True)
        tt_dir.mkdir(parents=True, exist_ok=True)

        for i, img in enumerate(self.slides, start=1):
            img.save(ig_dir / f"slide_{i}.png")
            canvas = Image.new("RGB", B.STORY_SIZE, B.BG)
            x = (B.STORY_SIZE[0] - img.width) // 2
            y = (B.STORY_SIZE[1] - img.height) // 2
            canvas.paste(img, (x, y))
            canvas.save(tt_dir / f"slide_{i}.png")

        self._contact_sheet()
        return ig_dir, tt_dir

    def _contact_sheet(self):
        n = len(self.slides)
        if n == 0:
            return
        cols = 3
        rows = (n + cols - 1) // cols
        thumb_w = 300
        thumb_h = int(thumb_w * B.FEED_SIZE[1] / B.FEED_SIZE[0])
        pad = 20
        sheet_w = cols * thumb_w + (cols + 1) * pad
        sheet_h = rows * thumb_h + (rows + 1) * pad
        sheet = Image.new("RGB", (sheet_w, sheet_h), B.BG)
        for i, img in enumerate(self.slides):
            thumb = img.resize((thumb_w, thumb_h))
            r, c = divmod(i, cols)
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h + pad)
            sheet.paste(thumb, (x, y))
        sheet.save(OUTPUT / self.name / "uebersicht.png")


class HighlightDeck:
    """Story-Highlight-Serie, nativ 1080x1920 (CLAUDE.md 'Wiederkehrende Formate' / PROMPTS.md Prompt 5).

    Nutzung:
        deck = HighlightDeck("etf_basics", total_slides=5)
        deck.slide_title("etf", "Was ein ETF eigentlich ist.")
        deck.slide_text("ETF", "Ein ETF ist ein *Fonds* ...", "Fliesstext ...")
        ...
        deck.export()
    """

    def __init__(self, name: str, total_slides: int):
        self.name = name
        self.total = total_slides
        self.slides: list[Image.Image] = []

    def _max_width(self):
        return B.STORY_SIZE[0] - B.MARGIN_LEFT - B.MARGIN_RIGHT

    def _content_area(self):
        top = 170
        bottom = int(B.STORY_SIZE[1] * B.CONTENT_MAX_Y_RATIO)
        return top, bottom

    def _new_canvas(self):
        img = Image.new("RGB", B.STORY_SIZE, B.BG)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, B.BAR_WIDTH, B.STORY_SIZE[1]], fill=B.INK)
        return img, draw

    def _draw_footer(self, draw, page_no):
        W, H = B.STORY_SIZE
        y_divider = int(H * 0.90)
        draw.line([(B.MARGIN_LEFT, y_divider), (W - B.MARGIN_RIGHT, y_divider)], fill=B.DIVIDER, width=2)
        font_word = _font(B.SANS_BOLD, B.FOOTER_SIZE)
        _draw_tracked(draw, (B.MARGIN_LEFT, y_divider + 18), B.WORDMARK, font_word, B.INK, 3)
        page_text = f"{page_no:02d} / {self.total:02d}"
        pw = _text_w(draw, page_text, font_word)
        draw.text((W - B.MARGIN_RIGHT - pw, y_divider + 18), page_text, font=font_word, fill=B.SUBTEXT)
        font_disc = _font(B.SERIF_REGULAR, B.DISCLAIMER_SIZE)
        draw.text((B.MARGIN_LEFT, y_divider + 54), B.DISCLAIMER, font=font_disc, fill=B.SUBTEXT)

    def slide_title(self, word, subtitle=""):
        """Titelkarte -- zaehlt nicht in der Seitennummerierung, kein Eyebrow/Footer-Zaehler."""
        img, draw = self._new_canvas()
        max_w = self._max_width()
        top, bottom = self._content_area()

        title_text = word.rstrip(".") + "."
        title_font = _font(B.SERIF_BOLD, 130)
        title_h = _line_height(title_font)

        sub_lines, sub_size, sub_h = [], 36, 0
        if subtitle:
            sub_lines, sub_size = _wrap_markup(
                draw, subtitle, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC, 36, max_w, max_lines=2
            )
            sub_h = _wrapped_height(len(sub_lines), B.SERIF_BOLD_ITALIC, sub_size)

        block_h = title_h + BLOCK_GAP + _accent_line_height() + (BLOCK_GAP + sub_h if subtitle else 0)
        y = top + max(0, (bottom - top - block_h) // 2)

        draw.text((B.MARGIN_LEFT, y), title_text, font=title_font, fill=B.INK)
        y += title_h + BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        if subtitle:
            y += BLOCK_GAP
            _draw_wrapped(draw, sub_lines, B.MARGIN_LEFT, y, B.SERIF_BOLD_ITALIC, B.SERIF_BOLD_ITALIC,
                          sub_size, B.GREEN, B.GREEN)

        self.slides.append(img)
        return img

    def slide_text(self, eyebrow, headline, body):
        img, draw = self._new_canvas()
        _draw_eyebrow(draw, eyebrow)
        max_w = self._max_width()
        top, bottom = self._content_area()

        h_lines, h_size, h_h = _headline_block(draw, headline, max_w)
        b_lines, b_size, b_h = _body_block(draw, body, max_w, max_lines=10)

        block_h = h_h + BLOCK_GAP + _accent_line_height() + BLOCK_GAP + b_h
        y = top + max(0, (bottom - top - block_h) // 2)

        y = _draw_headline(draw, h_lines, h_size, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        y = _draw_accent_line(draw, B.MARGIN_LEFT, y)
        y += BLOCK_GAP
        _draw_body(draw, b_lines, b_size, B.MARGIN_LEFT, y)

        page_no = len(self.slides)  # Titelkarte (falls vorhanden) zaehlt nicht mit
        self._draw_footer(draw, page_no)
        self.slides.append(img)
        return img

    def export(self):
        out_dir = OUTPUT / self.name
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(self.slides):
            img.save(out_dir / f"{i:02d}.png")
        return out_dir
