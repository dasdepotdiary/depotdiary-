"""Setzt die Slides eines Posts zu einem Video zusammen (sanftes Ken-Burns-Pan + Crossfade).

Ohne --audio: stumme Timing-Vorschau, um das Tempo vorab zu pruefen.
Mit --audio: Gesamtlaenge folgt der Audiodatei, die Slide-Anteile bleiben
             proportional zum Voiceover-Skript (output/<post_name>/timing.json).

Mit --captions: brennt kurze, automatisch generierte Untertitel-Phrasen ein
(synchron zum Voiceover-Timing aus timing.json), fest in der oberen Haelfte
positioniert -- ueberschneidet sich nicht mit dem Footer unten.

Aufruf:
  python video/assemble.py depot_update_2026-08
  python video/assemble.py depot_update_2026-08 --audio pfad/zu/meiner_stimme.mp3
"""

import argparse
import json
import sys
from pathlib import Path

import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, VideoClip, VideoFileClip, concatenate_videoclips, vfx

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B

ROOT = Path(__file__).parent.parent
FADE = 0.35
DEFAULT_SLIDE_SECONDS = 4.0

# Ochre-Akzentfarbe (brand.OCHRE = #B08A2E) als RGB fuer den Ambient-Sweep
OCHRE_RGB = (176, 138, 46)

CAPTION_WORDS_PER_PHRASE = 3
CAPTION_FONT = ImageFont.truetype(B.SANS_BOLD, 44)
# Die tiktok_9x16-Slides sind das 4:5-Bild (1350px hoch), zentriert in eine
# 1920px-Leinwand gepastet -- oben und unten bleiben dadurch ca. 285px reine
# Leerflaeche, IMMER, unabhaengig vom Slide-Inhalt (siehe render.py export()).
# Das ist die einzige garantiert freie Zone -- alles "mittig" ueberschneidet
# sich bei inhaltsreichen Slides (Stats-Kacheln etc.) mit echtem Content.
# Oben statt unten, weil Instagram/TikTok ihre eigene UI (Like/Kommentar/
# Story-Infos) unten ueberlagern.
CAPTION_TOP_PADDING_PX = 80


def _wrap_caption(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def render_caption_image(text: str, video_size: tuple[int, int], position: str = "top") -> np.ndarray:
    """Kurze Untertitel-Phrase: weisser fetter Text auf dunklem Balken (INK,
    hoher Kontrast). position="top": garantiert leere obere Letterbox-Zone
    der tiktok_9x16-Slides (Karten-Modus, ueberschneidet nie echten Inhalt).
    position="center": klassische Untertitel-Position im unteren Drittel,
    fuer --pure-footage, wo der ganze Bildschirm echtes Video ist und die
    Untertitel selbst der Inhalt sind, nicht nur eine Ergaenzung."""
    w, h = video_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    max_text_w = w - 160
    lines = _wrap_caption(draw, text.upper(), CAPTION_FONT, max_text_w)
    line_h = CAPTION_FONT.size + 12
    block_h = len(lines) * line_h
    pad_y = 20
    bar_h = block_h + pad_y * 2

    if position == "center":
        # unteres Drittel, aber klar oberhalb der IG/TikTok-eigenen UI
        # (Like/Kommentar/Story-Infos liegen im untersten ~18%)
        bar_top = int(h * 0.68) - bar_h // 2
    else:
        bar_top = CAPTION_TOP_PADDING_PX

    draw.rounded_rectangle(
        [70, bar_top, w - 70, bar_top + bar_h], radius=16, fill=(22, 24, 28, 230)
    )

    y = bar_top + pad_y
    for line in lines:
        tw = draw.textlength(line, font=CAPTION_FONT)
        x = (w - tw) / 2
        draw.text((x, y), line, font=CAPTION_FONT, fill=(255, 255, 255, 255))
        y += line_h

    return np.array(img)


def split_into_phrases(text: str, max_words: int = 5) -> list[str]:
    """Teilt Text an Satzzeichen/Gedankenstrichen in Phrasen -- vermeidet
    Bruchstuecke mitten im Satz (z.B. 'DAS ABER WIRTSCHAFTLICH'). Nur zu
    lange Phrasen zwischen den Satzzeichen werden zusaetzlich an
    Wortgrenzen aufgeteilt."""
    text = text.replace(" -- ", ", ")
    clauses = re.split(r"(?<=[.,!?;:])\s+", text.strip())
    phrases = []
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        words = clause.split()
        if len(words) <= max_words:
            phrases.append(clause)
        else:
            for i in range(0, len(words), max_words):
                phrases.append(" ".join(words[i:i + max_words]))
    return phrases


def caption_clips(sentences: list[dict], video_size: tuple[int, int], position: str = "top") -> list:
    """Bei echten Whisper-Zeitstempeln (pure-footage-Reels) sind sentences
    bereits einzelne, gut geschnittene Phrasen (siehe scripts/simple_voice_reel_captions.py
    group_into_phrases) -- ein zu niedriges max_words hier wuerde sie erneut
    zerteilen und Bruchstuecke wie "AN," erzeugen (am 2026-09-05 live beobachtet).
    max_words=8 laesst diese Phrasen unangetastet, splittet aber weiterhin die
    langen ganzen Saetze aus voiceover.py fuer die Karten-Slide-Videos."""
    clips = []
    for s in sentences:
        phrases = split_into_phrases(s["text"], max_words=8)
        if not phrases:
            continue
        phrase_dur = s["duration"] / len(phrases)
        for i, phrase in enumerate(phrases):
            arr = render_caption_image(phrase, video_size, position=position)
            clip = ImageClip(arr).with_start(s["start"] + i * phrase_dur).with_duration(phrase_dur)
            clips.append(clip)
    return clips


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


def load_sentences(post_name: str, n_slides: int) -> list[dict] | None:
    path = ROOT / "output" / post_name / "timing.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        sentences = data["sentences"]
        if len(sentences) == n_slides:
            return sentences
        print(f"Hinweis: timing.json hat {len(sentences)} Eintraege, aber {n_slides} Slides -- keine Untertitel.")
    return None


def load_durations(post_name: str, n_slides: int) -> list[float]:
    sentences = load_sentences(post_name, n_slides)
    if sentences:
        return [s["duration"] for s in sentences]
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
    parser.add_argument("--pexels-clips", help="Kommagetrennte Liste echter Videoclips (z.B. von Pexels), werden ueber das Video verteilt eingestreut")
    parser.add_argument("--clip-seconds", type=float, default=2.5, help="Laenge jedes eingestreuten Clips in Sekunden (Default 2.5)")
    parser.add_argument("--no-captions", action="store_true", help="Keine eingebrannten Untertitel")
    parser.add_argument("--captions", action="store_true", help="Eingebrannte Untertitel erzwingen (bei --pure-footage sonst aus, App-eigene Untertitel werden stattdessen genutzt)")
    parser.add_argument("--pure-footage", action="store_true", help="Keine Slide-Karten im Video -- nur echte Videoclips (Slides werden trotzdem fuer Carousel/Story gebraucht)")
    args = parser.parse_args()

    # Nutzer-Feedback: bei --pure-footage wiederholen sich die wenigen echten
    # Clips zu oft und eingebrannte Untertitel passen dann nicht mehr gut dazu
    # -- Default hier ist jetzt AUS, App-eigene Untertitel uebernehmen das.
    # Beim alten Karten-Modus bleiben Captions weiter standardmaessig an.
    if args.pure_footage and not args.captions:
        args.no_captions = True

    slide_dir = ROOT / "output" / args.post_name / "tiktok_9x16"
    slides = sorted(slide_dir.glob("slide_*.png"))
    if not slides:
        sys.exit(f"Keine Slides gefunden in {slide_dir}")

    sentences = load_sentences(args.post_name, len(slides))
    durations = load_durations(args.post_name, len(slides))

    audio_clip = None
    if args.audio:
        audio_path = Path(args.audio)
        if not audio_path.exists():
            sys.exit(f"Audiodatei nicht gefunden: {audio_path}")
        audio_clip = AudioFileClip(str(audio_path))
        scale = audio_clip.duration / sum(durations)
        durations = [d * scale for d in durations]

    def real_clip(path: Path, dur: float, start_offset: float = 0.0):
        vc = VideoFileClip(str(path))
        src_dur = vc.duration
        start = start_offset % max(src_dur - min(dur, src_dur), 0.01)
        if dur <= src_dur - start:
            vc = vc.subclipped(start, start + dur)
        else:
            vc = vc.subclipped(start, src_dur).with_effects([vfx.Loop(duration=dur)])
        w, h = vc.size
        target_w, target_h = 1080, 1920
        scale = max(target_w / w, target_h / h)
        vc = vc.resized(scale).with_position("center")
        return CompositeVideoClip([vc], size=(target_w, target_h)).with_duration(dur)

    pexels_paths = []
    if args.pexels_clips:
        for p in args.pexels_clips.split(","):
            p = Path(p.strip())
            if not p.exists():
                sys.exit(f"Clip nicht gefunden: {p}")
            pexels_paths.append(p)

    clips = []
    slide_starts = []  # tatsaechliche Startzeit jeder Slide im fertigen Video
    cursor = 0.0

    def add_clip(c, dur, is_slide):
        nonlocal cursor
        if clips:
            c = c.with_effects([vfx.CrossFadeIn(FADE)])
            cursor -= FADE
        if is_slide:
            slide_starts.append(cursor)
        clips.append(c)
        cursor += dur

    if args.pure_footage:
        if not pexels_paths:
            sys.exit("--pure-footage braucht --pexels-clips")
        # ein Footage-Segment pro Satz (statt pro Slide) -- Karten werden nie
        # gezeigt, Inhalt kommt nur ueber Sprache + Untertitel
        for i, dur in enumerate(durations):
            path = pexels_paths[i % len(pexels_paths)]
            offset = (i // len(pexels_paths)) * 4.0
            add_clip(real_clip(path, dur, start_offset=offset), dur, is_slide=True)
    else:
        # erster echter Clip immer als Intro voranstellen
        if pexels_paths:
            add_clip(real_clip(pexels_paths[0], args.clip_seconds), args.clip_seconds, is_slide=False)

        # restliche echte Clips gleichmaessig zwischen die Slides verteilen
        remaining = pexels_paths[1:]
        insert_every = max(1, len(slides) // (len(remaining) + 1)) if remaining else None

        for i, (path, dur) in enumerate(zip(slides, durations)):
            add_clip(ken_burns_clip(path, dur), dur, is_slide=True)
            if remaining and (i + 1) % insert_every == 0 and len(clips) < len(slides) + len(pexels_paths):
                add_clip(real_clip(remaining.pop(0), args.clip_seconds), args.clip_seconds, is_slide=False)

    padding = -FADE if len(clips) > 1 else 0
    video = concatenate_videoclips(clips, method="compose", padding=padding)

    if sentences and not args.no_captions:
        if args.pure_footage:
            # Bei pure-footage kommen die sentences aus echten Whisper-
            # Zeitstempeln der tatsaechlichen Aufnahme (siehe scripts/
            # simple_voice_reel_captions.py) -- die Original-start/duration-
            # Werte sind bereits exakt audiogenau. slide_starts/durations
            # sind dagegen die VISUELLE, durch Crossfade-Ueberlappungen
            # (cursor -= FADE bei jedem Clip-Wechsel) komprimierte Zeitachse
            # der Video-Segmente -- captions daran auszurichten liess sie mit
            # jeder Ueberblendung frueher rutschen und driftete ueber die
            # Laufzeit zunehmend vom echten Ton weg (live beobachtet
            # 2026-09-06, ca. 1,5s Vorlauf nach 6 Uebergaengen). Deshalb hier
            # bewusst die unveraenderten Original-Zeitstempel verwenden.
            caption_sentences = sentences
        else:
            caption_sentences = [
                {**s, "start": slide_starts[i], "duration": durations[i]}
                for i, s in enumerate(sentences)
            ]
        subs = caption_clips(caption_sentences, video.size, position="center" if args.pure_footage else "top")
        if subs:
            video = CompositeVideoClip([video] + subs, size=video.size).with_duration(video.duration)

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
