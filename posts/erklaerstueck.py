"""Generischer Erklaerstueck-Post (CLAUDE.md Format 'Erklaerstueck', 2x/Woche).

Input: posts/inputs/erklaerstueck_<slug>.json (siehe erklaerstueck_beispiel.json)

Aufruf:
  python posts/erklaerstueck.py beispiel
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import voiceover
import site_sync

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

    date_str = data.get("date", date.today().isoformat())
    cover = site_sync.stage_cover(post.name)
    site_sync.add_post(
        post_id=post.name,
        title=data["hook"].replace("*", ""),
        category="erklaerstueck",
        date_str=date_str,
        excerpt=data.get("hook_sub", ""),
        cover_relpath=cover,
    )
    body_paragraphs = ([data["hook_sub"]] if data.get("hook_sub") else []) + [
        s["body"] for s in data["sections"]
    ]
    site_sync.add_wissen(
        entry_id=slug,
        title=data["hook"].replace("*", ""),
        date_str=date_str,
        body_paragraphs=body_paragraphs,
    )
    print("Website-Eintrag aktualisiert (docs/content/posts.json + wissen.json)")


if __name__ == "__main__":
    main()
