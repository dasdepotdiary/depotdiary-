"""News-Reel im "Rendite-Radar"-Stil: Foto-Hintergrund (Ken Burns, Wechsel pro Satz), Wort-fuer-Wort-
Untertitel mit gelber Hervorhebung, KI-Stimme (ElevenLabs). Nur Fakten, keine Empfehlung.

Aufruf: python posts/reel_news_style.py <name> <config.json>
  config: {"text": "...", "photos": ["assets/news_photos/..."], "date_label": "17.10.2026"}
"""
import json, os, shutil, subprocess, sys
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image, ImageEnhance

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import style_finanzhafen as S
load_dotenv(ROOT / ".env")
FF = shutil.which("ffmpeg")
VOICE = "EXAVITQu4vr4xnSDxMaL"


def tts(text, out):
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35}}, timeout=180)
    r.raise_for_status(); out.write_bytes(r.content)


def words(audio):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", compute_type="int8")
    seg, _ = m.transcribe(str(audio), language="de", word_timestamps=True)
    return [(w.start, w.end, w.word.strip()) for s in seg for w in s.words]


def align(ws, tw):
    """Ordnet Skriptwoertern Zeiten zu (difflib-Anker + lineare Interpolation dazwischen)."""
    import difflib, re
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower().replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss"))
    a = [norm(w) for w in tw]; b = [norm(w[2]) for w in ws]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(tw)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): times[blk.a + k] = ws[blk.b + k][0]
    # Interpolation
    t0, t1 = ws[0][0], ws[-1][1]
    idx = [i for i, t in enumerate(times) if t is not None]
    if not idx: idx = []
    prev_i, prev_t = -1, t0
    for i in idx + [len(tw)]:
        nxt_t = times[i] if i < len(tw) else t1
        gap = i - prev_i - 1
        for g in range(gap): times[prev_i + 1 + g] = prev_t + (nxt_t - prev_t) * (g + 1) / (gap + 1) if prev_i >= 0 or True else prev_t
        prev_i, prev_t = i, nxt_t
    return [(t, t, w) for t, w in zip(times, tw)]


def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(ws, text_words, path):
    # Anzeige-Text aus dem Skript (richtige Schreibweise), Zeiten aus Whisper (gleiche Wortanzahl noetig)
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
           "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
           "Style: Cap,Arial,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,60,60,520,1\n\n"
           "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    n = min(len(ws), len(text_words)); ev = []
    i = 0
    while i < n:
        j = min(i + 3, n); chunk = [w.upper() for w in text_words[i:j]]
        for k in range(i, j):
            st = ws[k][0]; en = ws[k + 1][0] if k + 1 < n else ws[k][1] + 0.4
            if k == j - 1 and j < n: en = ws[j][0]
            txt = " ".join((f"{{\c&H00F0FF&}}{w}{{\c&HFFFFFF&}}" if idx + i == k else w) for idx, w in enumerate(chunk))
            ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{txt}")
        i = j
    path.write_text(hdr + "\n".join(ev) + "\n", encoding="utf-8")


def cover(path, dim=0.6):
    im = Image.open(path).convert("RGB"); w, h = im.size; r = 1080 / 1920
    if w / h > r:
        nw = int(h * r); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / r); y0 = int((h - nh) * 0.3); im = im.crop((0, y0, w, y0 + nh))
    im = ImageEnhance.Brightness(im.resize((1080, 1920), Image.LANCZOS)).enhance(dim).convert("RGBA")
    S.draw_wordmark(im)
    return im.convert("RGB")


def main(name, cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    out = ROOT / "output" / "reels_neu" / name; out.mkdir(parents=True, exist_ok=True)
    audio = out / "voice.mp3"
    if not audio.exists(): tts(cfg["text"], audio)
    ws = words(audio)
    tw = cfg["text"].replace("S und P", "S&P").split()
    print("Woerter Skript/Whisper:", len(tw), len(ws))
    ws_al = align(ws, tw)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(audio)]).decode().strip())
    total = dur + 0.6
    photos = cfg["photos"]; n = len(photos); seg = total / n
    clips = []
    for i, ph in enumerate(photos):
        png = out / f"p{i}.png"; cover(ROOT / ph).save(png)
        v = out / f"c{i}.mp4"; d = seg + (0.4 if i < n - 1 else 0)
        subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-vf",
            f"scale=1296:2304,zoompan=z='1+0.0007*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(d*30)}:s=1080x1920:fps=30",
            "-t", f"{d:.2f}", "-pix_fmt", "yuv420p", "-c:v", "libx264", str(v)], check=True)
        clips.append(v)
    ins, fc, last = [], "", "[0:v]"
    for v in clips: ins += ["-i", str(v)]
    for i in range(1, n):
        fc += f"{last}[{i}:v]xfade=transition=fade:duration=0.4:offset={seg*i:.2f}[v{i}];"; last = f"[v{i}]"
    base = out / "base.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", *ins, "-filter_complex", fc.rstrip(";"), "-map", last, "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", str(base)], check=True)
    build_ass(ws_al, tw, out / "subs.ass")
    final = out.parent / f"{name}.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", "base.mp4", "-i", "voice.mp3", "-vf", "subtitles=subs.ass",
        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final.resolve())], check=True, cwd=out)
    print(final, f"{dur:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
