"""Marktupdate-Post im Datenkarten-Format (slide_stats), fuer Themen wie
Speicherchip-Preise, Sektorverteilung, Fed-Zinsentscheidung -- rein faktisch,
keine Kursziele, keine Kauf-/Verkaufsempfehlung.

Input: posts/inputs/marktupdate_<slug>.json

Aufruf:
  python posts/marktupdate.py speicherchips
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import brand as B
import voiceover
import site_sync

INPUTS_DIR = Path(__file__).parent / "inputs"

COLOR_MAP = {
    "ink": B.INK, "green": B.GREEN, "green_mid": B.GREEN_MID,
    "ochre": B.OCHRE, "grey": B.GREY, "red": B.RED, "subtext": B.SUBTEXT,
}


def load_input(slug: str) -> dict:
    path = INPUTS_DIR / f"marktupdate_{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def stats_tuples(stats):
    return [(s[0], s[1], s[2], COLOR_MAP.get(s[3], B.INK)) for s in stats]


def stats_sentence(headline, stats):
    parts = [f"{s[0]} {s[1]}: {s[2]}" for s in stats]
    return headline.replace("*", "") + " " + "; ".join(parts) + "."


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/marktupdate.py <slug>  (Datei: posts/inputs/marktupdate_<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    total = 2 + len(data["sections"])
    post_name = f"marktupdate_{slug}"
    post = Post(post_name, total_slides=total)

    eyebrow = data.get("eyebrow", "MARKTUPDATE")
    post.slide_hook(eyebrow, data["hook"], data.get("hook_sub", ""))

    hook_sentence = data["hook"].replace("*", "")
    if data.get("hook_sub"):
        hook_sentence += ". " + data["hook_sub"]
    sentences = [hook_sentence]

    for section in data["sections"]:
        if section["type"] == "stats":
            post.slide_stats(eyebrow, section["headline"], stats_tuples(section["stats"]), section.get("note", ""))
            sentences.append(stats_sentence(section["headline"], section["stats"]))
        else:
            post.slide_text(eyebrow, section["headline"], section["body"])
            sentences.append(section["headline"].replace("*", "") + " " + section["body"])

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
        category="marktupdate",
        date_str=date_str,
        excerpt=data.get("hook_sub", ""),
        cover_relpath=cover,
    )
    print("Website-Eintrag aktualisiert (docs/content/posts.json)")


if __name__ == "__main__":
    main()
