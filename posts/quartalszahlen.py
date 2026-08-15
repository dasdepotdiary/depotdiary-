"""Quartalszahlen-Post (PROMPTS.md Prompt 4).

Referiert ausschliesslich veroeffentlichte Zahlen -- keine Einordnung, kein
Kursziel, kein Satz darueber was die Aktie jetzt macht. Der einzige
persoenliche Teil: "Ich halte die Aktie seit <Zeitraum>, und das waren die
Zahlen."

Input: posts/inputs/quartalszahlen_<slug>.json (siehe quartalszahlen_beispiel.json)

Aufruf:
  python posts/quartalszahlen.py beispiel
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import brand as B
import voiceover
import site_sync

INPUTS_DIR = Path(__file__).parent / "inputs"


def load_input(slug: str) -> dict:
    path = INPUTS_DIR / f"quartalszahlen_{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/quartalszahlen.py <slug>  (Datei: posts/inputs/quartalszahlen_<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    post_name = f"quartalszahlen_{slug}"
    post = Post(post_name, total_slides=6)

    post.slide_hook(
        "QUARTALSZAHLEN",
        f"{data['unternehmen']} -- die *Zahlen* zu {data['quartal']}.",
        f"Veröffentlicht am {data['berichtsdatum']}.",
    )

    rows = [(k["label"], k["wert"], B.INK) for k in data["kennzahlen"]]
    post.slide_rows(
        "QUARTALSZAHLEN",
        "Was *veröffentlicht* wurde.",
        rows,
        f"Quelle: {data['quelle']}.",
    )

    post.slide_text(
        "QUARTALSZAHLEN",
        "Der *Ausblick* im Wortlaut.",
        data["ausblick_wortlaut"],
    )

    post.slide_text(
        "QUARTALSZAHLEN",
        "Woher die *Zahlen* kommen.",
        f"{data['quelle']}, veröffentlicht am {data['berichtsdatum']}. Keine Einordnung von mir, nur Referenz.",
    )

    post.slide_text(
        "QUARTALSZAHLEN",
        f"Ich halte die Aktie seit *{data['gehalten_seit']}*.",
        "Und das waren die Zahlen.",
    )

    post.slide_cta(
        "QUARTALSZAHLEN",
        "Nächstes *Quartal* wieder.",
        "Ich ordne hier nichts ein, ich referiere nur, was veröffentlicht wurde.",
    )

    ig_dir, tt_dir = post.export()
    print("Instagram 4:5:", ig_dir)
    print("TikTok 9:16:", tt_dir)
    print("Kontaktabzug:", ig_dir.parent / "uebersicht.png")

    sentences = [
        f"{data['unternehmen']} hat die Zahlen zu {data['quartal']} veroeffentlicht -- hier sind sie, ohne Bewertung.",
        f"{data['kennzahlen'][0]['label']}: {data['kennzahlen'][0]['wert']}. "
        f"{data['kennzahlen'][1]['label']}: {data['kennzahlen'][1]['wert']}.",
        f"Nettomarge und Wachstum zum Vorjahresquartal findest du auch in der Slide-Tabelle.",
        "Den Ausblick des Unternehmens zeig ich dir im Wortlaut, ohne meine eigene Einschaetzung.",
        f"Ich halte die Aktie seit {data['gehalten_seit']}, und das waren einfach die Zahlen dazu.",
        "Naechstes Quartal wieder -- ich referiere nur, ich ordne nichts fuer dich ein.",
    ]
    voiceover.write(post.name, sentences)
    print("Voiceover-Skript:", (Path(__file__).parent.parent / "output" / post.name / "script.md"))

    cover = site_sync.stage_cover(post.name)
    site_sync.add_post(
        post_id=post.name,
        title=f"{data['unternehmen']} -- {data['quartal']}",
        category="quartalszahlen",
        date_str=data["berichtsdatum"],
        excerpt=f"Veröffentlichte Zahlen zu {data['quartal']}, Quelle: {data['quelle']}.",
        cover_relpath=cover,
    )
    print("Website-Eintrag aktualisiert (docs/content/posts.json)")


if __name__ == "__main__":
    main()
