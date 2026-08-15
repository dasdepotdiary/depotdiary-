"""Postet eine einzelne Story (Ankuendigung 'Neuer Post') ueber die Meta Graph API.

Nutzt dieselbe .env wie publish_instagram.py. Stories sind IMMER ein einzelnes
Bild (kein Carousel) -- hier wird slide_1 im 9:16-Format aus tiktok_9x16/ genutzt.

Aufruf:
  python scripts/publish_instagram_story.py erklaerstueck_kgv          (Trockenlauf)
  python scripts/publish_instagram_story.py erklaerstueck_kgv --live   (wirklich veroeffentlichen)
"""

import argparse
import json
import os
import sys
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


def create_story_container(token: str, ig_id: str, image_url: str) -> str:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Story-Container: {resp.status_code} {resp.text}")
    return resp.json()["id"]


def publish_container(token: str, ig_id: str, creation_id: str) -> dict:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
        "creation_id": creation_id,
        "access_token": token,
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

    slide = ROOT / "output" / args.post_name / "tiktok_9x16" / "slide_1.png"
    if not slide.exists():
        sys.exit(f"Nicht gefunden: {slide}")

    image_url = f"{base_url}/assets/posts_9x16/{args.post_name}/slide_1.png"
    print(f"{'LIVE' if args.live else 'TROCKENLAUF'} -- Story fuer '{args.post_name}'")
    print(f"  Bild-URL: {image_url}")

    container_id = create_story_container(token, ig_id, image_url)
    print(f"  Container erzeugt: {container_id}")

    result = {
        "post_name": args.post_name, "type": "story",
        "timestamp": datetime.now().isoformat(),
        "container_id": container_id, "live": args.live, "published": False,
    }

    if args.live:
        publish_result = publish_container(token, ig_id, container_id)
        result["published"] = True
        result["media_id"] = publish_result.get("id")
        print(f"  Veroeffentlicht: {publish_result}")
    else:
        print("  Trockenlauf abgeschlossen -- mit --live wirklich posten.")

    log_result(result)


if __name__ == "__main__":
    main()
