"""Kopiert die Instagram-4:5-Slides eines Posts nach site/assets/posts/<name>/,
damit sie beim naechsten 'git push' ueber GitHub Pages oeffentlich erreichbar sind
-- Voraussetzung fuer die Graph API (Bilder muessen unter einer public URL liegen).

Aufruf:
  python scripts/stage_for_publish.py depot_update_2026-08
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python scripts/stage_for_publish.py <post_name>")
    name = sys.argv[1]

    src = ROOT / "output" / name / "instagram_4x5"
    if not src.exists():
        sys.exit(f"Nicht gefunden: {src}")

    dst = ROOT / "site" / "assets" / "posts" / name
    dst.mkdir(parents=True, exist_ok=True)

    for f in sorted(src.glob("slide_*.png")):
        shutil.copy2(f, dst / f.name)

    print(f"{len(list(dst.glob('slide_*.png')))} Slides bereitgestellt in {dst}")
    print("Noch committen + pushen, damit sie ueber GitHub Pages live sind.")


if __name__ == "__main__":
    main()
