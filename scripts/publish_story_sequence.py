"""Postet ALLE Datenkarten-Slides eines Posts als Sequenz von Instagram-Stories
(nacheinander im Story-Reel des Accounts) -- nicht nur eine Ankuendigung, sondern
die echte Analyse selbst, fuer Firmen die laut Mag7-Regel keinen vollen Carousel-
Post bekommen.

Aufruf:
  python scripts/publish_story_sequence.py marktupdate_target-q2-2026 --live
"""

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

GRAPH_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


def get_config():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    base_url = os.environ.get("PUBLIC_BASE_URL")
    missing = [n for n, v in [("INSTAGRAM_ACCESS_TOKEN", token), ("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id), ("PUBLIC_BASE_URL", base_url)] if not v]
    if missing:
        sys.exit(f"Fehlt in .env: {', '.join(missing)}")
    return token, ig_id, base_url.rstrip("/")


def stage_all_slides(post_name: str) -> list[str]:
    src_dir = ROOT / "output" / post_name / "tiktok_9x16"
    slides = sorted(src_dir.glob("slide_*.png"))
    if not slides:
        sys.exit(f"Keine Slides gefunden in {src_dir}")
    dst_dir = ROOT / "docs" / "assets" / "posts_9x16" / post_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    relpaths = []
    for slide in slides:
        dst = dst_dir / slide.name
        shutil.copy2(slide, dst)
        relpaths.append(f"assets/posts_9x16/{post_name}/{slide.name}")
    return relpaths


def create_story_container(token: str, ig_id: str, image_url: str) -> str:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "image_url": image_url, "media_type": "STORIES", "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Story-Container ({image_url}): {resp.status_code} {resp.text}")
    return resp.json()["id"]


def publish_container(token: str, ig_id: str, creation_id: str) -> dict:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
        "creation_id": creation_id, "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Veroeffentlichen: {resp.status_code} {resp.text}")
    return resp.json()


def log_result(entry: dict):
    log_path = ROOT / "data" / "published_log.json"
    log_path.parent.mkdir(exist_ok=True)
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    log.append(entry)
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("post_name")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    token, ig_id, base_url = get_config()
    relpaths = stage_all_slides(args.post_name)
    print(f"{len(relpaths)} Slides gestaged fuer '{args.post_name}'. Bitte committen+pushen, dann mit --live erneut aufrufen.")

    if not args.live:
        return

    media_ids = []
    for i, relpath in enumerate(relpaths, 1):
        image_url = f"{base_url}/{relpath}"
        print(f"  Slide {i}/{len(relpaths)}: {image_url}")
        container_id = create_story_container(token, ig_id, image_url)
        result = publish_container(token, ig_id, container_id)
        media_ids.append(result.get("id"))
        print(f"    Veroeffentlicht: {result}")
        if i < len(relpaths):
            time.sleep(2)

    log_result({
        "post_name": args.post_name, "type": "story_sequence",
        "timestamp": datetime.now().isoformat(),
        "media_ids": media_ids, "live": True, "published": True,
    })
    print(f"\nAlle {len(media_ids)} Stories veroeffentlicht. Protokolliert in data/published_log.json")


if __name__ == "__main__":
    main()
