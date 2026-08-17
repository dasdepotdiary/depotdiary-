"""Setzt die Slides eines Posts zu einem Video zusammen (sanftes Ken-Burns-Pan + Crossfade).

Ohne --audio: stumme Timing-Vorschau, um das Tempo vorab zu pruefen.
Mit --audio: Gesamtlaenge folgt der Audiodatei, die Slide-Anteile bleiben
             proportional zum Voiceover-Skript (output/<post_name>/timing.json).

Keine eingebrannten Untertitel -- die App-eigenen (TikTok/Instagram) sind
praeziser (echtes Speech-to-Text-Timing statt geschaetzt) und besser in die
jeweilige Plattform-UI integriert.

Aufruf:
  python video/assemble.py depot_update_2026-08
  python video/assemble.py depot_update_2026-08 --audio pfad/zu/meiner_stimme.mp3
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, VideoClip, concatenate_videoclips, vfx

ROOT = Path(__file__).parent.parent
FADE = 0.35
DEFAULT_SLIDE_SECONDS = 4.0

# Ochre-Akzentfarbe (brand.OCHRE = #B08A2E) als RGB fuer den Ambient-Sweep
OCHRE_RGB = (176, 138, 46)


def ambient_sweep_clip(size: tuple[int, int], duration: float, opacity: float = 0.10):
    """Sehr sanfter, langsam diagonal wandernder Lichtschein -- dezente Bewegung
    im Hintergrund, ohne den Text zu stoeren (niedrige Deckkraft, weicher Verlauf)."""
    w, h = size
    band_w = int(w * 0.9)
    yy, xx = np.mgrid[0:h, 0:w]
    diag = (xx + yy).astype(np.float32)
    diag_min, diag_max = diag.min(), diag.max()

    def make_frame(t):
        progress = (t / duration) % 1.0
        center = diag_min + (diag_max - diag_min) * progress
        dist = np.abs(diag - center)
        band = np.clip(1 - dist / band_w, 0, 1) ** 2
        frame = np.zeros((h, w, 3), dtype=np.float32)
        for c in range(3):
            frame[:, :, c] = band * OCHRE_RGB[c]
        return frame.astype("uint8")

    def make_mask(t):
        progress = (t / duration) % 1.0
        center = diag_min + (diag_max - diag_min) * progress
        dist = np.abs(diag - center)
        band = np.clip(1 - dist / band_w, 0, 1) ** 2
        return (band * opacity).astype(np.float64)

    clip = VideoClip(make_frame, duration=duration)
    mask = VideoClip(make_mask, duration=duration, is_mask=True)
    return clip.with_mask(mask)


def load_durations(post_name: str, n_slides: int) -> list[float]:
    path = ROOT / "output" / post_name / "timing.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        durations = [s["duration"] for s in data["sentences"]]
        if len(durations) == n_slides:
            return durations
        print(f"Hinweis: timing.json hat {len(durations)} Eintraege, aber {n_slides} Slides -- nutze Standardtiming.")
    return [DEFAULT_SLIDE_SECONDS] * n_slides


def ken_burns_clip(path: Path, duration: float, zoom: float = 0.06):
    base = ImageClip(str(path))
    w, h = base.size
    zoomed = base.with_duration(duration).with_effects(
        [vfx.Resize(lambda t: 1 + zoom * (t / duration))]
    )
    zoomed = zoomed.with_position("center")
    return CompositeVideoClip([zoomed], size=(w, h)).with_duration(duration)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("post_name")
    parser.add_argument("--audio", help="Pfad zu deiner eigenen Sprachaufnahme (mp3/wav/m4a)")
    parser.add_argument("--ambient", action="store_true", help="Sanfter bewegter Lichtschein-Hintergrund (kostenlos, kein KI-Video)")
    args = parser.parse_args()

    slide_dir = ROOT / "output" / args.post_name / "tiktok_9x16"
    slides = sorted(slide_dir.glob("slide_*.png"))
    if not slides:
        sys.exit(f"Keine Slides gefunden in {slide_dir}")

    durations = load_durations(args.post_name, len(slides))

    audio_clip = None
    if args.audio:
        audio_path = Path(args.audio)
        if not audio_path.exists():
            sys.exit(f"Audiodatei nicht gefunden: {audio_path}")
        audio_clip = AudioFileClip(str(audio_path))
        scale = audio_clip.duration / sum(durations)
        durations = [d * scale for d in durations]

    clips = []
    for i, (path, dur) in enumerate(zip(slides, durations)):
        clip = ken_burns_clip(path, dur)
        if i > 0:
            clip = clip.with_effects([vfx.CrossFadeIn(FADE)])
        clips.append(clip)

    padding = -FADE if len(clips) > 1 else 0
    video = concatenate_videoclips(clips, method="compose", padding=padding)

    if args.ambient:
        sweep = ambient_sweep_clip(video.size, video.duration)
        video = CompositeVideoClip([video, sweep], size=video.size).with_duration(video.duration)

    if audio_clip is not None:
        video = video.with_audio(audio_clip)

    out_path = ROOT / "output" / args.post_name / "reel_9x16.mp4"
    video.write_videofile(
        str(out_path), fps=30, codec="libx264",
        audio_codec="aac" if audio_clip else None, logger=None,
    )
    print(f"Video: {out_path} ({video.duration:.1f}s)")


if __name__ == "__main__":
    main()
