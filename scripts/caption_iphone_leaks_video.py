"""Brennt synchrone Untertitel (echte faster-whisper-Wortzeitstempel, nicht
geschaetzt) auf das bereits gefixte iPhone-Leaks-Video des Nutzers
(output/iphone_leaks_fix/iphone_leaks_fixed.mp4) -- Nutzerwunsch 2026-09-09:
"upload mit subtitles ... matching subtitles".

Nutzt dieselbe Transkriptions-/Phrasierungslogik wie die persoenlichen
Reels (scripts/simple_voice_reel_captions.py) und dieselbe Caption-Optik
wie video/assemble.py (render_caption_image, position="center" -- echte
Aufnahme, Untertitel sind hier der Haupt-Content-Layer, nicht nur Ergaenzung).

Aufruf:
  python scripts/caption_iphone_leaks_video.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
from scripts.simple_voice_reel_captions import group_into_phrases, transcribe_words

sys.path.insert(0, str(Path(__file__).parent.parent / "video"))
from assemble import render_caption_image

from moviepy import CompositeVideoClip, ImageClip, VideoFileClip

ROOT = Path(__file__).parent.parent
SRC = ROOT / "output" / "iphone_leaks_fix" / "iphone_leaks_fixed.mp4"
OUT = ROOT / "output" / "iphone_leaks_fix" / "iphone_leaks_captioned.mp4"


def main():
    if not SRC.exists():
        sys.exit(f"Nicht gefunden: {SRC} -- erst fix_iphone_leaks_video.py fertig laufen lassen.")

    print("Transkribiere echte Aufnahme (faster-whisper)...")
    words = transcribe_words(str(SRC))
    phrases = group_into_phrases(words, max_words=8, pause_break=0.5)
    print(f"{len(phrases)} Untertitel-Phrasen erkannt.")

    base = VideoFileClip(str(SRC))
    W, H = base.size

    caption_layers = []
    for p in phrases:
        arr = render_caption_image(p["text"], (W, H), position="center")
        clip = ImageClip(arr).with_start(p["start"]).with_duration(max(p["end"] - p["start"], 0.3))
        caption_layers.append(clip)

    video = CompositeVideoClip([base] + caption_layers, size=(W, H)).with_duration(base.duration)
    video = video.with_audio(base.audio)
    video.write_videofile(str(OUT), fps=30, codec="libx264", audio_codec="aac", logger=None)
    print(f"Fertig: {OUT} ({video.duration:.1f}s)")


if __name__ == "__main__":
    main()
