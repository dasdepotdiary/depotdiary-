"""Kurze Story-Ankuendigung fuer einen frisch veroeffentlichten Feed-Post --
weist auf ein neues Carousel hin (z.B. "Dividenden-Aktien im Check"), damit
Follower im Feed vorbeischauen. Wiederverwendbar fuer jeden Feed-Post.

Aufruf:
  python posts/story_post_ankuendigung.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
from format_wochenlogos import draw_wordmark_anchor, wrap_text, HOOK_PHOTO

ROOT = Path(__file__).parent.parent
NAME = "story_post_ankuendigung"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE
CREAM = "#F5F3EE"
MUTED = "#8C8C88"
ACCENT = "#4CC9F0"
OWN_HANDLE = "@DASDEPOTDIARY"


def font(path, size):
    return ImageFont.truetype(path, size)


def story_photo_background():
    """Foto-Hintergrund fuer 9:16 -- eigene Zuschnitt-/Verlauf-Logik statt
    der FEED-tuned Version aus format_wochenlogos, weil die Story deutlich
    hoeher ist und der Verlauf sonst nicht zum Text passt."""
    photo = Image.open(HOOK_PHOTO).convert("RGB")
    src_ratio = photo.width / photo.height
    dst_ratio = W / H
    if src_ratio > dst_ratio:
        new_w = int(photo.height * dst_ratio)
        x0 = (photo.width - new_w) // 2
        photo = photo.crop((x0, 0, x0 + new_w, photo.height))
    else:
        new_h = int(photo.width / dst_ratio)
        y0 = int((photo.height - new_h) * 0.35)
        photo = photo.crop((0, y0, photo.width, y0 + new_h))
    photo = photo.resize((W, H))
    img = ImageEnhance.Brightness(photo).enhance(0.8)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(0.9)

    scrim = Image.new("L", (W, H), 0)
    sdraw = ImageDraw.Draw(scrim)
    for yy in range(H):
        t = yy / H
        if t < 0.28:
            a = int(150 * (1 - t / 0.28))
        elif t < 0.42:
            a = 0
        else:
            a = int(240 * ((t - 0.42) / 0.58))
        sdraw.line([(0, yy), (W, yy)], fill=a)
    black = Image.new("RGB", (W, H), (6, 5, 5))
    img = Image.composite(black, img, scrim)
    return img


def build(headline_lines, sub_text, preview_thumb=None):
    img = story_photo_background()
    draw = ImageDraw.Draw(img)

    handle_font = font(B.SANS_BOLD, 26)
    draw.text((80, 90), OWN_HANDLE, font=handle_font, fill=CREAM)

    y = H * 0.52
    label_font = font(B.SANS_BOLD, 30)
    draw.text((80, y), "NEUER POST IST ONLINE", font=label_font, fill=ACCENT)
    y += 62

    title_font = font(B.SANS_BOLD, 78)
    for line in headline_lines:
        draw.text((80, y), line, font=title_font, fill=CREAM)
        y += 86

    y += 30
    sub_font = font(B.SANS_BOLD, 30)
    for line in wrap_text(draw, sub_text, sub_font, W - 160):
        draw.text((80, y), line, font=sub_font, fill="#D8D5CE")
        y += 40

    y += 40
    cta_font = font(B.SANS_BOLD, 30)
    draw.text((80, y), "Jetzt im Feed ansehen ->", font=cta_font, fill=ACCENT)

    note_font = font(B.SANS_BOLD, 19)
    draw.text((80, H - 70), "Keine Anlageberatung -- reine Uebersicht.", font=note_font, fill="#B8B4AC")

    draw_wordmark_anchor(img, draw)
    return img


def main():
    img = build(
        ["DIVIDENDEN-", "AKTIEN IM CHECK."],
        "Bekannte Dividendenzahler aus verschiedenen Branchen -- jetzt komplett im Feed.",
    )
    img.save(TT_DIR / "slide_1.png")
    img.save(OUTPUT / "uebersicht.png")
    print(f"Fertig: {OUTPUT / 'uebersicht.png'}")


if __name__ == "__main__":
    main()
