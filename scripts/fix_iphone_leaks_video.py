"""Einmaliger Fix fuer das selbst aufgenommene iPhone-18-Leaks-Video des Nutzers
(2026-09-09): Quelle ist 576x1248 (schmaler als die 1080x1920-Reel-Leinwand,
haette sonst schwarze Balken) und 99s lang als EIN statisches Standbild --
Nutzer-Feedback war "kannst du das Frame fixen" + "pexel clips dazwischen".

Skaliert/croppt die Bulletlist-Aufnahme auf volle 1080x1920 (cover-Crop) und
schneidet an ein paar Stellen kurz auf echte Pexels-B-Roll-Clips um (Ton
laeuft durchgehend vom Original weiter, nur das Bild wechselt kurz).

Aufruf:
  python scripts/fix_iphone_leaks_video.py
"""
from pathlib import Path

from moviepy import CompositeVideoClip, VideoFileClip, vfx

ROOT = Path(__file__).parent.parent
SRC = Path(r"C:\Users\rasch\Downloads\Neuer Ordner (2)\WhatsApp Video 2026-09-09 at 02.01.58.mp4")
OUT_DIR = ROOT / "output" / "iphone_leaks_fix"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "iphone_leaks_fixed.mp4"

TARGET_W, TARGET_H = 1080, 1920
BROLL_DURATION = 2.5
# Zeitpunkte im Original, an denen kurz auf B-Roll umgeschnitten wird --
# grob gleichmaessig ueber die 99s verteilt, meidet Anfang/Ende (Hook und
# Payoff sollen die eigene Aufnahme bleiben).
CUTAWAY_STARTS = [14, 34, 54, 74]
BROLL_FILES = ["pexels_1.mp4", "pexels_2.mp4", "pexels_3.mp4"]


def cover_resize(clip, w, h):
    scale = max(w / clip.w, h / clip.h)
    resized = clip.resized(scale)
    x_center, y_center = resized.w / 2, resized.h / 2
    return resized.cropped(x_center=x_center, y_center=y_center, width=w, height=h)


def main():
    base = VideoFileClip(str(SRC))
    base = cover_resize(base, TARGET_W, TARGET_H)

    layers = [base]
    for i, start in enumerate(CUTAWAY_STARTS):
        broll_path = OUT_DIR / BROLL_FILES[i % len(BROLL_FILES)]
        broll = VideoFileClip(str(broll_path)).subclipped(0, BROLL_DURATION)
        broll = cover_resize(broll, TARGET_W, TARGET_H)
        broll = broll.with_start(start).with_effects([vfx.CrossFadeIn(0.3), vfx.CrossFadeOut(0.3)])
        layers.append(broll)

    video = CompositeVideoClip(layers, size=(TARGET_W, TARGET_H)).with_duration(base.duration)
    video = video.with_audio(base.audio)

    video.write_videofile(str(OUT), fps=30, codec="libx264", audio_codec="aac", logger=None)
    print(f"Fertig: {OUT} ({video.duration:.1f}s)")


if __name__ == "__main__":
    main()
