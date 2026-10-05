"""CTA-Story "Wie war deine Woche?" (neu, 2026-09-20): allgemeine
Engagement-Frage zur Boersenwoche, nicht aktienspezifisch -- Follower
antworten per DM/Kommentar (Graph API unterstuetzt keine echten
Umfrage-Sticker, gleiche Einschraenkung wie story_depotfrage_cta.py und
story_deepdive_poll.py). Eigene Farbidentitaet: warmes Terrakotta statt
Gold/Blau/Violett/Rosegold, die die anderen CTA-/Poll-Formate schon nutzen.

Aufruf:
  python posts/story_wochencheck_cta.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
import brand as B
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent
NAME = "story_wochencheck_cta"
OUTPUT = ROOT / "output" / NAME
TT_DIR = OUTPUT / "tiktok_9x16"
TT_DIR.mkdir(parents=True, exist_ok=True)

W, H = B.STORY_SIZE

BG_TOP = (46, 26, 20)
BG_BOTTOM = (20, 12, 10)
CREAM = "#F2F0EA"
MUTED = "#C9AFA3"
TERRACOTTA = "#E0714F"
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


def gradient_background(top_rgb, bottom_rgb):
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((W, H))


def add_radial_glow(img, cx, cy, radius, color, strength=55):
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    color_layer = Image.new("RGB", (W, H), color)
    img.paste(color_layer, (0, 0), glow)


def slide_rueckblick(week_label):
    """v2 (2026-10-06): depotdiary-Foto-Schema statt Terrakotta-Flaeche."""
    return S.draw_cta_story(
        "wochencheck-1-" + week_label, "WOCHEN-CHECK  1/2", ["WIE WAR DEINE", "WOCHE?"],
        f"Meins: {week_label}. Und bei dir -- Plus, Minus oder unveraendert?",
        "Schreib's mir per DM oder Kommentar.",
        "Keine Anlageberatung -- reine Community-Frage.")


def slide_ausblick(earnings_names):
    return S.draw_cta_story(
        "wochencheck-2-" + ",".join(earnings_names[:2]), "WOCHEN-CHECK  2/2",
        ["UND WIE WIRD DIE", "KOMMENDE WOCHE?"],
        "Diese Woche berichten u.a. " + ", ".join(earnings_names) + " -- volle Earnings-Woche.",
        "Worauf achtest du naechste Woche am meisten?",
        "Keine Anlageberatung -- reine Community-Frage.")


def main(week_label, earnings_names):
    slide_rueckblick(week_label).save(TT_DIR / "slide_1.png")
    slide_ausblick(earnings_names).save(TT_DIR / "slide_2.png")
    slide_rueckblick(week_label).save(OUTPUT / "uebersicht.png")
    print(f"Fertig: 2 Slides in {TT_DIR}")


if __name__ == "__main__":
    main("+1,61 %", ["AutoZone", "Costco", "Cintas", "General Mills", "Paychex"])
