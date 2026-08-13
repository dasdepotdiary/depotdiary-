"""Story-Highlight-Serie (PROMPTS.md Prompt 5). Format nativ 1080x1920.

Input: posts/inputs/highlight_<slug>.json (siehe highlight_etf-basics.json)

Aufruf:
  python posts/highlight.py etf-basics
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import HighlightDeck

INPUTS_DIR = Path(__file__).parent / "inputs"


def load_input(slug: str) -> dict:
    path = INPUTS_DIR / f"highlight_{slug}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/highlight.py <slug>  (Datei: posts/inputs/highlight_<slug>.json)")
    slug = sys.argv[1]
    data = load_input(slug)

    deck = HighlightDeck(f"highlight_{slug}", total_slides=len(data["eintraege"]))
    deck.slide_title(data["titel_wort"], data.get("untertitel", ""))

    eyebrow = data["thema"].upper()
    for eintrag in data["eintraege"]:
        deck.slide_text(eyebrow, eintrag["headline"], eintrag["body"])

    out_dir = deck.export()
    print("Highlight-Serie:", out_dir)


if __name__ == "__main__":
    main()
