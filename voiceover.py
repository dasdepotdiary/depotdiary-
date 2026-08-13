"""Voiceover-Skript-Generator (siehe CLAUDE.md: ein gesprochener Satz pro Slide,
Gesamtlaenge 35-45 Sekunden, Hook zuerst).

Schreibt output/<post_name>/script.md (zum Lesen/Einsprechen) und
output/<post_name>/timing.json (Zeit pro Slide, fuer video/assemble.py).
"""

import json
from pathlib import Path

WORDS_PER_MINUTE = 150  # durchschnittliches natuerliches Sprechtempo


def estimate_seconds(sentence: str) -> float:
    words = len(sentence.split())
    return max(1.5, round(words / WORDS_PER_MINUTE * 60, 2))


def build(sentences: list[str]) -> dict:
    durations = [estimate_seconds(s) for s in sentences]
    starts = []
    t = 0.0
    for d in durations:
        starts.append(round(t, 2))
        t += d
    return {
        "sentences": [
            {"index": i + 1, "text": s, "start": starts[i], "duration": durations[i]}
            for i, s in enumerate(sentences)
        ],
        "total_seconds": round(t, 1),
    }


def write(post_name: str, sentences: list[str], output_root: Path = None) -> dict:
    output_root = output_root or (Path(__file__).parent / "output")
    data = build(sentences)
    out_dir = output_root / post_name
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"# Voiceover-Skript -- {post_name}", "", f"Gesamt: ca. {data['total_seconds']}s", ""]
    for s in data["sentences"]:
        lines.append(f"**Slide {s['index']}** ({s['duration']}s): {s['text']}")
        lines.append("")
    (out_dir / "script.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "timing.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    in_range = 35 <= data["total_seconds"] <= 45
    if not in_range:
        print(f"Hinweis: Skript ist {data['total_seconds']}s lang (Ziel: 35-45s).")
    return data
