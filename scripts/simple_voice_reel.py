"""Minimal-Aufwand-Reel: eine einzelne Titel-Folie (9:16) + eine echte
Sprachaufnahme, keine Slides, kein Pexels-Footage. Fuer die persoenlichen
Videos, wo die eigene Stimme/der eigene Standpunkt im Vordergrund steht.

Aufruf:
  python scripts/simple_voice_reel.py <post_name> "<Titel>" <audio_datei> <output_mp4>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
import brand as B


def build_title_slide(title: str) -> Image.Image:
    W, H = B.STORY_SIZE
    img = Image.new("RGB", (W, H), B.BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, B.BAR_WIDTH, H], fill=B.INK)

    eyebrow_font = ImageFont.truetype(B.SANS_BOLD, B.EYEBROW_SIZE)
    draw.text((B.MARGIN_LEFT, 90), "PERSÖNLICH", font=eyebrow_font, fill=B.SUBTEXT)

    max_w = W - B.MARGIN_LEFT - B.MARGIN_RIGHT
    size = 68
    font = ImageFont.truetype(B.SERIF_BOLD, size)
    words = title.split()
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    line_h = int(size * 1.25)
    block_h = len(lines) * line_h
    y = (H - block_h) // 2
    for line in lines:
        draw.text((B.MARGIN_LEFT, y), line, font=font, fill=B.INK)
        y += line_h

    draw.text((B.MARGIN_LEFT, H - 90), "@DASDEPOTDIARY",
               font=ImageFont.truetype(B.SANS_BOLD, 20), fill=B.GREEN)
    draw.text((B.MARGIN_LEFT, H - 60), "Keine Anlageberatung. Nur meine eigene Meinung.",
               font=ImageFont.truetype(B.SERIF_REGULAR, 18), fill=B.SUBTEXT)
    return img


def main():
    post_name, title, audio_path, out_path = sys.argv[1:5]
    out_dir = Path(__file__).parent.parent / "output" / post_name
    out_dir.mkdir(parents=True, exist_ok=True)
    slide_path = out_dir / "title_slide.png"
    build_title_slide(title).save(slide_path)

    import imageio_ffmpeg
    import subprocess
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(slide_path),
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        sys.exit(1)
    print(f"Fertig: {out_path}")


if __name__ == "__main__":
    main()
