"""Aufruf: python scripts/fast_pexels_reel.py <name>  (braucht output/<name>/{timing.json,voiceover_elevenlabs.mp3,clips/clip1..N.mp4}; REEL_GRADE=red fuer roten Alarm-Look). Schneller Pexels-Reel-Bau per ffmpeg (statt moviepy): Clips pro Satz zuschneiden,
konkatenieren, Wort-fuer-Wort-Untertitel (ASS) + Voiceover einbrennen."""
import json, os, subprocess, sys, shutil
from pathlib import Path

ROOT = Path(r"C:\Users\rasch\depotdiary")
sys.path.insert(0, str(ROOT / "posts"))
import reel_news_style as R

name = sys.argv[1]
out = ROOT / "output" / name
timing = json.load(open(out / "timing.json", encoding="utf-8"))
audio = out / "voiceover_elevenlabs.mp3"
FF = shutil.which("ffmpeg")
work = out / "fast"
work.mkdir(exist_ok=True)

dur_audio = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(audio)]).decode().strip())
clips = sorted((out / "clips").glob("clip*.mp4"))
sents = timing["sentences"]

segs = []
for i, s in enumerate(sents):
    d = s["duration"] if i + 1 < len(sents) else dur_audio - s["start"]
    clip = clips[i % len(clips)]
    off = 0 if i < len(clips) else 4
    seg = work / f"seg{i}.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-stream_loop", "-1", "-ss", str(off), "-i", str(clip),
        "-t", f"{d:.2f}", "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,eq=brightness=-0.10" + (",colorbalance=rs=0.22:gs=-0.08:bs=-0.12" if os.environ.get("REEL_GRADE") == "red" else "") + "",
        "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(seg)], check=True)
    segs.append(seg)

lst = work / "list.txt"
lst.write_text("".join(f"file '{p.name}'\n" for p in segs), encoding="utf-8")
base = work / "base.mp4"
subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "base.mp4"],
               check=True, cwd=work)

text = " ".join(s["text"] for s in sents).replace("S und P", "S&P")
tw = text.split()
ws = R.words(audio)
ws_al = R.align(ws, tw)
R.build_ass(ws_al, tw, work / "subs.ass")

final = out / "reel_fast.mp4"
subprocess.run([FF, "-y", "-loglevel", "error", "-i", "base.mp4", "-i", str(audio.resolve()), "-vf", "subtitles=subs.ass",
    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-shortest", str(final.resolve())], check=True, cwd=work)
print(final, round(dur_audio, 1), "s")
