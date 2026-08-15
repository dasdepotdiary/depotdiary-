"""Erzeugt die 'Neuer Post'-Story-Ankuendigung fuer einen Post.

Aufruf:
  python scripts/make_story_announcement.py erklaerstueck_kgv "Was ein KGV eigentlich aussagt." ERKLAERSTUECK
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import render_story_announcement

ROOT = Path(__file__).parent.parent


def main():
    if len(sys.argv) < 3:
        sys.exit("Aufruf: python scripts/make_story_announcement.py <post_name> <titel> [kategorie]")
    post_name = sys.argv[1]
    title = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else ""

    img = render_story_announcement(title, category)
    out_dir = ROOT / "output" / post_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "story_announcement.png"
    img.save(out_path)
    print("Story-Ankuendigung:", out_path)


if __name__ == "__main__":
    main()
