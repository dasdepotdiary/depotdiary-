"""Generischer Erklaerstueck-Post (CLAUDE.md Format 'Erklaerstueck', 2x/Woche).

Input: posts/inputs/erklaerstueck_<slug>.json (siehe erklaerstueck_beispiel.json)

Aufruf:
  python posts/erklaerstueck.py beispiel
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import voiceover

INPUTS_DIR = Path(__file__).parent / "inputs"


def load_input(slug: str) -> dict:
    path = INPUTS_DIR / f"erklaerstueck_{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/erklaerstueck.py <slug>  (Datei: posts/inputs/erklaerstueck_<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    total = 2 + len(data["sections"])
    post_name = f"erklaerstueck_{slug}"
    post = Post(post_name, total_slides=total)

    eyebrow = data.get("eyebrow", "ERKLÄRSTÜCK")
    post.slide_hook(eyebrow, data["hook"], data.get("hook_sub", ""))

    sentences = [data["hook"].replace("*", "")]
    for section in data["sections"]:
        post.slide_text(eyebrow, section["headline"], section["body"])
        sentences.append(section["headline"].replace("*", ""))

    post.slide_cta(eyebrow, data["cta_headline"], data.get("cta_body", ""))
    sentences.append(data["cta_headline"].replace("*", "") + ". " + data.get("cta_body", ""))

    ig_dir, tt_dir = post.export()
    print("Instagram 4:5:", ig_dir)
    print("TikTok 9:16:", tt_dir)
    print("Kontaktabzug:", ig_dir.parent / "uebersicht.png")

    voiceover.write(post.name, sentences)
    print("Voiceover-Skript:", (Path(__file__).parent.parent / "output" / post.name / "script.md"))


if __name__ == "__main__":
    main()
