"""Rendert vorproduzierte Fachbegriff-Stories aus posts/inputs/fachbegriff_bank.json
neu (z.B. nach Design-Aenderungen) in docs/assets/posts_9x16/fachbegriff_<datum>/.

Aufruf:
  python posts/build_fachbegriff_bank.py            # alle Eintraege ab heute
  python posts/build_fachbegriff_bank.py 2026-10-06 # nur dieses Datum
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import story_fachbegriff as sf

ROOT = Path(__file__).parent.parent
BANK = json.loads((ROOT / "posts" / "inputs" / "fachbegriff_bank.json").read_text(encoding="utf-8"))


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    today = date.today().isoformat()
    for iso, entry in sorted(BANK.items()):
        if only and iso != only:
            continue
        if not only and iso < today:
            continue
        y, m, d = iso.split("-")
        sf.DATE_LABEL = f"{d}.{m}.{y}"
        img = sf.slide_fachbegriff(entry)
        out = ROOT / "docs" / "assets" / "posts_9x16" / f"fachbegriff_{iso}"
        out.mkdir(parents=True, exist_ok=True)
        img.save(out / "slide_1.png")
        print("gebaut:", iso, entry["term"])


if __name__ == "__main__":
    main()
