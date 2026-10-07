"""Taegliches Reel "Everything you need to know" -- Bildspur im depotdiary-Foto-Schema,
zum Drueberlegen deiner eigenen Voiceover-Aufnahme. Daten kommen aus
posts/inputs/marktbrief_<datum>.json. Nur Fakten, keine Empfehlung (BaFin/MAR).

Aufruf: python posts/reel_marktbrief.py posts/inputs/marktbrief_2026-10-07.json
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import style_finanzhafen as S

ROOT = Path(__file__).parent.parent
GREEN, RED = "#5ED38A", "#FF6B6B"


def base(key, label, date):
    img = S.story_background(S.photo_for(key), 0.2, 0.5)
    d = ImageDraw.Draw(img)
    S.draw_top(d, S.accent_for(key), label, date)
    return img, S.accent_for(key)


def finish(img):
    S.draw_wordmark(img)
    return img


def center(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((S.SW - w) / 2, y), text, font=f, fill=fill)


def slide_hook(c):
    img, acc = base("hook" + c["date_label"], "MARKT-BRIEF", c["date_label"])
    d = ImageDraw.Draw(img)
    y = 760
    for i, line in enumerate(c["hook"]):
        center(d, y, line, S.font(150 if i == 0 else 110), S.CREAM if i == 0 else acc); y += 170 if i == 0 else 130
    center(d, y + 40, c["hook_sub"], S.font(44), S.SOFT)
    return finish(img)


def slide_rows(c, key, label, rows, fmt_right, note=None):
    img, acc = base(key + c["date_label"], label, c["date_label"])
    y0 = 560; h = 190
    boxes = [(70, y0 + i * (h + 24), S.SW - 70, y0 + i * (h + 24) + h) for i in range(len(rows))]
    img = S.glass(img, boxes)
    d = ImageDraw.Draw(img)
    for (x0, y, x1, y2), r in zip(boxes, rows):
        d.text((x0 + 40, y + 52), r[0], font=S.font(60), fill=S.CREAM)
        txt, col = fmt_right(r)
        w = d.textlength(txt, font=S.font(64))
        d.text((x1 - 40 - w, y + 48), txt, font=S.font(64), fill=col)
    if note:
        yy = boxes[-1][3] + 50
        for ln in S.wrap_text(d, note, S.font(44), S.SW - 160):
            d.text((80, yy), ln, font=S.font(44), fill=S.SOFT); yy += 58
    return finish(img)


def pct(r):
    v = r[-1]
    return f"{v:+.1f}%".replace(".", ","), (GREEN if v >= 0 else RED)


def slide_outro(c):
    img, acc = base("outro" + c["date_label"], "MARKT-BRIEF", c["date_label"])
    d = ImageDraw.Draw(img)
    y = 800
    for i, line in enumerate(c["outro"]):
        center(d, y, line, S.font(100 if i == 0 else 64), S.CREAM if i == 0 else acc); y += 130 if i == 0 else 84
    center(d, y + 40, "Keine Anlageberatung.", S.font(36), S.MUTED)
    return finish(img)


def main(cfg):
    c = json.load(open(cfg, encoding="utf-8"))
    name = "marktbrief_" + c["date_label"].split(".")[2] + "-" + c["date_label"].split(".")[1] + "-" + c["date_label"].split(".")[0]
    out = ROOT / "output" / "reels_neu" / name; out.mkdir(parents=True, exist_ok=True)
    slides = [(slide_hook(c), 4)]
    slides.append((slide_rows(c, "idx", "GESTERN AN DER BOERSE", c["indices"], lambda r: (f"{r[1]}   " + pct((0, r[2]))[0], pct((0, r[2]))[1])), 14))
    slides.append((slide_rows(c, "mov", "DIE GROESSTEN GEWINNER", c["movers"], pct, c.get("movers_note")), 12))
    slides.append((slide_rows(c, "heute", "WAS HEUTE ANSTEHT", c["today"], lambda r: (r[1], S.CREAM)), 14))
    if c.get("trade"):
        slides.append((slide_rows(c, "trade", "SO HABE ICH GEHANDELT", c["trade"], lambda r: (r[1], S.CREAM)), 12))
    slides.append((slide_outro(c), 5))
    ff = shutil.which("ffmpeg"); clips = []; total = 0
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
