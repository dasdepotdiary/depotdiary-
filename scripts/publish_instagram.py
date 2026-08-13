"""Instagram-Publishing-Pipeline ueber die Meta Graph API (PROMPTS.md Prompt 7).

Voraussetzungen (selbst einrichten):
  - Instagram-Business-Konto, verknuepft mit einer Facebook-Seite
  - Meta-Developer-App mit instagram_content_publish Berechtigung
  - Langlebiger Access Token

.env im Projektordner (niemals committen, ist gitignored):
  INSTAGRAM_ACCESS_TOKEN=...
  INSTAGRAM_BUSINESS_ACCOUNT_ID=...
  PUBLIC_BASE_URL=https://<username>.github.io/depotdiary

Ablauf:
  1. python scripts/stage_for_publish.py <post_name>   (Bilder public machen)
  2. python scripts/publish_instagram.py <post_name> --caption "..."          (Trockenlauf)
  3. python scripts/publish_instagram.py <post_name> --caption "..." --live   (wirklich veroeffentlichen)

Trockenlauf bereitet alles vor (Container werden bei Meta angelegt, das ist
folgenlos) und laesst nur den letzten Schritt (media_publish) aus.
"""

import argparse
import json
import os
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
    missing = [
        n for n, v in [
            ("INSTAGRAM_ACCESS_TOKEN", token),
            ("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id),
            ("PUBLIC_BASE_URL", base_url),
        ] if not v
    ]
    if missing:
        sys.exit(f"Fehlt in .env: {', '.join(missing)} (siehe .env.example)")
    return token, ig_id, base_url.rstrip("/")


def create_item_container(token: str, ig_id: str, image_url: str) -> str:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Container fuer {image_url}: {resp.status_code} {resp.text}")
    return resp.json()["id"]


def create_carousel_container(token: str, ig_id: str, children_ids: list[str], caption: str) -> str:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Carousel-Container: {resp.status_code} {resp.text}")
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
    parser.add_argument("--caption", required=True)
    parser.add_argument("--live", action="store_true",
                         help="Ohne dieses Flag: Trockenlauf, es wird NICHT veroeffentlicht")
    args = parser.parse_args()

    token, ig_id, base_url = get_config()

    post_dir = ROOT / "output" / args.post_name / "instagram_4x5"
    slides = sorted(post_dir.glob("slide_*.png"))
    if not slides:
        sys.exit(f"Keine Slides gefunden in {post_dir}")

    print(f"{'LIVE' if args.live else 'TROCKENLAUF'} -- {len(slides)} Slides fuer '{args.post_name}'\n")

    children_ids = []
    for slide in slides:
        image_url = f"{base_url}/assets/posts/{args.post_name}/{slide.name}"
        print(f"  Container fuer {image_url} ...")
        cid = create_item_container(token, ig_id, image_url)
        children_ids.append(cid)
        time.sleep(1)  # kleiner Puffer gegen Rate-Limits

    print("\n  Carousel-Container erzeugen ...")
    carousel_id = create_carousel_container(token, ig_id, children_ids, args.caption)

    result = {
        "post_name": args.post_name,
        "timestamp": datetime.now().isoformat(),
        "carousel_container_id": carousel_id,
        "children_ids": children_ids,
        "live": args.live,
        "published": False,
    }

    if args.live:
        print("  Veroeffentliche ...")
        publish_result = publish_container(token, ig_id, carousel_id)
        result["published"] = True
        result["media_id"] = publish_result.get("id")
        print(f"  Veroeffentlicht: {publish_result}")
    else:
        print(f"\n  Trockenlauf abgeschlossen. Carousel-Container bereit: {carousel_id}")
        print("  Fuehre mit --live aus, um wirklich zu veroeffentlichen:")
        print(f"    python scripts/publish_instagram.py {args.post_name} --caption \"...\" --live")

    log_result(result)
    print("\nProtokolliert in data/published_log.json")


if __name__ == "__main__":
    main()
