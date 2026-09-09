"""Neues Carousel-Format "Mythos vs. Realitaet" (2026-09-09).

Nutzer-Anliegen beim Anfordern: der Account "verliert die Design-Farbe" --
zu viele neue Formate (Guess the Stock, Aktienquiz, Wochenbewegung) haben
jeweils eigene, neue Paletten bekommen. Dieses Format ist deshalb bewusst
ANDERS aufgebaut: es nutzt render.py/Post (dieselbe Engine wie Erklaerstueck/
Deep-Dive/ETF-Steckbrief) und ausschliesslich die bestehenden Brand-Farben
aus brand.py (RED fuer "Mythos", GREEN fuer "Realitaet" -- dieselbe Rot/Gruen-
Sprache wie bei Kursveraenderungen ueberall sonst im Account). Neue Struktur
(Kontrast-Karten statt Fliesstext), aber keine neue Farbpalette.

Input: posts/inputs/mythos_realitaet_<slug>.json

Aufruf:
  python posts/mythos_realitaet.py <slug>
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
    path = INPUTS_DIR / f"mythos_realitaet_{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/mythos_realitaet.py <slug>  (Datei: posts/inputs/mythos_realitaet_<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    total = 2 + len(data["items"])
    post_name = f"mythos_realitaet_{slug}"
    post = Post(post_name, total_slides=total)

    eyebrow = data.get("eyebrow", "MYTHOS VS. REALITÄT")
    post.slide_hook(eyebrow, data["hook"], data.get("hook_sub", ""))

    hook_sentence = data["hook"].replace("*", "")
    if data.get("hook_sub"):
        hook_sentence += ". " + data["hook_sub"]
    sentences = [hook_sentence]
    for item in data["items"]:
        post.slide_contrast(
            eyebrow, item["headline"],
            item.get("wrong_label", "Mythos"), item["wrong_text"],
            item.get("right_label", "Realität"), item["right_text"],
        )
        sentences.append(item["headline"].replace("*", "") + ". Mythos: " + item["wrong_text"] + " Realität: " + item["right_text"])

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
        f"Mythos: {i['wrong_text']} Realität: {i['right_text']}" for i in data["items"]
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
