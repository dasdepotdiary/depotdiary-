"""Erzeugt docs/feed.xml aus content/posts.json (RSS 2.0)."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent.parent
POSTS_JSON = ROOT / "docs" / "content" / "posts.json"
FEED_XML = ROOT / "docs" / "feed.xml"
BASE_URL = "https://dasdepotdiary.github.io/depotdiary-"

CATEGORY_LABELS = {
    "depot-update": "Depot-Update",
    "wochennotiz": "Wochennotiz",
    "erklaerstueck": "Erklärstück",
    "quartalszahlen": "Quartalszahlen",
    "fehler": "Fehler",
}


def rfc822(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y 00:00:00 +0000")


def main():
    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)

    items = []
    for p in posts:
        link = p.get("url") or f"{BASE_URL}/archiv/"
        title = p["title"].replace("*", "")
        excerpt = (p.get("excerpt") or "").replace("*", "")
        category = CATEGORY_LABELS.get(p["category"], p["category"])
        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="false">{escape(p['id'])}</guid>
      <pubDate>{rfc822(p['date'])}</pubDate>
      <category>{escape(category)}</category>
      <description>{escape(excerpt)}</description>
    </item>""")

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>depotdiary</title>
    <link>{BASE_URL}/</link>
    <description>Ein 19-jähriges Depot, offen dokumentiert. Keine Anlageberatung, nur mein eigener Weg.</description>
    <language>de-AT</language>
    <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    FEED_XML.write_text(xml, encoding="utf-8")
    print("RSS-Feed:", FEED_XML, f"({len(items)} Eintraege)")


if __name__ == "__main__":
    main()
