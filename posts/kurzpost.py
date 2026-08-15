"""Generischer Kurzpost fuer Wochennotiz / Fehler (CLAUDE.md Formate).

Persoenliche Erzaehlformate -- landen im Archiv, aber NICHT bei Wissen
(das ist fuer Erklaerstuecke reserviert).

Input: posts/inputs/<kategorie>_<slug>.json
  {
    "kategorie": "wochennotiz" | "fehler",
    "eyebrow": "WOCHENNOTIZ" | "FEHLER",
    "hook": "...",
    "hook_sub": "...",
    "sections": [{"headline":..., "body":...}, ...],
    "cta_headline": "...",
    "cta_body": "..."
  }

Aufruf:
  python posts/kurzpost.py wochennotiz_2026-08-15
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
    path = INPUTS_DIR / f"{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/kurzpost.py <slug>  (Datei: posts/inputs/<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    total = 2 + len(data["sections"])
    post = Post(slug, total_slides=total)

    eyebrow = data["eyebrow"]
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

    cover = site_sync.stage_cover(post.name)
    site_sync.add_post(
        post_id=post.name,
        title=data["hook"].replace("*", ""),
        category=data["kategorie"],
        date_str=data.get("date", date.today().isoformat()),
        excerpt=data.get("hook_sub", ""),
        cover_relpath=cover,
    )
    print("Website-Eintrag aktualisiert (docs/content/posts.json)")


if __name__ == "__main__":
    main()
