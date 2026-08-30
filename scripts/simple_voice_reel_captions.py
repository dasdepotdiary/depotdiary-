"""Minimal-Aufwand-Reel MIT Untertiteln: eine einzelne Titel-Folie (9:16) +
echte Sprachaufnahme + eingebrannte Untertitel, die proportional zur
Wortzahl über die echte Audiolaenge verteilt werden (kein Pexels-Footage).

Aufruf:
  python scripts/simple_voice_reel_captions.py <post_name> "<Titel>" <audio_datei> <text_datei.txt> <output_mp4>
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
from scripts.simple_voice_reel import build_title_slide

sys.path.insert(0, str(Path(__file__).parent.parent / "video"))
from assemble import render_caption_image, split_into_phrases


def get_audio_duration(path: str) -> float:
    import imageio_ffmpeg
    import subprocess
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ffmpeg, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def build_caption_timeline(full_text: str, total_duration: float) -> list[dict]:
    """Teilt den Text in Saetze, verteilt die echte Audiolaenge proportional
    zur Wortzahl jedes Satzes -- gleiches Prinzip wie timing.json bei den
    KI-Stimme-Reels, nur mit der echten Aufnahmelaenge statt geschaetzt."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", full_text.strip()) if s.strip()]
    word_counts = [len(re.findall(r"\S+", s)) for s in sentences]
    total_words = sum(word_counts)
    result = []
    t = 0.0
    for s, wc in zip(sentences, word_counts):
        dur = total_duration * (wc / total_words)
        result.append({"text": s, "start": t, "duration": dur})
        t += dur
    return result


def main():
    post_name, title, audio_path, text_path, out_path = sys.argv[1:6]
    full_text = Path(text_path).read_text(encoding="utf-8")
    out_dir = Path(__file__).parent.parent / "output" / post_name
    out_dir.mkdir(parents=True, exist_ok=True)
    slide_path = out_dir / "title_slide.png"
    build_title_slide(title).save(slide_path)

    duration = get_audio_duration(audio_path)
    sentences = build_caption_timeline(full_text, duration)

    from moviepy import AudioFileClip, CompositeVideoClip, ImageClip

    W, H = B.STORY_SIZE
    bg = ImageClip(str(slide_path)).with_duration(duration)

    caption_clips_list = []
    for s in sentences:
        phrases = split_into_phrases(s["text"])
        if not phrases:
            continue
        phrase_dur = s["duration"] / len(phrases)
        for i, phrase in enumerate(phrases):
            arr = render_caption_image(phrase, (W, H), position="center")
            clip = ImageClip(arr).with_start(s["start"] + i * phrase_dur).with_duration(phrase_dur)
            caption_clips_list.append(clip)

    audio = AudioFileClip(audio_path)
    video = CompositeVideoClip([bg] + caption_clips_list, size=(W, H)).with_duration(duration)
    video = video.with_audio(audio)
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", logger=None)
    print(f"Fertig: {out_path}")


if __name__ == "__main__":
    main()
