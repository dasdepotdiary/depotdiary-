"""Marktbrief-Reel V2: Datum gross auf jeder Folie, Hook mit 3 Schlagzahlen, Einzelaktien-Karten,
Zins-Folie. Zum Drueberlegen deiner Voiceover-Spur (Laenge passt zu skript_1min_*.md).

Aufruf: python posts/reel_marktbrief_v2.py posts/inputs/marktbrief_v2_2026-10-07.json
"""
import json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import style_finanzhafen as S
import reel_marktbrief as R

ROOT = Path(__file__).parent.parent


def frame(c, key, label):
    img = S.story_background(S.photo_for(key + c["date_label"]), 0.15, 0.6)
    acc = S.accent_for(key + c["date_label"])
    d = ImageDraw.Draw(img)
    # grosse Datums-Pille oben (im Safe-Bereich)
    txt = c["weekday"].upper() + "  " + c["date_label"]
    f = S.font(54); w = d.textlength(txt, font=f)
    d.rounded_rectangle([(S.SW - w) / 2 - 36, 285, (S.SW + w) / 2 + 36, 285 + 96], radius=48, fill=acc)
    d.text(((S.SW - w) / 2, 303), txt, font=f, fill="#0A0A0A")
    R.center(d, 420, label, S.font(40), S.SOFT)
    return img, acc


def s_big3(c, s):
    img, acc = frame(c, "big3", s["label"])
    boxes = [(70, 560 + i * 300, S.SW - 70, 560 + i * 300 + 270) for i in range(3)]
    img = S.glass(img, boxes); d = ImageDraw.Draw(img)
    for (x0, y, x1, y2), (big, small, col) in zip(boxes, s["items"]):
        d.text((x0 + 44, y + 36), big, font=S.font(110), fill=col)
        for k, ln in enumerate(S.wrap_text(d, small, S.font(44), x1 - x0 - 88)[:2]):
            d.text((x0 + 44, y + 170 + k * 52), ln, font=S.font(44), fill=S.SOFT)
    return R.finish(img)


def s_rows(c, s):
    img, acc = frame(c, s["key"], s["label"])
    rows = s["rows"]; h = 200
    boxes = [(70, 560 + i * (h + 22), S.SW - 70, 560 + i * (h + 22) + h) for i in range(len(rows))]
    img = S.glass(img, boxes); d = ImageDraw.Draw(img)
    for (x0, y, x1, y2), r in zip(boxes, rows):
        d.text((x0 + 40, y + 34), r[0], font=S.font(58), fill=S.CREAM)
        if len(r) > 2:
            for k, ln in enumerate(S.wrap_text(d, r[2], S.font(36), x1 - x0 - 330)[:2]):
                d.text((x0 + 40, y + 108 + k * 44), ln, font=S.font(36), fill=S.MUTED)
        col = R.GREEN if r[1].startswith("+") else R.RED if r[1].startswith("-") or r[1].startswith("−") else S.CREAM
        w = d.textlength(r[1], font=S.font(70))
        d.text((x1 - 40 - w, y + 56), r[1], font=S.font(70), fill=col)
    return R.finish(img)


def s_stat(c, s):
    img, acc = frame(c, "stat", s["label"])
    d = ImageDraw.Draw(img)
    R.center(d, 700, s["big"], S.font(230), acc)
    y = 960
    for ln in S.wrap_text(d, s["text"], S.font(52), S.SW - 180):
        R.center(d, y, ln, S.font(52), S.CREAM); y += 70
    if s.get("foot"):
        y += 30
        for ln in S.wrap_text(d, s["foot"], S.font(40), S.SW - 180):
            R.center(d, y, ln, S.font(40), S.SOFT); y += 54
    return R.finish(img)


def s_photo(c, s):
    img, acc = frame(c, s["key"], s["label"])
    d = ImageDraw.Draw(img)
    y = 900
    for ln in s["lines"]:
        R.center(d, y, ln, S.font(86), S.CREAM); y += 110
    return R.finish(img)


def s_outro(c, s):
    img, acc = frame(c, "outro", "")
    d = ImageDraw.Draw(img)
    y = 860
    for i, ln in enumerate(s["lines"]):
        R.center(d, y, ln, S.font(96 if i == 0 else 64), S.CREAM if i == 0 else acc); y += 120 if i == 0 else 84
    R.center(d, y + 40, "Keine Anlageberatung.", S.font(36), S.MUTED)
    return R.finish(img)


def main(cfg):
    c = json.load(open(cfg, encoding="utf-8"))
    d, m, y = c["date_label"].split(".")
    name = f"marktbrief_v2_{y}-{m}-{d}"
    out = ROOT / "output" / "reels_neu" / name; out.mkdir(parents=True, exist_ok=True)
    fn = {"big3": s_big3, "rows": s_rows, "stat": s_stat, "photo": s_photo, "outro": s_outro}
    slides = [(fn[s["type"]](c, s), s["dur"]) for s in c["slides"]]
    ff = shutil.which("ffmpeg"); clips = []
    for i, (im, dur) in enumerate(slides):
        p = out / f"s{i}.png"; im.save(p); v = out / f"c{i}.mp4"
        subprocess.run([ff, "-y", "-loglevel", "error", "-loop", "1", "-i", str(p), "-vf",
                        f"scale=1296:2304,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur*30}:s=1080x1920:fps=30",
                        "-t", str(dur), "-pix_fmt", "yuv420p", "-c:v", "libx264", str(v)], check=True)
        clips.append((v, dur))
    ins, fc, last, t = [], "", "[0:v]", clips[0][1]
    for v, _ in clips: ins += ["-i", str(v)]
    for i in range(1, len(clips)):
        fc += f"{last}[{i}:v]xfade=transition=fade:duration=0.4:offset={t-0.4:.1f}[v{i}];"; last = f"[v{i}]"; t += clips[i][1] - 0.4
    mp4 = out.parent / f"{name}.mp4"
    subprocess.run([ff, "-y", "-loglevel", "error", *ins, "-filter_complex", fc.rstrip(";"), "-map", last, "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", str(mp4)], check=True)
    print(mp4, f"{t:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1])
