"""Synct einzelne Posts in die Website-Content-JSONs (docs/content/).

Damit jeder neue Post automatisch im Archiv (und ggf. bei Wissen) auftaucht,
ohne dass man die Website separat pflegen muss.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
POSTS_JSON = ROOT / "docs" / "content" / "posts.json"
WISSEN_JSON = ROOT / "docs" / "content" / "wissen.json"


def stage_story(post_name: str) -> str:
    """Kopiert die Story-Ankuendigung (falls vorhanden, sonst Slide 1 im 9:16-Format)
    nach docs/assets/posts_9x16/<name>/ und gibt den relativen Pfad zurueck."""
    dst_dir = ROOT / "docs" / "assets" / "posts_9x16" / post_name
    dst_dir.mkdir(parents=True, exist_ok=True)

    announcement = ROOT / "output" / post_name / "story_announcement.png"
    if announcement.exists():
        dst = dst_dir / "story_announcement.png"
        shutil.copy2(announcement, dst)
        return f"assets/posts_9x16/{post_name}/story_announcement.png"

    fallback = ROOT / "output" / post_name / "tiktok_9x16" / "slide_1.png"
    dst = dst_dir / "slide_1.png"
    shutil.copy2(fallback, dst)
    return f"assets/posts_9x16/{post_name}/slide_1.png"


def stage_cover(post_name: str) -> str:
    """Kopiert die Instagram-4:5-Slides nach docs/assets/posts/<name>/ (fuer
    Website-Vorschau und Insta-API-Hosting) und gibt den relativen Cover-Pfad
    fuer Slide 1 zurueck."""
    src = ROOT / "output" / post_name / "instagram_4x5"
    dst = ROOT / "docs" / "assets" / "posts" / post_name
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("slide_*.png")):
        shutil.copy2(f, dst / f.name)
    return f"assets/posts/{post_name}/slide_1.png"


def _load(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_post(post_id, title, category, date_str, excerpt, cover_relpath):
    """cover_relpath z.B. 'assets/posts/<post_id>/slide_1.png' (siehe stage_for_publish.py)."""
    posts = _load(POSTS_JSON)
    posts = [p for p in posts if p["id"] != post_id]
    posts.append({
        "id": post_id,
        "title": title,
        "category": category,
        "date": date_str,
        "excerpt": excerpt,
        "cover": cover_relpath,
        "url": None,
    })
    _save(POSTS_JSON, posts)


def add_wissen(entry_id, title, date_str, body_paragraphs):
    entries = _load(WISSEN_JSON)
    entries = [e for e in entries if e["id"] != entry_id]
    entries.append({
        "id": entry_id,
        "title": title,
        "date": date_str,
        "body": body_paragraphs,
    })
    _save(WISSEN_JSON, entries)
