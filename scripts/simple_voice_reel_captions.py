"""Minimal-Aufwand-Reel MIT Untertiteln: eine einzelne Titel-Folie (9:16) +
echte Sprachaufnahme + eingebrannte Untertitel. Die Untertitel-Zeiten kommen
aus echter Spracherkennung (faster-whisper, Wort-Zeitstempel) der
tatsaechlichen Aufnahme -- nicht aus einer Wortzahl-Schaetzung ueber ein
vorgeschriebenes Skript, weil frei gesprochene Aufnahmen vom Skripttext
abweichen und damit jede Schaetzung aus der Zeit laeuft.

Aufruf:
  python scripts/simple_voice_reel_captions.py <post_name> "<Titel>" <audio_datei> <output_mp4>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B
from scripts.simple_voice_reel import build_title_slide

sys.path.insert(0, str(Path(__file__).parent.parent / "video"))
from assemble import render_caption_image

MAX_PHRASE_WORDS = 5
PAUSE_BREAK_SECONDS = 0.5


def transcribe_words(audio_path: str, model_size: str = "small") -> list[dict]:
    """Echte Wort-Zeitstempel per faster-whisper. Gibt [{"word", "start", "end"}, ...]."""
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language="de", word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return words


def group_into_phrases(words: list[dict], max_words: int = MAX_PHRASE_WORDS,
                        pause_break: float = PAUSE_BREAK_SECONDS) -> list[dict]:
    """Gruppiert Woerter zu Untertitel-Phrasen anhand echter Sprechpausen
    (Luecke zwischen zwei Woertern) und Satzzeichen -- nicht anhand einer
    festen Wortanzahl allein, damit die Phrasen an natuerlichen Stellen
    enden."""
    phrases = []
    current = []
    for i, w in enumerate(words):
        current.append(w)
        is_last = i == len(words) - 1
        ends_clause = bool(current) and current[-1]["word"] and current[-1]["word"][-1] in ".,!?;:"
        gap_after = (words[i + 1]["start"] - w["end"]) if not is_last else 0
        if is_last or len(current) >= max_words or ends_clause or gap_after >= pause_break:
            text = " ".join(c["word"] for c in current)
            phrases.append({"text": text, "start": current[0]["start"], "end": current[-1]["end"]})
            current = []
    return phrases


def main():
    post_name, title, audio_path = sys.argv[1:4]
    out_path = sys.argv[4]
    out_dir = Path(__file__).parent.parent / "output" / post_name
    out_dir.mkdir(parents=True, exist_ok=True)
    slide_path = out_dir / "title_slide.png"
    build_title_slide(title).save(slide_path)

    print("Transkribiere echte Aufnahme (faster-whisper)...")
    words = transcribe_words(audio_path)
    phrases = group_into_phrases(words)

    from moviepy import AudioFileClip, CompositeVideoClip, ImageClip

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    W, H = B.STORY_SIZE
    bg = ImageClip(str(slide_path)).with_duration(duration)

    caption_clips_list = []
    for p in phrases:
        arr = render_caption_image(p["text"], (W, H), position="center")
        clip = ImageClip(arr).with_start(p["start"]).with_duration(max(p["end"] - p["start"], 0.3))
        caption_clips_list.append(clip)

    video = CompositeVideoClip([bg] + caption_clips_list, size=(W, H)).with_duration(duration)
    video = video.with_audio(audio)
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", logger=None)
    print(f"Fertig: {out_path}")


if __name__ == "__main__":
    main()
